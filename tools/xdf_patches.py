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
    n = len(cats)                       # new folder gets 0-based index n -> CATEGORYMEM category = n+1
    cat = n + 1
    uids = {int(u, 16) for u in re.findall(r'uniqueid="(0x[0-9A-Fa-f]+)"', text)}

    items = list(ITEMS)
    if 'mmedaddress="0xBF000"' not in text:   # stock reads: also expose the anti-lag settings
        items += ALS_ITEMS

    out = []
    uid = UID_ITEM
    for kind, addr, bits, title, units, eq, dec, desc in items:
        assert uid not in uids, uid
        d = escape(desc + ' @0x%X' % addr, quote=False)
        tmpl = FLAG if kind == 'flag' else CONST
        out.append(tmpl.format(uid=uid, title=escape(title, quote=False), desc=d, cat=cat,
                               addr=addr, bits=bits, units=escape(units, quote=False), eq=escape(eq, quote=False), dec=dec))
        uid += 1

    # NOTE: native TunerPro patches (XDFPATCH) are intentionally NOT embedded - that element crashed
    # TunerPro on open. Patches are applied with tools/apply_patches.py instead. The PATCH/PENTRY
    # templates and PATCH_DESC are kept for reference / possible future use once the format is confirmed.

    cat_xml = '    <CATEGORY index="0x%X" name="%s" />\n' % (n, escape(FOLDER))
    text = re.sub(r'(\n  </XDFHEADER>)', lambda m: '\n' + cat_xml.rstrip('\n') + m.group(1), text, count=1)
    text = text.replace('</XDFFORMAT>', ''.join(out) + '</XDFFORMAT>')
    return text


def check(text):
    root = ET.fromstring(text)                 # must be valid XML
    names = [c.get('name') for c in root.find('XDFHEADER').findall('CATEGORY')]
    assert FOLDER in names, 'patch folder missing'
    assert not root.findall('XDFPATCH'), 'XDFPATCH present - crashes TunerPro, must not be embedded'
    seen = [e.get('uniqueid') for e in root.iter() if e.tag in ('XDFCONSTANT', 'XDFFLAG', 'XDFTABLE')]
    assert len(seen) == len(set(seen)), 'duplicate uniqueid'
