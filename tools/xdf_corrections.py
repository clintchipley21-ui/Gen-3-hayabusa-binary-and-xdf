#!/usr/bin/env python3
"""Apply the verified unit / label corrections (XDF v9.2) to a Gen 3 Hayabusa XDF, in place.

Why: many AUTO-DEFINED items took their unit from the RAM variable they were "compared with",
and that RAM list was built by guessing each variable from the tables that use it. Five of the
38 variables it relied on were wrong, and some items were tied to the wrong variable of a
multi-variable comparison. Every RAM variable below was re-checked against the code that writes
it, and every constant in CONST_FIXES against the code that compares it (decompiled 5JCZSJ40).

  fef02634  was "TP - Throttle position (copy)"      -> front wheel speed  (km/h = X/128)
  fef02636  was "TP - Throttle position (copy)"      -> rear wheel speed   (km/h = X/128)
  fef02604  was "TP - Throttle position, fuel path"  -> throttle opening RATE: TP now - TP 4
                                                        samples ago + 0x8000 (FUN_731A0)
  fef01562  was "Grip% 0-100 % (X/5)"                -> traction-control slip error (FUN_4DBD6)
  fef0264C  was "Engine speed (copy)"                -> RPM expected from wheel speed x gear ratio

Consequence worth knowing: 0x1824C6 ("WOT Throttle-Path Gate", shown as 91.4 deg) is compared
with fef02604, so it is a TIP-IN RATE gate: a TP rise of >= 1.41 deg within 4 samples forces 100%
TPS-map fuel for 4 cycles (0x18267A). It is not a 91.4 deg WOT threshold.

usage: python3 tools/xdf_corrections.py <file.xdf> <reference.bin> <sw label in STOCK lines>
       (the stock master uses 5JCZSJ10 and stock/5JCZSJ10/5JCZSJ10.bin)
Running it twice is harmless: every edit checks for the old text first.
"""
import re
import sys
import xml.etree.ElementTree as ET
from html import escape

# verified RAM variables: label, equation, units, decimals, short word for titles
V = {}
def _v(names, label, eq, units, dec, word):
    for n in names.split():
        V[n] = (label, eq, units, dec, word)
_v('fef0258e fef0258c fef02590 fef02592 fef02594 fef0259c fef0155c', 'Engine speed', 'X/2.56', 'RPM', 0, 'RPM')
_v('fef0264c', 'RPM expected from wheel speed x gear ratio', 'X/2.56', 'RPM', 0, 'RPM')
_v('fef025fe fef02600 fef02602', 'Throttle valve position', 'X/364.08', 'deg TP', 1, 'throttle')
_v('fef025d2', 'Throttle or grip angle (selected)', 'X/364.08', 'deg', 1, 'throttle')
_v('fef02634', 'Front wheel speed', 'X/128', 'km/h', 1, 'speed')
_v('fef02636', 'Rear wheel speed', 'X/128', 'km/h', 1, 'speed')
_v('fef02604', 'Throttle opening rate (TP now - TP 4 samples ago, 0x8000 = 0)', '(X-32768)/364.08', 'deg/4 samples', 2, 'throttle-rate')
_v('fef01562', 'Traction-control slip error (actual - target slip)', 'X', 'raw', 0, 'slip-error')
_v('fef02628', 'Manifold vacuum (AP - IAP, 7862 = 0 kPa)', '(X-7862)/393.14', 'kPa vacuum', 1, 'vacuum')

