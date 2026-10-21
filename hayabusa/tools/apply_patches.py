#!/usr/bin/env python3
"""Transform a stock 2 MB Gen 3 Hayabusa read into a boosted RACE bin.

Four independent patches, applied in a fixed (canonical) order so their one shared
region resolves the same way no matter what order you ask for them:

  sd        - SPEED-DENSITY fuelling + ignition on a 3-bar MAP sensor. Rescales the IAP
              sensor, repoints the fuel lookups from manifold VACUUM to ABSOLUTE pressure,
              DISREGARDS the throttle (alpha-N/TPS) fuel path (blend curve + WOT gate off so
              the MAP table holds authority everywhere), re-axises all 8 SD fuel maps to the
              3-bar scale, and adds the boost spark-retard maps. This is the full SD-v3 change
              set (23,730 bytes) lifted byte-for-byte out of the shipped race/old/SD-v3.bin.
              Pick the MAP sensor with --sensor (default gm3bar).
  antilag   - rolling anti-lag: START + WOT while rolling captures RPM and holds it with a
              spark cut. Code 0xBE000, cal 0xBF000, retard map 0x188214, three hooks. Bytes
              come from race/Busa-SD-v4.1.bin. Ships DISABLED (enable in the XDF).
  autoshift - auto-upshift (air-shifter): at a per-gear RPM target, pulse the PAIR output to
              kick an air-ram shifter (no spark cut; the factory quickshifter does that).
              Code 0xBE148, cal 0xBF010, one hook. Ships DISABLED. *** The PAIR output
              bit/polarity is UNVERIFIED: confirm it on the bench first. ***
  boost     - boost control: software-PWM a race-unused output (repurposed O2-heater driver)
              to a wastegate/boost-control solenoid, scheduled by gear/RPM, with optional
              closed-loop trim from a pressure sensor on a repurposed O2 signal input. Code
              0xBE280, cal 0xBF030, one hook. Ships DISABLED. *** Output AND input primitives
              are UNVERIFIED: bench them first. *** Only available once race/als/boost.bin has
              been assembled (race/als/build.sh on a v850e3v5 toolchain); if it is missing this
              patch is skipped with a note.

Every byte region a patch touches is identical across all eight stock 5JCZ reads, so the
patches are read-agnostic. The field-1 CRC is re-stamped automatically after patching.

Everything is UNVERIFIED ON HARDWARE. Bench an ECM first and keep a stock read for recovery.

usage:
  python3 tools/apply_patches.py in_stock.bin race.bin                    # full race bin: sd+antilag+autoshift(+boost)
  python3 tools/apply_patches.py in_stock.bin out.bin sd                  # one or more of: sd antilag autoshift boost
  python3 tools/apply_patches.py in_stock.bin out.bin sd --sensor gm25bar # speed density on a GM 2.5-bar sensor
  python3 tools/apply_patches.py in_stock.bin out.bin --check             # report state, write nothing
"""
import binascii
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK_REF = os.path.join(ROOT, 'stock/5JCZSJ40/5JCZSJ40.bin')   # expected stock "base" bytes
SD41_REF = os.path.join(ROOT, 'race/Busa-SD-v4.1.bin')          # supplies the anti-lag patch bytes
SD3_REF = os.path.join(ROOT, 'race/old/SD-v3.bin')              # supplies the speed-density patch bytes
AS_BLOB = os.path.join(ROOT, 'race/als/autoshift.bin')          # assembled auto-upshift code
BOOST_BLOB = os.path.join(ROOT, 'race/als/boost.bin')           # assembled boost-control code (optional)

ORDER = ['sd', 'antilag', 'autoshift', 'boost']   # canonical apply order (resolves the 0x188214 overlap)
SIZE = 0x200000
CRC_END = 0x1FFAFC        # field-1 CRC covers 0x10000..0x1FFAFC, stored big-endian at 0x1FFAFE

# IAP (manifold-pressure) sensor presets. The SD patch rescales the stock sensor so a wide-range
# MAP sensor fits the ECU's internal pressure scale; only the 16-bit GAIN/OFFSET pair differs per
# sensor (the divisor and DTC threshold the SD patch sets are sensor-independent).
#   counts = 7862 + (OFFSET-0x8000) + raw*GAIN*32/10925        (fitted to the stock scale)
#   for a sensor transfer kPa = a*raw + b (raw = 0..1023 ADC):
#       GAIN   = round(393.14 * a * 10925 / 32)
#       OFFSET = round(32768 + 393.14 * b)
# Both are PROVISIONAL starting points: true them with one key-on reading (raw*a+b == baro).
SENSORS = {
    # name:    (GAIN,   OFFSET,  a (kPa/count), b (kPa), human label)
    'gm3bar':  (0xA12F, 0x6CA6, 0.307429, -12.6, 'GM 3-bar (~62.9 kPa/V, span ~20-300 kPa) [SD-v3 default]'),
    'gm25bar': (0x8689, 0x6FE0, 0.256598, -10.5, 'GM 2.5-bar (~52.5 kPa/V, span ~20-250 kPa)'),
}
GAIN_ADDR, OFFSET_ADDR = 0x18EF58, 0x18EF5A

