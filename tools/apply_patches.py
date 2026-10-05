#!/usr/bin/env python3
"""Apply the rolling anti-lag and/or auto-upshift (air-shifter) code patches to a stock 2 MB read.

Both patches are read-agnostic: every byte region they touch is identical across all eight stock
5JCZ reads, so this works on any of them. The field-1 CRC is re-stamped automatically after patching.

  rolling anti-lag  - START + WOT while rolling captures RPM and holds it with a spark cut.
                      Code 0xBE000, cal 0xBF000, retard map 0x188214, three hooks. Bytes come from
                      the shipped race/Busa-SD-v4.1.bin (anti-lag ships DISABLED; enable in the XDF).
  auto-upshift      - at a per-gear RPM target, pulse the PAIR-valve output to kick an air-ram shifter
                      (no spark cut; the factory quickshifter does that). Code 0xBE148, cal 0xBF010,
                      one hook. Ships DISABLED. *** The PAIR output bit/polarity is UNVERIFIED: confirm
                      it on the bench with the XDF "Bench Test Output" switch before trusting it. ***

Everything is UNVERIFIED ON HARDWARE. Bench an ECM first and keep a stock read for recovery.

usage:
  python3 tools/apply_patches.py in_stock.bin out.bin                 # both patches
  python3 tools/apply_patches.py in_stock.bin out.bin antilag         # one of: antilag autoshift
  python3 tools/apply_patches.py in_stock.bin out.bin --check         # report state, write nothing
"""
import binascii
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK_REF = os.path.join(ROOT, 'stock/5JCZSJ40/5JCZSJ40.bin')   # supplies the expected stock "base" bytes
SD_REF = os.path.join(ROOT, 'race/Busa-SD-v4.1.bin')             # supplies the anti-lag patch bytes
AS_BLOB = os.path.join(ROOT, 'race/als/autoshift.bin')           # assembled auto-upshift code (race/als/build.sh)

# auto-upshift calibration defaults at 0xBF010 (little-endian); see autoshift.s for the field layout.
AS_CAL = bytes([
    0x00,       # +0  enable            0x80 = on   (ships OFF)
    0x00,       # +1  bench test output 0x80 = hold output on
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

SIZE = 0x200000
CRC_END = 0x1FFAFC        # field-1 CRC covers 0x10000..0x1FFAFC, stored big-endian at 0x1FFAFE


def crc_stamp(b):
    b[0x1FFAFE:0x1FFB00] = binascii.crc_hqx(bytes(b[0x10000:CRC_END]), 0xFFFF).to_bytes(2, 'big')


def entries(stock, sd):
    """(address, base_bytes, patch_bytes) for each patch. base = stock, patch = patched image."""
    antilag = []
    for a, n in ((0x2C700, 4), (0x525F2, 4), (0x5BE02, 4), (0xBE000, 328), (0xBF000, 16), (0x188214, 892)):
        antilag.append((a, stock[a:a + n], sd[a:a + n]))
    code = open(AS_BLOB, 'rb').read()
    autoshift = [
        (0xBE148, stock[0xBE148:0xBE148 + len(code)], code),
        (0x5DC9E, stock[0x5DC9E:0x5DC9E + 4], AS_HOOK),
        (0xBF010, stock[0xBF010:0xBF010 + len(AS_CAL)], AS_CAL),
    ]
    return {'antilag': antilag, 'autoshift': autoshift}


def apply(b, name, ent, check):
    done = skipped = 0
    for a, base, patch in ent:
        cur = bytes(b[a:a + len(patch)])
        if cur == patch:
            skipped += 1
        elif cur == base:
            if not check:
                b[a:a + len(patch)] = patch
            done += 1
        else:
            sys.exit('%s: base bytes at 0x%06X do not match a stock read - unsupported bin, aborting '
                     '(no changes written)' % (name, a))
    print('  %-9s %d region(s) %s, %d already present' % (name, done, 'to apply' if check else 'applied', skipped))
    return done


def main():
    args = sys.argv[1:]
    check = '--check' in args
    args = [a for a in args if a != '--check']
    if len(args) < 2:
        sys.exit(__doc__)
    inf, outf = args[0], args[1]
    which = args[2:] or ['antilag', 'autoshift']
    for w in which:
        if w not in ('antilag', 'autoshift'):
            sys.exit('unknown patch %r (use antilag and/or autoshift)' % w)
    b = bytearray(open(inf, 'rb').read())
    if len(b) != SIZE:
        sys.exit('expected a 2 MB read, got %d bytes' % len(b))
    ent = entries(open(STOCK_REF, 'rb').read(), open(SD_REF, 'rb').read())
    print(('checking ' if check else 'patching ') + inf)
    changed = sum(apply(b, w, ent[w], check) for w in which)
    if check:
        return
    crc_stamp(b)
    open(outf, 'wb').write(b)
    print('wrote %s (%d regions changed, field-1 CRC re-stamped)' % (outf, changed))
    print('Remember: UNVERIFIED on hardware. Both features ship DISABLED - enable and tune in the XDF. '
          'Confirm the auto-shift PAIR output on the bench first.')


if __name__ == '__main__':
    main()