# constant address -> the RAM variable the code actually compares it with
CONST_FIXES = {0x154336: 'fef01562', 0x18B6E4: 'fef01562', 0x154338: 'fef01562', 0x15433A: 'fef01562', 0x15434C: 'fef02636', 0x154388: 'fef02634', 0x15438A: 'fef02636', 0x154396: 'fef02636', 0x154398: 'fef02636', 0x154434: 'fef02634', 0x154436: 'fef02636', 0x154497: 'fef02634', 0x154498: 'fef02634', 0x154499: 'fef02636', 0x15449A: 'fef02636', 0x1544AA: 'fef02634', 0x15476E: 'fef02634', 0x15483C: 'fef02600', 0x154848: 'fef02600', 0x154860: 'fef02636', 0x154862: 'fef02636', 0x154864: 'fef02636', 0x1548AA: 'fef0258e', 0x1548AC: 'fef0258e', 0x1548B4: 'fef02628', 0x1548E8: 'fef02636', 0x15490E: 'fef02628', 0x1549EC: 'fef02634', 0x1549ED: 'fef02636', 0x1824C6: 'fef02604', 0x1824D0: 'fef02604', 0x1824D2: 'fef02604', 0x18259C: 'fef02604', 0x1825BA: 'fef02604', 0x1825BC: 'fef02604', 0x1825BE: 'fef02604', 0x1825C2: 'fef02604', 0x18263C: 'fef02604', 0x18264C: 'fef02604', 0x18266A: 'fef02602', 0x18266E: 'fef02628', 0x18B632: 'fef02604', 0x18B63C: 'fef02604', 0x18B63E: 'fef02604', 0x18B644: 'fef02604', 0x18B648: 'fef02604', 0x18B64A: 'fef02604', 0x18B660: 'fef02604', 0x18B662: 'fef02636', 0x18B69E: 'fef0258e', 0x18B6A2: 'fef02636', 0x18B6CE: 'fef01562', 0x18B6D0: 'fef01562', 0x18B6D2: 'fef01562', 0x18B6D4: 'fef01562', 0x18B6D6: 'fef01562', 0x18B6D8: 'fef01562', 0x18B6DA: 'fef01562', 0x18B6DC: 'fef01562', 0x18B6DE: 'fef01562', 0x18B6E0: 'fef01562', 0x18B6E2: 'fef01562', 0x18B71C: 'fef025d2', 0x18B785: 'fef02636', 0x18C4A2: 'fef02636', 0x18C4FA: 'fef02594', 0x18C4FC: 'fef02594', 0x18C4FE: 'fef02636', 0x18C500: 'fef02594', 0x18C502: 'fef02594', 0x18C504: 'fef02636', 0x18DA5A: 'fef02636', 0x18DA5C: 'fef02636', 0x18DA5E: 'fef02636', 0x18DA60: 'fef02636', 0x18DA6A: 'fef0258e', 0x18DA70: 'fef02604', 0x18DA72: 'fef02604', 0x18DAAC: 'fef02636', 0x18DAAE: 'fef02636', 0x18DAB0: 'fef02636', 0x18DAB2: 'fef02636', 0x18DB2E: 'fef02634', 0x18DB30: 'fef02634', 0x18DB32: 'fef02634', 0x18DB34: 'fef02634', 0x18DB36: 'fef02634', 0x18EF56: 'fef02634', 0x18EFDC: 'fef02634', 0x18EFDE: 'fef02636', 0x18EFE0: 'fef02636', 0x18F06C: 'fef02634', 0x18F082: 'fef02634', 0x18F0D2: 'fef02636', 0x1AD856: 'fef02636', 0x1B6F2C: 'fef02592', 0x1B6F30: 'fef02636', 0x1B6F38: 'fef02636', 0x1B9468: 'fef02636', 0x1B946C: 'fef02636'}
# constants whose code comparison was confirmed directly (others were only tied by the old label,
# so they are re-scaled only when they carry the wrong inferred scaling and are 16-bit)
DIRECT = {0x154336, 0x18B6E4, 0x1824C6, 0x1824D0, 0x154388, 0x154396, 0x154398, 0x154434, 0x154436, 0x15476E, 0x15483C, 0x154848, 0x154862, 0x154864, 0x1548AA, 0x1548AC, 0x1548B4, 0x1548E8, 0x15490E, 0x1824D2, 0x18259C, 0x1825BA, 0x1825BC, 0x1825BE, 0x1825C2, 0x18263C, 0x18264C, 0x18266A, 0x18266E, 0x18B632, 0x18B63C, 0x18B63E, 0x18B644, 0x18B648, 0x18B64A, 0x18B660, 0x18B662, 0x18B69E, 0x18B6A2, 0x18B71C, 0x18C4A2, 0x18C4FA, 0x18C4FC, 0x18C4FE, 0x18C500, 0x18C502, 0x18C504, 0x18DA5A, 0x18DA5C, 0x18DA5E, 0x18DA60, 0x18DA6A, 0x18DA70, 0x18DA72, 0x18DAAC, 0x18DAAE, 0x18DAB0, 0x18DAB2, 0x18DB30, 0x18DB32, 0x18DB34, 0x18DB36, 0x18EF56, 0x18F06C, 0x18F082, 0x1AD856, 0x1B6F2C, 0x1B6F30, 0x1B6F38, 0x1B9468, 0x1B946C}
WRONG_INFERRED = ('X/364.08', 'X/5', 'X*0.9375-30', '(X-7862)/393.14', 'X/2.56')
SPECIAL_TITLES = {0x1824C6: 'Fuel Blend - Tip-In Rate Gate (forces TPS maps)',
                  0x1824D0: 'Accel Enrichment :: Min Throttle Opening Rate'}