# auto-upshift calibration defaults at 0xBF010 (little-endian); see autoshift.s for the field layout.
AS_CAL = bytes([
    0x00,        # +0  enable            0x80 = on   (ships OFF)
    0x00,        # +1  bench test output 0x80 = hold output on
    0x14, 0x00,  # +2  pulse ticks       0x0014
    0xAA, 0x2A,  # +4  min grip (WOT)    ~30 deg (X/364.08)
    0x00, 0x05,  # +6  re-arm rpm drop   ~500 rpm (X/2.56)
    0x00, 0x5F,  # +8  1->2 target       9500 rpm
    0x00, 0x5F,  # +10 2->3
    0x00, 0x5F,  # +12 3->4
    0x00, 0x5F,  # +14 4->5
    0x00, 0x5F,  # +16 5->6
])
AS_HOOK = bytes.fromhex('86ffaa04')   # 0x5DC9E: jarl 0x5DB5E -> jarl AUTOSHIFT_TICK (0xBE148)

# boost-control calibration defaults at 0xBF030 (see boost.s for the field layout). Ships DISABLED.
BOOST_CAL = bytes([
    0x00,        # +0  enable             0x80 = on   (ships OFF)
    0x00,        # +1  bench test output  0x80 = hold solenoid output on
    0x00,        # +2  closed-loop enable 0x80 = trim duty toward target from the pressure input
    0x00,        # +3  pad
    0x14, 0x00,  # +4  pwm period ticks   0x0014 (~100 ms at a 5 ms tick -> ~10 Hz software PWM)
    0x00, 0x14,  # +6  min rpm to run     ~2000 rpm (X/2.56) below this the solenoid stays off (no boost)
    0x00, 0x00,  # +8  duty 1st gear      0..period ticks on (0 = wastegate spring pressure)
    0x00, 0x00,  # +10 duty 2nd
    0x00, 0x00,  # +12 duty 3rd
    0x00, 0x00,  # +14 duty 4th
    0x00, 0x00,  # +16 duty 5th
    0x00, 0x00,  # +18 duty 6th
    0x00, 0x00,  # +20 target kPa abs (closed loop) raw-ADC counts on the pressure input
    0x02, 0x00,  # +22 trim step          duty ticks per period when closed-loop correcting
])
BOOST_HOOK = bytes.fromhex('00000000')   # filled from boost.bin's hook word if the blob is present
BOOST_CODE_ADDR = 0xBE280
BOOST_CAL_ADDR = 0xBF030
BOOST_HOOK_ADDR = 0x5DCA2   # FUN_5dc9a: 'jarl 0x5dc64' -> 'jarl BOOST_TICK'; exact word comes from build.sh


def crc_stamp(b):
    b[0x1FFAFE:0x1FFB00] = binascii.crc_hqx(bytes(b[0x10000:CRC_END]), 0xFFFF).to_bytes(2, 'big')


def diff_runs(a, c, gap=8):
    """Contiguous (addr, length) runs where bytes a[] and c[] differ, merging gaps <= `gap`."""
    d = [i for i in range(len(a)) if a[i] != c[i]]
    runs = []
    if d:
        s = p = d[0]
        for i in d[1:]:
            if i - p <= gap:
                p = i
            else:
                runs.append((s, p - s + 1)); s = p = i
        runs.append((s, p - s + 1))
    return runs


def entries(stock, sd41, sd3, want):
    """name -> list of (address, [acceptable_base_bytes...], patch_bytes, [already_ok_bytes...]).

    A region is applied when the current bytes match ANY listed base; it is left untouched when
    they equal the patch or any "already_ok" state. The only region two patches share is the
    neutral boost-spark / anti-lag retard map at 0x188214: the SD patch writes the boost map
    there and anti-lag later overwrites part of it with the retard map. So for SD and anti-lag
    the final combined bytes (exactly what SD-v4.1 holds) are listed as "already_ok", which lets
    --check report a finished race bin cleanly instead of tripping over the overlap.
    """
    ent = {}

    # --- speed density: every SD-v3-vs-stock region except the field-1 CRC word
    sd = []
    for a, n in diff_runs(stock, sd3):
        if a == 0x1FFAFE:
            continue
        sd.append((a, [stock[a:a + n]], sd3[a:a + n], [sd41[a:a + n]]))
    ent['sd'] = sd

    # --- rolling anti-lag: every SD-v4.1-vs-SD-v3 region except the CRC word (bytes from SD-v4.1)
    antilag = []
    for a, n in diff_runs(sd3, sd41):
        if a == 0x1FFAFE:
            continue
        bases = [stock[a:a + n]]
        if sd3[a:a + n] != stock[a:a + n]:     # SD also touched this region -> accept its bytes as a base too
            bases.append(sd3[a:a + n])
        antilag.append((a, bases, sd41[a:a + n], []))
    ent['antilag'] = antilag

    # --- auto-upshift (air-shifter)
    code = open(AS_BLOB, 'rb').read()
    ent['autoshift'] = [
        (0xBE148, [stock[0xBE148:0xBE148 + len(code)]], code, []),
        (0x5DC9E, [stock[0x5DC9E:0x5DC9E + 4]], AS_HOOK, []),
        (0xBF010, [stock[0xBF010:0xBF010 + len(AS_CAL)]], AS_CAL, []),
    ]

    # --- boost control (only if the code blob has been assembled)
    if os.path.exists(BOOST_BLOB):
        bcode = open(BOOST_BLOB, 'rb').read()
        hook = BOOST_HOOK
        hpath = BOOST_BLOB[:-4] + '.hook'
        if os.path.exists(hpath):
            hook = bytes.fromhex(open(hpath).read().strip())
        ent['boost'] = [
            (BOOST_CODE_ADDR, [stock[BOOST_CODE_ADDR:BOOST_CODE_ADDR + len(bcode)]], bcode, []),
            (BOOST_HOOK_ADDR, [stock[BOOST_HOOK_ADDR:BOOST_HOOK_ADDR + 4]], hook, []),
            (BOOST_CAL_ADDR, [stock[BOOST_CAL_ADDR:BOOST_CAL_ADDR + len(BOOST_CAL)]], BOOST_CAL, []),
        ]
    elif 'boost' in want:
        print('  boost     SKIPPED - race/als/boost.bin not assembled yet (run race/als/build.sh on a '
              'v850e3v5 toolchain). Everything else was still applied.')

    return ent


