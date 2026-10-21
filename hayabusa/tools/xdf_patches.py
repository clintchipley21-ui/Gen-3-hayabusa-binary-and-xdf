#!/usr/bin/env python3
"""Add the patch tuning items to a finalized XDF (folder "22 Patches & Air-Shifter").

Called at the end of make_stock_xdfs.py and make_race_xdf.py, after xdf_userfriendly.finalize().
It appends, without disturbing any existing category index:

  - one folder "22 Patches & Air-Shifter";
  - editable auto-shift settings (enable, bench-test output, pulse, WOT gate, re-arm, 5 per-gear RPM targets)
    at 0xBF010;
  - the rolling anti-lag settings at 0xBF000, but only for XDFs that do not already define them (the eight
    stock reads; the race XDF already has them).

The patches themselves are applied with tools/apply_patches.py (which also re-stamps the field-1 CRC), NOT
from inside the XDF: native TunerPro patch elements (XDFPATCH/XDFPATCHENTRY) crashed TunerPro on open, so
they are deliberately not embedded. The PATCH/PENTRY templates below are kept for reference only, in case the
exact format is confirmed later; check() asserts no XDFPATCH is ever written.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply_patches as ap  # noqa: E402

FOLDER = '22 Patches & Air-Shifter (apply to a stock bin)'
FOLDER_BOOST = '23 Boost Control (apply to a stock bin)'   # boost gets its own folder so it is easy to find
UID_ITEM = 0xE000
UID_PATCH = 0xE100

# auto-shift settings at 0xBF010 (see race/als/autoshift.s). (kind, addr, bits, title, units, eq, dec, desc)
ITEMS = [
    ('flag', 0xBF010, 8, 'Auto-Shift :: Enable', '', '', 0,
     '0x80 = auto-upshift ON. At each per-gear RPM target it pulses the PAIR output to kick the air ram; '
     'no spark cut (the factory quickshifter handles that). Ships OFF. UNVERIFIED - bench first.'),
    ('flag', 0xBF011, 8, 'Auto-Shift :: Bench Test Output', '', '', 0,
     '0x80 = hold the PAIR output asserted (no shifting) so you can confirm on the bench which pin / relay '
     'it drives. Set back to 0 for normal use.'),
    ('const', 0xBF012, 16, 'Auto-Shift :: Pulse Length', 'ticks', 'X', 0,
     'How long the PAIR output is held per shift, in ~5 ms task ticks (20 ~= 100 ms). Tune to your air ram.'),
    ('const', 0xBF014, 16, 'Auto-Shift :: Min Grip (WOT gate)', 'deg', 'X/364.08', 1,
     'Only auto-shift at or above this twist-grip angle, so it fires under power, not when rolling off.'),
    ('const', 0xBF016, 16, 'Auto-Shift :: Re-arm RPM Drop', 'RPM', 'X/2.56', 0,
     'After a shift, engine RPM must fall this far below the gear target before the next gear can fire.'),
    ('const', 0xBF018, 16, 'Auto-Shift :: Target 1 to 2', 'RPM', 'X/2.56', 0, 'Upshift when RPM reaches this in 1st gear.'),
    ('const', 0xBF01A, 16, 'Auto-Shift :: Target 2 to 3', 'RPM', 'X/2.56', 0, 'Upshift when RPM reaches this in 2nd gear.'),
    ('const', 0xBF01C, 16, 'Auto-Shift :: Target 3 to 4', 'RPM', 'X/2.56', 0, 'Upshift when RPM reaches this in 3rd gear.'),
    ('const', 0xBF01E, 16, 'Auto-Shift :: Target 4 to 5', 'RPM', 'X/2.56', 0, 'Upshift when RPM reaches this in 4th gear.'),
    ('const', 0xBF020, 16, 'Auto-Shift :: Target 5 to 6', 'RPM', 'X/2.56', 0, 'Upshift when RPM reaches this in 5th gear.'),
]

# boost-control settings at 0xBF030 (see race/als/boost.s). Software-PWM a repurposed O2-heater output
# to a wastegate/boost-control solenoid, duty scheduled per gear, with an optional closed-loop trim from a
# pressure sensor on a repurposed O2 signal input. Added to every XDF (the addresses are free flash).
BOOST_ITEMS = [
    ('flag', 0xBF030, 8, 'Boost :: Enable', '', '', 0,
     '0x80 = boost control ON. Software-PWMs the repurposed O2-heater output to a wastegate / boost-control '
     'solenoid at the per-gear duty below. Ships OFF (and all duties 0 = wastegate spring pressure). '
     'UNVERIFIED - bench the output first with "Bench Test Output".'),
    ('flag', 0xBF031, 8, 'Boost :: Bench Test Output', '', '', 0,
     '0x80 = hold the solenoid output asserted (no PWM, no control) so you can confirm on the bench which pin '
     'drives it (candidate: O2-heater low-side driver). Output polarity is set by the wiring (relay coil leg / '
     'NO vs NC solenoid), not here. Set back to 0 for normal use.'),
    ('flag', 0xBF032, 8, 'Boost :: Closed-Loop Enable', '', '', 0,
     '0x80 = trim the duty toward "CL Target" using the wastegate-pressure sensor on the input channel set by '
     '"Pressure Input Address". Leave OFF until that input is proven on the bench; open-loop per-gear duty works without it.'),
    ('const', 0xBF034, 16, 'Boost :: PWM Period', 'ticks', 'X', 0,
     'Software-PWM period in ~5 ms task ticks (20 ~= 100 ms ~= 10 Hz). Duty is 0..Period. Match your '
     'boost-control solenoid (MAC valves like ~30 Hz; raise the tick rate only if the bench shows room).'),
    ('const', 0xBF036, 16, 'Boost :: Min RPM to Run', 'RPM', 'X/2.56', 0,
     'Below this RPM the solenoid is held off (wastegate spring pressure) so there is no boost off-idle. Default 2000.'),
    ('const', 0xBF038, 16, 'Boost :: Duty Gear 1', 'ticks', 'X', 0, 'Solenoid on-ticks per period in 1st gear (duty%% = ticks/Period). 0 = spring pressure (least boost).'),
    ('const', 0xBF03A, 16, 'Boost :: Duty Gear 2', 'ticks', 'X', 0, 'On-ticks per period in 2nd gear.'),
    ('const', 0xBF03C, 16, 'Boost :: Duty Gear 3', 'ticks', 'X', 0, 'On-ticks per period in 3rd gear.'),
    ('const', 0xBF03E, 16, 'Boost :: Duty Gear 4', 'ticks', 'X', 0, 'On-ticks per period in 4th gear.'),
    ('const', 0xBF040, 16, 'Boost :: Duty Gear 5', 'ticks', 'X', 0, 'On-ticks per period in 5th gear.'),
    ('const', 0xBF042, 16, 'Boost :: Duty Gear 6', 'ticks', 'X', 0, 'On-ticks per period in 6th gear.'),
    ('const', 0xBF044, 16, 'Boost :: CL Target', 'kPa', 'X*0.342-15', 0,
     'Closed-loop target manifold pressure. The cell stores RAW counts; this equation (X*0.342-15) is the '
     'wastegate-pressure SENSOR TRANSFER so you enter the target in kPa - PROVISIONAL, set it to match your '
     'sensor and input scaling (see "Pressure Input Address"). Only used when "Closed-Loop Enable" is on.'),
    ('const', 0xBF046, 16, 'Boost :: CL Trim Step', 'ticks', 'X', 0,
     'Duty ticks the closed loop adds/removes each period while correcting toward CL Target. Small = slow/stable. '
     'Trim is clamped to +/- Period.'),
    ('const', 0xBF048, 16, 'Boost :: Pressure Input Address', 'RAM lo', 'X', 0,
     'Which ADC word the wastegate-pressure sensor is read from, as the low 16 bits of a 0xFEF0xxxx RAM address '
     '(effective address = 0xFEF00000 + this). Default 0x2648 (a candidate repurposed-O2 input). Set it to the '
     'word the bench proves carries the sensor; add a TunerPro RAM gauge at 0xFEF0<this> with the same transfer '
     'as "CL Target" to watch live boost. Only used when "Closed-Loop Enable" is on.'),
]

# IAP MAP-sensor scaling. The SD patch sets these for a GM 3-bar sensor; the preset guide lets you retune for a
# GM 2.5-bar (or calibrate any sensor). The conversion divisor (0x74302) is defined in no stock XDF, so the guide
# is anchored there and shows in every XDF; gain/offset are added only where the SD consts are not already present.
SENSOR_PRESETS = (
    'IAP sensor presets (kPa = a*raw + b; GAIN = round(393.14*a*10925/32), OFFSET = round(32768+393.14*b)): '
    'GM 3-bar a=0.307429 b=-12.6 -> GAIN 0xA12F OFFSET 0x6CA6 (SD default); '
    'GM 2.5-bar a=0.256598 b=-10.5 -> GAIN 0x8689 OFFSET 0x6FE0. Both PROVISIONAL - true them with one key-on '
    'reading (raw*a+b should equal local baro) and set the XDF kPa equation on the SD fuel/boost maps to match.')
SENSOR_GUIDE = [
    ('const', 0x74302, 16, 'IAP Sensor :: Conversion Divisor', 'raw', 'X', 0,
     'SD sets this to 10925 (stock 21850) so a 3-bar-range MAP sensor fits the ECU internal pressure scale with a '
     '16-bit gain. Leave it; retune the sensor with Gain/Offset. ' + SENSOR_PRESETS),
]
SENSOR_GAINOFF = [
    ('const', 0x18EF58, 16, 'IAP Sensor :: Gain', 'raw', 'X', 0, 'IAP (manifold-pressure) sensor gain. ' + SENSOR_PRESETS),
    ('const', 0x18EF5A, 16, 'IAP Sensor :: Offset', 'raw', 'X', 0, 'IAP (manifold-pressure) sensor offset. ' + SENSOR_PRESETS),
]

# rolling anti-lag settings at 0xBF000 (same layout the race XDF defines). Added only to XDFs that do not
# already define them (i.e. the stock reads; the race XDF already has them in its race folders).
ALS_ITEMS = [
    ('const', 0xBF000, 8, 'ALS Enable', 'raw', 'X', 0,
     '0x80 = rolling anti-lag ON; anything else = OFF (START button behaves stock). Ships OFF on a patched bin.'),
    ('const', 0xBF001, 8, 'ALS Min Coolant Temp', 'deg C', 'X*0.9375-30', 0,
     'ALS will not arm below this coolant temperature (RAM 0xFEF026BD). Default 60 C.'),
    ('const', 0xBF002, 16, 'ALS Min Rolling Speed', 'km/h', 'X/128', 1,
     'ALS arms only while FRONT wheel speed (0xFEF0263A) is at or above this; below it START stays stock. Default 20.'),
    ('const', 0xBF004, 16, 'ALS Capture Grip Angle (WOT)', 'deg grip', 'X/364.08', 1,
     'With START held and rolling, when grip (0xFEF025EC, ~107 deg = full) reaches this the current RPM is captured. Default 90.'),
    ('const', 0xBF006, 16, 'ALS Release Grip Angle', 'deg grip', 'X/364.08', 1,
     'Grip below this while active releases ALS; re-opening past the capture angle re-captures. Keep below capture. Default 60.'),
    ('const', 0xBF008, 16, 'ALS Min Capture RPM', 'RPM', 'X/2.56', 0,
     'ALS will not engage if RPM at capture is below this. Default 3000. Must be greater than the hysteresis.'),
    ('const', 0xBF00A, 16, 'ALS Max Capture RPM', 'RPM', 'X/2.56', 0,
     'Captured RPM is clamped to this. Keep below the fuel-cut (11,200) and ignition-cut (12,000) limiters. Default 10500.'),
    ('const', 0xBF00C, 16, 'ALS Hold Hysteresis', 'RPM', 'X/2.56', 0,
     'Spark returns when RPM falls this far below the captured RPM. Smaller = tighter, harsher cut. Default 150.'),
    ('const', 0xBF00E, 16, 'ALS Max Active Time', 's', 'X*0.005', 1,
     'Safety timer: after this long continuously active, ALS drops out until START is released. Default 2000 counts = 10 s.'),
]

PATCH_DESC = {
    'antilag': ('Patch :: Install Rolling Anti-Lag',
                'Writes the rolling anti-lag code (0xBE000), its settings (0xBF000) and retard map, and three '
                'hooks, onto a stock bin. Ships DISABLED - enable with "ALS Enable". After applying in TunerPro, '
                're-stamp the field-1 CRC (tools/fix_field1_crc.py) or the ECU may reject the bin. UNVERIFIED.'),
    'autoshift': ('Patch :: Install Auto-Upshift (air-shifter)',
                  'Writes the auto-upshift code (0xBE148), its settings (0xBF010) and one hook, onto a stock bin. '
                  'Ships DISABLED - enable with "Auto-Shift :: Enable" after confirming the PAIR output on the '
                  'bench. Re-stamp the field-1 CRC after applying (tools/fix_field1_crc.py). UNVERIFIED.'),
}

CONST = ('  <XDFCONSTANT uniqueid="0x{uid:X}" flags="0x0">\n    <title>{title}</title>\n'
         '    <description>{desc}</description>\n    <CATEGORYMEM index="0" category="{cat}" />\n'
         '    <EMBEDDEDDATA mmedtypeflags="0x02" mmedaddress="0x{addr:X}" mmedelementsizebits="{bits}" '
         'mmedmajorstridebits="0" mmedminorstridebits="0" />\n    <units>{units}</units>\n'
         '    <decimalpl>{dec}</decimalpl>\n    <datatype>0</datatype>\n    <unittype>0</unittype>\n'
         '    <DALINK index="0" />\n    <MATH equation="{eq}">\n      <VAR id="X" />\n    </MATH>\n  </XDFCONSTANT>\n')
FLAG = ('  <XDFFLAG uniqueid="0x{uid:X}">\n    <title>{title}</title>\n    <description>{desc}</description>\n'
        '    <CATEGORYMEM index="0" category="{cat}" />\n    <EMBEDDEDDATA mmedaddress="0x{addr:X}" '
        'mmedelementsizebits="8" mmedmajorstridebits="0" mmedminorstridebits="0" />\n    <mask>0x80</mask>\n  </XDFFLAG>\n')
PATCH = ('  <XDFPATCH uniqueid="0x{uid:X}" flags="0x0">\n    <title>{title}</title>\n'
         '    <description>{desc}</description>\n    <CATEGORYMEM index="0" category="{cat}" />\n{entries}  </XDFPATCH>\n')
PENTRY = ('    <XDFPATCHENTRY name="{name}" address="0x{addr:X}" datasize="0x{n:X}" '
          'patchdata="{patch}" basedata="{base}" />\n')


def inject(text, which=('antilag', 'autoshift')):
    cats = re.findall(r'<CATEGORY index="(0x[0-9A-Fa-f]+)" name="[^"]*"', text)
    n = len(cats)                       # new folders get 0-based indices n, n+1 -> category = index+1
    cat_patch = n + 1                   # "22 Patches & Air-Shifter": air-shift + sensor (+ anti-lag on stock)
    cat_boost = n + 2                   # "23 Boost Control": the boost-control items, in their own folder
    uids = {int(u, 16) for u in re.findall(r'uniqueid="(0x[0-9A-Fa-f]+)"', text)}

    # (item, category) pairs. Boost lives in its own folder so it is unmissable in any editor.
    grouped = [(it, cat_patch) for it in ITEMS]
    grouped += [(it, cat_patch) for it in SENSOR_GUIDE]           # IAP sensor preset guide (every XDF)
    if 'mmedaddress="0x18EF58"' not in text:                      # XDFs without the SD sensor consts
        grouped += [(it, cat_patch) for it in SENSOR_GAINOFF]
    if 'mmedaddress="0xBF000"' not in text:                       # stock reads: expose anti-lag settings
        grouped += [(it, cat_patch) for it in ALS_ITEMS]
    grouped += [(it, cat_boost) for it in BOOST_ITEMS]            # boost-control settings -> own folder

    out = []
    uid = UID_ITEM
    for (kind, addr, bits, title, units, eq, dec, desc), cat in grouped:
        assert uid not in uids, uid
        d = escape(desc + ' @0x%X' % addr, quote=False)
        tmpl = FLAG if kind == 'flag' else CONST
        out.append(tmpl.format(uid=uid, title=escape(title, quote=False), desc=d, cat=cat,
                               addr=addr, bits=bits, units=escape(units, quote=False), eq=escape(eq, quote=False), dec=dec))
        uid += 1

    # NOTE: native TunerPro patches (XDFPATCH) are intentionally NOT embedded - that element crashed
    # TunerPro on open. Patches are applied with tools/apply_patches.py instead. The PATCH/PENTRY
    # templates and PATCH_DESC are kept for reference / possible future use once the format is confirmed.

    cat_xml = ('    <CATEGORY index="0x%X" name="%s" />\n    <CATEGORY index="0x%X" name="%s" />\n'
               % (n, escape(FOLDER), n + 1, escape(FOLDER_BOOST)))
    text = re.sub(r'(\n  </XDFHEADER>)', lambda m: '\n' + cat_xml.rstrip('\n') + m.group(1), text, count=1)
    text = text.replace('</XDFFORMAT>', ''.join(out) + '</XDFFORMAT>')
    return text


def check(text):
    root = ET.fromstring(text)                 # must be valid XML
    names = [c.get('name') for c in root.find('XDFHEADER').findall('CATEGORY')]
    assert FOLDER in names, 'patch folder missing'
    assert FOLDER_BOOST in names, 'boost folder missing'
    assert not root.findall('XDFPATCH'), 'XDFPATCH present - crashes TunerPro, must not be embedded'
    seen = [e.get('uniqueid') for e in root.iter() if e.tag in ('XDFCONSTANT', 'XDFFLAG', 'XDFTABLE')]
    assert len(seen) == len(set(seen)), 'duplicate uniqueid'