# table axes (keyed by the table's Z data address): axis id -> (input var, equation, units, decimals)
AXIS_FIXES = {
    0x150E04: ('x', 'Cruise target speed (fef00A00)', 'X/128', 'km/h', 1),
    0x1512A8: ('x', 'Rear wheel speed, filtered (fef009F2)', 'X/128', 'km/h', 1),
    0x150818: ('x', 'Rear wheel speed, filtered (fef009F2)', 'X/128', 'km/h', 1),
    0x154190: ('x', 'Cruise controller internal value (fef00A3E, 0x8000-centred)', 'X', 'raw', 0),
    0x1549FC: ('x', 'Throttle opening rate (fef02604)', '(X-32768)/364.08', 'deg/4 samples', 1),
    0x184CD0: ('x', 'Throttle valve position (fef02600)', 'X/364.08', 'deg TP', 1),
    0x184D10: ('x', 'Throttle valve position (fef02600)', 'X/364.08', 'deg TP', 1),
    0x184D50: ('x', 'Throttle valve position (fef02600)', 'X/364.08', 'deg TP', 1),
    0x18CBD8: ('x', 'Rear wheel speed (fef01F4E = fef02636)', 'X/128', 'km/h', 1),
    0x18CC10: ('x', 'Rear wheel speed (fef01F4E = fef02636)', 'X/128', 'km/h', 1),
    0x18CC50: ('x', 'Rear wheel speed (fef01F4E = fef02636)', 'X/128', 'km/h', 1),
    0x1511D8: ('x', 'Rear wheel speed, averaged (fef0263C)', 'X/128', 'km/h', 1),
    0x18C6E8: ('x', 'Rear wheel speed, averaged (fef0263C)', 'X/128', 'km/h', 1),
    0x18C728: ('x', 'Rear wheel speed, averaged (fef0263C)', 'X/128', 'km/h', 1),
    0x18C768: ('x', 'Rear wheel speed, averaged (fef0263C)', 'X/128', 'km/h', 1),
    0x18E4C8: ('y', 'Wheel speed, front or rear (fef02978)', 'X/128', 'km/h', 1),
}
TITLE_FIXES = {'Speed Monitor :: Threshold vs fef01F4E': 'Speed Monitor :: Threshold vs Rear Wheel Speed',
               'Speed Monitor :: Upper Threshold vs fef01F4E': 'Speed Monitor :: Upper Threshold vs Rear Wheel Speed',
               'Speed Monitor :: Hysteresis Threshold vs fef01F4E (flat)': 'Speed Monitor :: Hysteresis Threshold vs Rear Wheel Speed (flat)',
               'IMU :: Map vs fef0268C x Wheel Speed (Helper 1)': 'IMU :: Map vs Lean x Wheel Speed (Helper 1)'}