def apply(b, name, ent, check):
    done = skipped = 0
    for a, bases, patch, ok in ent:
        cur = bytes(b[a:a + len(patch)])
        if cur == patch or cur in ok:
            skipped += 1
        elif cur in bases:
            if not check:
                b[a:a + len(patch)] = patch
            done += 1
        else:
            sys.exit('%s: base bytes at 0x%06X do not match a stock read (or an earlier patch) - '
                     'unsupported bin, aborting (no changes written)' % (name, a))
    print('  %-9s %d region(s) %s, %d already present' % (name, done, 'to apply' if check else 'applied', skipped))
    return done


def set_sensor(b, name, check):
    gain, off, a, bb, label = SENSORS[name]
    if check:
        cur_g = struct.unpack('<H', b[GAIN_ADDR:GAIN_ADDR + 2])[0]
        cur_o = struct.unpack('<H', b[OFFSET_ADDR:OFFSET_ADDR + 2])[0]
        print('  sensor    current GAIN 0x%04X OFFSET 0x%04X; %s wants GAIN 0x%04X OFFSET 0x%04X'
              % (cur_g, cur_o, name, gain, off))
        return
    b[GAIN_ADDR:GAIN_ADDR + 2] = struct.pack('<H', gain)
    b[OFFSET_ADDR:OFFSET_ADDR + 2] = struct.pack('<H', off)
    print('  sensor    %s -> GAIN 0x%04X OFFSET 0x%04X  (kPa = %.6f*raw %+0.2f)  %s'
          % (name, gain, off, a, bb, label))


def main():
    args = sys.argv[1:]
    check = '--check' in args
    args = [x for x in args if x != '--check']
    sensor = 'gm3bar'
    if '--sensor' in args:
        i = args.index('--sensor')
        try:
            sensor = args[i + 1]
        except IndexError:
            sys.exit('--sensor needs a value (%s)' % '/'.join(SENSORS))
        if sensor not in SENSORS:
            sys.exit('unknown sensor %r (use %s)' % (sensor, '/'.join(SENSORS)))
        del args[i:i + 2]
    if len(args) < 2:
        sys.exit(__doc__)
    inf, outf = args[0], args[1]
    want = args[2:] or ['sd', 'antilag', 'autoshift', 'boost']
    for w in want:
        if w not in ORDER:
            sys.exit('unknown patch %r (use any of: %s)' % (w, ' '.join(ORDER)))

    b = bytearray(open(inf, 'rb').read())
    if len(b) != SIZE:
        sys.exit('expected a 2 MB read, got %d bytes' % len(b))
    ent = entries(open(STOCK_REF, 'rb').read(), open(SD41_REF, 'rb').read(), open(SD3_REF, 'rb').read(), want)

    print(('checking ' if check else 'patching ') + inf)
    changed = 0
    for w in ORDER:                 # always apply in canonical order
        if w in want and w in ent:
            changed += apply(b, w, ent[w], check)
    if 'sd' in want:                # pick the MAP sensor scaling (default already in the SD bytes)
        set_sensor(b, sensor, check)

    if check:
        return
    crc_stamp(b)
    open(outf, 'wb').write(b)
    print('wrote %s (%d code/data regions changed, field-1 CRC re-stamped)' % (outf, changed))
    print('Remember: UNVERIFIED on hardware. Boosted SD needs injector scaling and a sensor calibration '
          'before it runs; anti-lag / auto-shift / boost all ship DISABLED - enable and tune in the XDF. '
          'Confirm the auto-shift and boost outputs on the bench first.')


if __name__ == '__main__':
    main()