TEXT_FIXES = [
    ('fef02636 = TP - Throttle position (copy).', 'fef02636 = Rear wheel speed (km/h = X/128).'),
    ('fef02634 = TP - Throttle position (copy).', 'fef02634 = Front wheel speed (km/h = X/128).'),
    ('fef02604 = TP - Throttle position used by fuel path.', 'fef02604 = Throttle opening rate (TP now - TP 4 samples ago, 0x8000 = 0).'),
    ('fef01562 = Grip% - Grip opening 0-100 % (X/5).', 'fef01562 = Traction-control slip error (actual - target slip, raw).'),
    ('Engine speed (copy) (RAM 0xFEF0264C)', 'RPM expected from wheel speed x gear ratio (RAM 0xFEF0264C)'),
    ('is forced to 256 (100% TPS map) at/above the WOT gate (0x1824C6, 91.4 deg). So at light/part throttle this map fuels the engine; at large throttle openings and WOT the TPS map does.',
     'is forced to 256 (100% TPS map) for 4 cycles after a fast throttle opening (tip-in rate gate 0x1824C6: TP rise of 1.41 deg or more within 4 samples). So at light/part throttle this map fuels the engine; at large openings, WOT and on fast tip-in the TPS map does.'),
    ('Above the WOT gate (Fuel Blend - WOT Throttle-Path Gate, 91.4 deg) the TPS maps always have 100% authority.',
     'On a fast throttle opening (Fuel Blend - Tip-In Rate Gate: TP rise of 1.41 deg or more within 4 samples) the TPS maps take 100% authority for 4 cycles.'),
    ('while TP (fef02604) is at/above the WOT gate (0x1824C6)', 'while the throttle opening rate (fef02604: TP rise over 4 samples) is at/above the tip-in rate gate (0x1824C6)'),
    ('After TP drops below the gate', 'After the rate drops below the gate'),
    ('blend curve and WOT gate are 0xFFFF', 'blend curve and tip-in rate gate (0x1824C6) are 0xFFFF'),
]
GATE_DESC = ('Tip-in rate gate (FUN_4916E / FUN_491BC). Compared with fef02604 = throttle opening rate '
             '(TP now - TP 4 samples ago, 0x8000 = 0), NOT throttle position. While the rate is at/above '
             'this value, and for 0x18267A (4) cycles after it drops below, the ECU forces 100% TPS-map '
             'fuel (blend weight fef011CA = 256). Stock 33282 = TP rise of 1.41 deg within 4 samples. '
             '0xFFFF disables it (SD-v2 and later race bins do this so the speed-density map keeps '
             'authority on tip-in). Earlier XDFs showed this as a 91.4 deg WOT gate - that was wrong.')

BLOCK = re.compile(r'<(XDFCONSTANT|XDFTABLE|XDFFLAG) uniqueid="(0x[0-9A-Fa-f]+)"[^>]*>.*?</\1>', re.S)


def fmt(v, dec):
    return ('%.' + str(dec) + 'f') % v if dec else '%d' % round(v)


def fix_constant(blk, b, sw):
    addr = int(re.search(r'mmedaddress="(0x[0-9A-Fa-f]+)"', blk).group(1), 16)
    var = CONST_FIXES.get(addr)
    if not var:
        return blk
    label, eq, units, dec, word = V[var]
    bits = int(re.search(r'mmedelementsizebits="(\d+)"', blk).group(1))
    cur = re.search(r'<MATH equation="([^"]*)"', blk).group(1)
    rescale = addr in DIRECT or (cur in WRONG_INFERRED and bits == 16)
    if bits == 8 and eq != 'X':          # 8-bit items never carry a 16-bit sensor scale
        rescale, eq, units, dec = (cur in WRONG_INFERRED), 'X', 'raw', 0
    if rescale:
        blk = re.sub(r'<MATH equation="[^"]*">', '<MATH equation="%s">' % eq, blk, count=1)
        blk = re.sub(r'<units>.*?</units>', '<units>%s</units>' % escape(units, quote=False), blk, count=1)
        blk = re.sub(r'<decimalpl>\d+</decimalpl>', '<decimalpl>%d</decimalpl>' % dec, blk, count=1)
    else:
        eq = cur
        units = re.search(r'<units>(.*?)</units>', blk).group(1) if '<units>' in blk else 'raw'
    # title
    t = re.search(r'<title>(.*?)</title>', blk).group(1)
    nt = SPECIAL_TITLES.get(addr) or re.sub(r'\b(throttle|temperature|RPM|pressure|angle|speed|grip %|grip) threshold',
                                             word + ' threshold', t)
    blk = blk.replace('<title>%s</title>' % t, '<title>%s</title>' % escape(nt, quote=False), 1)
    # description: compared-with line, special text, STOCK line
    blk = re.sub(r'COMPARED WITH: fef[0-9A-Fa-f]+ = [^\n<]*', 'COMPARED WITH: %s = %s (verified from code, v9.2).' % (var, escape(label, quote=False)), blk, count=1)
    if addr == 0x1824C6:
        blk = re.sub(r'<description>.*?(\n\nSTOCK|</description>)', lambda m: '<description>' + escape(GATE_DESC, quote=False) + m.group(1), blk, count=1, flags=re.S)
    raw = int.from_bytes(b[addr:addr + bits // 8], 'little')
    v = eval(eq, {'X': raw})
    dm = re.search(r'<decimalpl>(\d+)</decimalpl>', blk)
    dec = int(dm.group(1)) if dm else 0
    stock = 'STOCK (%s): %s %s (raw %d / 0x%X). ADDRESS 0x%X, %d-bit.' % (sw, fmt(v, dec), units, raw, raw, addr, bits)
    blk = re.sub(r'STOCK \(%s\): [^\n<]*' % re.escape(sw), stock, blk, count=1)
    if addr == 0x1824C6 and 'STOCK (' not in blk:
        blk = blk.replace('</description>', '\n\n' + stock + '</description>', 1)
    return blk


def axis_values(b, blk, axis_id):
    m = re.search(r'<XDFAXIS id="%s"[^>]*>.*?</XDFAXIS>' % axis_id, blk, re.S)
    a = m.group(0)
    ed = re.search(r'<EMBEDDEDDATA[^>]*mmedaddress="(0x[0-9A-Fa-f]+)"[^>]*mmedelementsizebits="(\d+)"', a)
    n = int(re.search(r'<indexcount>(\d+)</indexcount>', a).group(1))
    ad, bits = int(ed.group(1), 16), int(ed.group(2))
    return m, [int.from_bytes(b[ad + i * bits // 8: ad + (i + 1) * bits // 8], 'little') for i in range(n)]


def fix_table(blk, b):
    z = re.search(r'<XDFAXIS id="z".*?mmedaddress="(0x[0-9A-Fa-f]+)"', blk, re.S)
    t = re.search(r'<title>(.*?)</title>', blk).group(1)
    if t in TITLE_FIXES:
        blk = blk.replace('<title>%s</title>' % t, '<title>%s</title>' % TITLE_FIXES[t], 1)
    if not z or int(z.group(1), 16) not in AXIS_FIXES:
        return blk
    axis_id, label, eq, units, dec = AXIS_FIXES[int(z.group(1), 16)]
    m, raw = axis_values(b, blk, axis_id)
    a = m.group(0)
    a2 = re.sub(r'<MATH equation="[^"]*">', '<MATH equation="%s">' % eq, a, count=1)
    a2 = re.sub(r'<units>.*?</units>', '<units>%s</units>' % escape(units, quote=False), a2, count=1) if '<units>' in a2 else a2
    a2 = re.sub(r'<decimalpl>\d+</decimalpl>', '<decimalpl>%d</decimalpl>' % dec, a2, count=1)
    blk = blk[:m.start()] + a2 + blk[m.end():]
    vals = [eval(eq, {'X': x}) for x in raw]
    new_axis = '%s axis: %d points, %s to %s %s' % (axis_id.upper(), len(vals), fmt(vals[0], dec), fmt(vals[-1], dec), units)
    blk = re.sub(r'%s axis: \d+ points, (?:[^;.<\n]|\.(?=\d))*' % axis_id.upper(), new_axis, blk, count=1)
    note = ' %s input verified from code (v9.2): %s.' % (axis_id.upper(), label)
    if note not in blk:
        blk = re.sub(r'(AXES: [^\n<]*)', lambda m: m.group(1) + note, blk, count=1)
    return blk


def apply(text, b, sw):
    for old, new in TEXT_FIXES:
        text = text.replace(escape(old, quote=False), escape(new, quote=False))
    out, last = [], 0
    for m in BLOCK.finditer(text):
        blk = m.group(0)
        if m.group(1) == 'XDFCONSTANT':
            blk = fix_constant(blk, b, sw)
        elif m.group(1) == 'XDFTABLE':
            blk = fix_table(blk, b)
        out.append(text[last:m.start()])
        out.append(blk)
        last = m.end()
    out.append(text[last:])
    text = ''.join(out)
    ET.fromstring(text)  # still valid XML
    return text


if __name__ == '__main__':
    path, binp, sw = sys.argv[1:4]
    text = open(path, encoding='utf-8').read()
    new = apply(text, open(binp, 'rb').read(), sw)
    open(path, 'w', encoding='utf-8').write(new)
    print('%s: %s' % (path, 'updated' if new != text else 'no changes'))
