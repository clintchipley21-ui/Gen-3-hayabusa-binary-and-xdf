#!/usr/bin/env python3
"""Generate a TunerPro XDF for a Suzuki GSX-R1000 (M7, Renesas RH850) read by porting the
Gen-3 Hayabusa master map definitions onto the GSX-R's OWN on-bin map descriptors.

Why this works: the GSX-R M7 ECU stores the same Suzuki "map descriptor" table the Hayabusa
does (20-byte records: type, cols, rows, flag, then little-endian X/Y/data pointers). The
descriptor array, the record types and the calibration ordering are the same family, so:

  1. we scan the GSX-R bin for its descriptors (validated: the identical scanner recovers all
     749 Hayabusa descriptors exactly, 0 missing / 0 false positives);
  2. we scan the Hayabusa reference read for its descriptors and attach each one's named master
     definition (title, axis bit-size, scaling, units, folders);
  3. we sequence-align the two descriptor lists by (type, cols, rows) in calibration order;
  4. for every GSX-R descriptor that aligns to a named Hayabusa map we reuse that map's EXACT
     XDF block (bit sizes, strides, scaling equations, units, category folders) and only swap
     in the GSX-R addresses + rewrite the title/description. Confidence:
         HIGH - the GSX-R and Hayabusa axis breakpoints are byte-identical (same map);
         MED  - same type/size, aligned by order, but breakpoints differ (strong guess - verify);
     GSX-R descriptors with no Hayabusa counterpart become generic "Unknown Map/Curve" items.

What this XDF contains: every map and curve in the bin (the GSX-R has 791 descriptors). It does
NOT contain the Hayabusa's ~2,900 scalar constants/flags - those have no descriptor and were
found by per-address code analysis that does not carry over to the GSX-R.

Checksums are NOT handled here: re-stamp the field-1 CRC with the repo's tools/fix_field1_crc.py
(identical method, verified on all four GSX-R reads) after editing.

usage:  python3 gsxr-1000/tools/make_gsxr_xdf.py <read.bin> <out.xdf> <software> <partno>
"""
import os, re, struct, sys, difflib
from html import escape as _escape


def escape(s):
    """XML-escape element text (&, <, >) but NOT quotes. Everything this module escapes goes
    into element content (<title>/<description>/<units>), never an attribute value, so apostrophes
    and double-quotes must stay as literal characters. TunerPro's XDF reader chokes on the numeric
    apostrophe entity &#x27; that html.escape emits by default, so we must avoid it (the working
    Hayabusa master XDF contains zero such entities)."""
    return _escape(str(s), quote=False)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))              # repo root
HAYA = os.path.join(ROOT, 'hayabusa')                      # parent-repo Hayabusa tree
HAYA_MASTER = os.path.join(HAYA, 'stock/master/master-v9.xdf')
HAYA_REF_BIN = os.path.join(HAYA, 'stock/5JCZSJ10/5JCZSJ10.bin')
REF_SW = '5JCZSJ10'

# ---------------------------------------------------------------- descriptor scan
TYPES_1D = {0x05, 0x06, 0x09, 0x0a}
TYPES_2D = {0x29, 0x2a, 0x15}
TYPES = TYPES_1D | TYPES_2D
ZBITS = {0x05: 8, 0x09: 8, 0x29: 8, 0x15: 8, 0x06: 16, 0x0a: 16, 0x2a: 16}
SCAN_LO, SCAN_HI = 0x150000, 0x1C0000


def u32(b, a):
    return struct.unpack('<I', b[a:a + 4])[0] if 0 <= a and a + 4 <= len(b) else None


def scan(b, lo=SCAN_LO, hi=SCAN_HI):
    out = []
    for a in range(lo, hi, 4):
        t = b[a]
        if t not in TYPES:
            continue
        c, r, f = b[a + 1], b[a + 2], b[a + 3]
        if f != 0 or not (1 <= c <= 64):
            continue
        xp, yp, dp = u32(b, a + 4), u32(b, a + 8), u32(b, a + 12)

        def inbin(p):
            return p is not None and lo <= p < hi

        def ptrok(p):
            return p == 0 or inbin(p)

        if not (ptrok(xp) and ptrok(yp) and ptrok(dp)):
            continue
        if t in TYPES_2D:
            if not (1 <= r <= 64) or not inbin(dp) or not inbin(xp):
                continue
        else:
            if r != 0 or not inbin(xp):
                continue
        out.append(dict(a=a, t=t, c=c, r=r, xp=xp, yp=yp, dp=dp, w4=u32(b, a + 16)))
    return out


# ---------------------------------------------------------------- master parse
BLOCK = re.compile(r'(  <XDFTABLE uniqueid="0x[0-9A-Fa-f]+".*?</XDFTABLE>\n)', re.S)
DADDR = re.compile(r'descriptor @0x([0-9A-Fa-f]+)')


def master_blocks():
    """daddr -> dict(block=text, title=..)  for every descriptor-backed Hayabusa table."""
    txt = open(HAYA_MASTER).read()
    out = {}
    for m in BLOCK.finditer(txt):
        blk = m.group(1)
        d = DADDR.search(blk)
        if not d:
            continue
        title = re.search(r'<title>(.*?)</title>', blk, re.S)
        out[int(d.group(1), 16)] = dict(block=blk, title=(title.group(1) if title else ''))
    return out


# Decompiled Hayabusa map metadata (re/decompiled.zip): per descriptor, the X/Y RAM-input
# meanings and the function that reads the map. Ported onto aligned GSX-R maps as context.
HAYA_DECOMP = os.path.join(HAYA, 're/decompiled.zip')


def map_links():
    """haya descriptor addr -> dict(xin, yin, func) from the Hayabusa decompile, if present."""
    import csv
    import zipfile
    out = {}
    if not os.path.exists(HAYA_DECOMP):
        return out
    try:
        with zipfile.ZipFile(HAYA_DECOMP) as z:
            rows = csv.DictReader(z.read('map_links.csv').decode().splitlines())
            for r in rows:
                if not r.get('descriptor'):
                    continue
                out[int(r['descriptor'], 16)] = dict(
                    xin=r.get('x_input_meaning', '').strip(),
                    yin=r.get('y_input_meaning', '').strip(),
                    func=r.get('function', '').strip())
    except Exception:
        pass
    return out


# ---------------------------------------------------------------- value reads
def read_axis(b, addr, n, bits, signed=False):
    step = bits // 8
    vals = []
    for i in range(n):
        v = int.from_bytes(b[addr + i * step:addr + (i + 1) * step], 'little')
        if signed and v >= 1 << (bits - 1):
            v -= 1 << bits
        vals.append(v)
    return vals


def guess_axis_bits(b, addr, n):
    """For generic items: pick the width whose breakpoints look monotonic."""
    def mono(bits):
        v = read_axis(b, addr, n, bits)
        return all(v[i] <= v[i + 1] for i in range(len(v) - 1)) and max(v) < (1 << bits)
    if n <= 1:
        return 16
    if mono(16):
        return 16
    if mono(8):
        return 8
    return 16


def ev(eq, x):
    try:
        return eval(eq, {'__builtins__': {}}, {'X': float(x)})
    except Exception:
        return x


def fmt(v):
    v = float(v)
    return ('%d' % v) if v.is_integer() else ('%.2f' % v)


# ---------------------------------------------------------------- block surgery
def _set_axis_addr(block, axis_id, addr):
    """Replace mmedaddress of the EMBEDDEDDATA inside <XDFAXIS id="axis_id">."""
    pat = re.compile(r'(<XDFAXIS id="%s".*?<EMBEDDEDDATA\b[^>]*?mmedaddress=")0x[0-9A-Fa-f]+(")'
                     % re.escape(axis_id), re.S)
    new, n = pat.subn(lambda m: m.group(1) + ('0x%X' % addr) + m.group(2), block, count=1)
    return new, n


def axis_info(block, axis_id):
    """(addr,bits,signed,eq,units) for an axis in a master block, or None."""
    am = re.search(r'<XDFAXIS id="%s".*?</XDFAXIS>' % re.escape(axis_id), block, re.S)
    if not am:
        return None
    sub = am.group(0)
    em = re.search(r'<EMBEDDEDDATA\b([^>]*)>', sub)
    if not em or 'mmedaddress' not in em.group(1):
        return None
    attrs = em.group(1)

    def at(k, d=None):
        mm = re.search(r'%s="([^"]*)"' % k, attrs)
        return mm.group(1) if mm else d
    bits = int(at('mmedelementsizebits', '8'))
    signed = int(at('mmedtypeflags', '0x0'), 16) & 1
    eqm = re.search(r'<MATH equation="([^"]*)"', sub)
    um = re.search(r'<units>(.*?)</units>', sub, re.S)
    return dict(addr=int(at('mmedaddress'), 16), bits=bits, signed=bool(signed),
                eq=(eqm.group(1) if eqm else 'X'), units=(um.group(1) if um else 'raw'))


def retitle(block, title, desc):
    block = re.sub(r'<title>.*?</title>', '<title>%s</title>' % escape(title),
                   block, count=1, flags=re.S)
    block = re.sub(r'<description>.*?</description>',
                   '<description>%s</description>' % escape(desc), block, count=1, flags=re.S)
    return block


# ---------------------------------------------------------------- descriptions
def axes_line(b, d, xinfo, yinfo):
    parts = []
    xb = xinfo['bits'] if xinfo else guess_axis_bits(b, d['xp'], d['c'])
    xeq = xinfo['eq'] if xinfo else 'X'
    xu = xinfo['units'] if xinfo else 'raw'
    xv = read_axis(b, d['xp'], d['c'], xb, xinfo['signed'] if xinfo else False)
    parts.append('X: %d pts %s..%s %s' % (d['c'], fmt(ev(xeq, xv[0])), fmt(ev(xeq, xv[-1])), xu))
    if d['r'] > 0:
        yb = yinfo['bits'] if yinfo else guess_axis_bits(b, d['yp'], d['r'])
        yeq = yinfo['eq'] if yinfo else 'X'
        yu = yinfo['units'] if yinfo else 'raw'
        yv = read_axis(b, d['yp'], d['r'], yb, yinfo['signed'] if yinfo else False)
        parts.append('Y: %d pts %s..%s %s' % (d['r'], fmt(ev(yeq, yv[0])), fmt(ev(yeq, yv[-1])), yu))
    return '; '.join(parts)


def values_line(b, d, zinfo, sw):
    zbits = ZBITS[d['t']]
    zsigned = zinfo['signed'] if zinfo else False
    zeq = zinfo['eq'] if zinfo else 'X'
    zu = zinfo['units'] if zinfo else 'raw'
    zaddr = d['dp'] if d['r'] > 0 else d['yp']
    n = (d['r'] or 1) * d['c']
    raw = read_axis(b, zaddr, n, zbits, zsigned)
    lo, hi = min(raw), max(raw)
    return 'VALUES (%s): %s to %s %s%s.' % (
        sw, fmt(ev(zeq, lo)), fmt(ev(zeq, hi)), zu,
        ' - every cell the same' if lo == hi else '')


def reference_line(d):
    zaddr = d['dp'] if d['r'] > 0 else d['yp']
    s = 'REFERENCE: descriptor @0x%X, data @0x%X, X @0x%X' % (d['a'], zaddr, d['xp'])
    if d['r'] > 0:
        s += ', Y @0x%X' % d['yp']
    return s + '.'


# ---------------------------------------------------------------- generic block
GENERIC = '''  <XDFTABLE uniqueid="0x%(uid)X" flags="0x0">
    <title>%(title)s</title>
    <description>%(desc)s</description>
    <CATEGORYMEM index="0" category="%(cat)d" />
    <XDFAXIS id="x">
      <EMBEDDEDDATA mmedtypeflags="0x02" mmedaddress="0x%(xp)X" mmedelementsizebits="%(xb)d" mmedcolcount="%(c)d" mmedmajorstridebits="0" mmedminorstridebits="0" />
      <units>raw</units>
      <indexcount>%(c)d</indexcount>
      <decimalpl>0</decimalpl>
      <embedinfo type="1" />
      <datatype>0</datatype>
      <unittype>0</unittype>
      <DALINK index="0" />
      <MATH equation="X"><VAR id="X" /></MATH>
    </XDFAXIS>
%(yaxis)s    <XDFAXIS id="z">
      <EMBEDDEDDATA mmedtypeflags="0x02" mmedaddress="0x%(zp)X" mmedelementsizebits="%(zb)d" mmedrowcount="%(zr)d" mmedcolcount="%(c)d" mmedmajorstridebits="0" mmedminorstridebits="0" />
      <units>raw</units>
      <decimalpl>0</decimalpl>
      <outputtype>1</outputtype>
      <MATH equation="X"><VAR id="X" /></MATH>
    </XDFAXIS>
  </XDFTABLE>
'''
GENERIC_Y = '''    <XDFAXIS id="y">
      <EMBEDDEDDATA mmedtypeflags="0x02" mmedaddress="0x%(yp)X" mmedelementsizebits="%(yb)d" mmedcolcount="%(r)d" mmedmajorstridebits="0" mmedminorstridebits="0" />
      <units>raw</units>
      <indexcount>%(r)d</indexcount>
      <decimalpl>0</decimalpl>
      <embedinfo type="1" />
      <datatype>0</datatype>
      <unittype>0</unittype>
      <DALINK index="0" />
      <MATH equation="X"><VAR id="X" /></MATH>
    </XDFAXIS>
'''


def generic_block(b, d, uid, cat):
    is2d = d['r'] > 0
    xb = guess_axis_bits(b, d['xp'], d['c'])
    yb = guess_axis_bits(b, d['yp'], d['r']) if is2d else 8
    zb = ZBITS[d['t']]
    kind = 'Map %dx%d' % (d['c'], d['r']) if is2d else 'Curve %d' % d['c']
    zaddr = d['dp'] if is2d else d['yp']
    title = 'Unknown %s @0x%X' % (kind, zaddr)
    tl = traced_inputs_line(d['a'], TRACED_MAP)
    desc = ('AUTO-DISCOVERED from the ECU map descriptor; no Hayabusa map aligned here, role '
            'unknown - log before changing.\n%s\n%s%s\n%s'
            % (axes_line(b, d, None, None), (tl + '\n') if tl else '',
               values_line(b, d, None, SW), reference_line(d)))
    yaxis = (GENERIC_Y % dict(yp=d['yp'], yb=yb, r=d['r'])) if is2d else ''
    return GENERIC % dict(uid=uid, title=escape(title), desc=escape(desc), cat=cat,
                          xp=d['xp'], xb=xb, c=d['c'], r=d['r'], zr=(d['r'] or 1),
                          zp=zaddr, zb=zb, yaxis=yaxis)


# ---------------------------------------------------------------- ported block
def inputs_line(ml):
    """One line of decompile-derived X/Y signal meanings + reading function, or ''."""
    if not ml:
        return ''
    bits = []
    if ml.get('xin'):
        bits.append('X = %s' % ml['xin'])
    if ml.get('yin'):
        bits.append('Y = %s' % ml['yin'])
    tail = (' Read by %s.' % ml['func']) if ml.get('func') else ''
    if not bits and not tail:
        return ''
    return 'INPUTS (Hayabusa decompile): %s.%s' % ('; '.join(bits) if bits else 'n/a', tail)


def ported_block(b, d, m, conf, sw, ml=None):
    blk = m['block']
    is2d = d['r'] > 0
    xi = axis_info(blk, 'x')
    yi = axis_info(blk, 'y') if is2d else None
    zi = axis_info(blk, 'z')
    # swap addresses: X -> xp ; (2D) Y -> yp, Z -> dp ; (1D) Z -> yp
    blk, _ = _set_axis_addr(blk, 'x', d['xp'])
    if is2d:
        blk, _ = _set_axis_addr(blk, 'y', d['yp'])
        blk, _ = _set_axis_addr(blk, 'z', d['dp'])
    else:
        blk, _ = _set_axis_addr(blk, 'z', d['yp'])
    base = m['title']
    if conf == 'HIGH':
        head = ('PORTED FROM HAYABUSA %s (HIGH: breakpoints byte-identical, almost certainly the '
                'same map). Units/scaling carried over; GSX-R addresses & values are this read\'s '
                'own. Hayabusa code refs are not verified on GSX-R.' % REF_SW)
        title = base
    else:
        head = ('PORTED FROM HAYABUSA %s (MED: same type/size and aligned by calibration order, '
                'but breakpoints differ - title is a strong guess, VERIFY before trusting). '
                'Units/scaling carried over; GSX-R addresses & values are this read\'s own.' % REF_SW)
        title = base + '  [UNCONFIRMED]'
    parts = [head, axes_line(b, d, xi, yi)]
    tl = traced_inputs_line(d['a'], TRACED_MAP)
    if tl:
        parts.append(tl)
    il = inputs_line(ml)
    if il:
        parts.append(il)
    parts += [values_line(b, d, zi, sw), reference_line(d)]
    return retitle(blk, title, '\n'.join(parts))


# ---------------------------------------------------------------- categories
def clean_cat_name(name):
    """Scrub Hayabusa-specific artifacts from an inherited category name: the Hayabusa ID-range
    'Unidentified - Cluster X' buckets mean nothing on the GSX-R, and '(legacy, empty)' is stale."""
    if 'Unidentified - Cluster' in name:
        return 'Uncategorized (auto-ported, verify)'
    return name.replace(' (legacy, empty)', '')


def category_block():
    txt = open(HAYA_MASTER).read()
    cats = re.findall(r'    <CATEGORY index="0x[0-9A-Fa-f]+" name="[^"]*" />\n', txt)
    cats = [re.sub(r'name="[^"]*"',
                   lambda m: 'name="%s"' % clean_cat_name(m.group(0)[6:-1]), c) for c in cats]
    maxidx = max(int(re.search(r'index="(0x[0-9A-Fa-f]+)"', c).group(1), 16) for c in cats)
    unmatched = maxidx + 1
    scalarcat = maxidx + 2
    cats.append('    <CATEGORY index="0x%X" name="ZZ Unmatched / Auto-discovered (verify)" />\n'
                % unmatched)
    cats.append('    <CATEGORY index="0x%X" name="ZZ Decompiler-discovered scalars (unverified)" />\n'
                % scalarcat)
    cats.append('    <CATEGORY index="0x%X" name="Steering Damper (ESD) (decoded)" />\n'
                % (maxidx + 3))
    # TunerPro CATEGORYMEM category="N" is 1-BASED: it selects CATEGORY index N-1 (verified against
    # the Hayabusa master, which the ported maps inherit their 1-based values from). So every category
    # VALUE the generator emits is (0-based index + 1). name2val maps a category NAME to that value.
    name2val = {}
    for c in cats:
        mm = re.search(r'index="(0x[0-9A-Fa-f]+)" name="([^"]*)"', c)
        if mm:
            name2val[mm.group(2)] = int(mm.group(1), 16) + 1
    return ''.join(cats), unmatched + 1, scalarcat + 1, name2val


# SUBSYS tag -> the "Scalars - X" category name in the master (unescaped). Untagged scalars, or
# tags with no dedicated folder, fall back to the generic decompiler-scalar category.
SCALAR_CAT_NAME = {
    'Ignition': 'Scalars - Ignition', 'Quickshifter': 'Scalars - Quickshifter',
    'Launch Control': 'Scalars - Launch Control', 'Traction Control': 'Scalars - Traction Control',
    'Anti-Lift': 'Scalars - Anti-Lift Control', 'Cruise Control': 'Scalars - Cruise Control',
    'Engine Brake': 'Scalars - Engine Brake Control', 'Fuel': 'Scalars - Fuel',
    'Idle/Fan': 'Scalars - Idle Control', 'O2/Closed-Loop': 'Scalars - HO2 / Closed Loop',
    'Rev/Speed Limiter': 'Scalars - Limiters', 'Throttle/ETV': 'Scalars - Throttle By Wire',
    'Diagnostics': 'Scalars - Diagnostics - Monitors', 'IMU/Chassis': 'Scalars - IMU / Wheel Speed',
    'Speed/Wheel': 'Scalars - IMU / Wheel Speed', 'Ride Modes': 'Scalars - Ride Mode Presets',
    'Sensors': 'Scalars - Sensor Scaling (MAP/baro)',
}


# Title-prefix -> correct category NAME, for decoded GSX-R maps the Hayabusa master mis-filed
# (e.g. it parks "Ride Mode" and "Mode-Setting Limit" tables in its "DTC Lamp Control" folder, and
# "Idle/Heat-Soak" tables in "Meter / CAN Outputs"). Only titles matching a rule are re-filed; every
# other map keeps the category it inherited, so the already-correct folders (TPS, IAP, Ignition
# Advance, PWR-n, Launch Control, Anti-Lift ...) are untouched. Ground truth is the map's own title.
RECAT = [
    ('Ride Mode ::', 'Ride Mode Presets'), ('Mode-Setting Limit ::', 'Ride Mode Presets'),
    ('Idle/Heat-Soak ::', 'Idle Control (decoded)'), ('Idle Control ::', 'Idle Control (decoded)'),
    ('ETV Monitor ::', 'ETV Monitor / Level-2 Safety (decoded)'),
    ('Meter / CAN Outputs ::', 'Meter / CAN Outputs (decoded)'),
    ('Meter Fuel Consumption ::', 'Meter / CAN Outputs (decoded)'),
    ('EVAP Purge ::', 'EVAP Purge (decoded)'),
    ('Catalyst/HO2 Monitor ::', 'HO2 / Closed Loop (decoded)'), ('HO2 ', 'HO2 / Closed Loop (decoded)'),
    ('Cruise Control ::', 'Cruise Control (decoded)'),
    ('Engine Brake Control ::', 'Engine Brake Control (decoded)'),
    ('Pitch Control ::', 'Anti-Lift Control'), ('Anti-Lift ::', 'Anti-Lift Control'),
    ('Speed Monitor ::', 'IMU / Wheel Speed (decoded)'),
    ('Diagnostics - DTC Lamp Control ::', 'Diagnostics - DTC Lamp Control'),
]


# Electronic steering damper (ESD) module - decompile-confirmed (see docs/tracing.md 3o).
# Controller FUN_000784dc: rear-wheel speed 0xFEBF63F4 -> one of three 16-pt curves -> modulation
# chain -> FUN_00024cb4 (PWM channel 0x500) -> T54 solenoid. These descriptors are referenced ONLY
# by the ESD module's own functions. Titles get a "Steering Damper ::" prefix so the RECAT rule below
# re-files them into the dedicated folder.
DAMPER_CAT = 'Steering Damper (ESD) (decoded)'
DAMPER_TABLES = {
    0x1716AC: 'Steering Damper :: Damping vs Speed - Mode 1',
    0x1716C0: 'Steering Damper :: Damping vs Speed - Mode 2',
    0x1716D4: 'Steering Damper :: Damping vs Speed - Mode 3',
    0x1716E8: 'Steering Damper :: Secondary Curve - Mode 1 (axis unverified)',
    0x1716FC: 'Steering Damper :: Secondary Curve - Mode 2 (axis unverified)',
    0x171710: 'Steering Damper :: Secondary Curve - Mode 3 (axis unverified)',
    0x171724: 'Steering Damper :: Correction Factor (axis unverified)',
    0x171738: 'Steering Damper :: Correction Table A (verify)',
    0x17174C: 'Steering Damper :: Correction Table B (verify)',
    0x171760: 'Steering Damper :: Output compensation (vs 0xFEBF643C, axis unverified)',
    0x155218: 'Steering Damper :: Diagnostic threshold (lo)',
    0x15522C: 'Steering Damper :: Diagnostic threshold (hi)',
}
# Per-table description overrides (default note used otherwise).
DAMPER_NOTES = {
    0x171760: ('Electronic steering damper output-compensation gain (5-pt, centred on 0x8000 = 1.0; '
               'stock 1.17 at low end -> 0.88 at high end). Indexed by 0xFEBF643C, an IMU/chassis-'
               'derived signed signal (0x8000 = neutral, rate-limited) from the fef0265A-2668 block '
               'that also feeds the damper secondary inputs 0xFEBF642A/C/E - i.e. the ESD modulates '
               'on vehicle attitude/dynamics, not just speed (exact IMU axis not yet pinned). SHARED '
               'within the ESD subsystem: the controller FUN_00078308 '
               'multiplies the damper modulation by this gain, and the damper solenoid DIAGNOSTIC '
               '(FUN_0003a062 / 0003a0be / 0003a1b6 / 0003a32e, which set fault bits in fef009c9 / '
               'fef009ca from the damper command 0xFEBF62BC) scales its expected-feedback thresholds '
               'by it. Not shared with any non-damper module.'),
    0x155218: ('ESD solenoid-diagnostic threshold, lower bound. The damper fault monitor '
               '(FUN_0003a062/0003a1b6/0003a32e) looks this up on the damper command 0xFEBF62BC, '
               'scales it by the 0x171760 compensation gain, and flags a fault if the measured '
               'feedback 0xFEBF6422 falls outside [lo,hi]. Backs the steering-damper solenoid DTC.'),
    0x15522C: ('ESD solenoid-diagnostic threshold, upper bound (pair of 0x155218). See 0x155218.'),
}
# The three Damping-vs-Speed curves share one note; it is only correct for them.
DAMPER_SPEED_NOTE = (
    'ELECTRONIC STEERING DAMPER modulation curve (decompile-confirmed). X axis = rear-wheel speed '
    '0xFEBF63F4: raw 2560 = 20 km/h, so the 16 breakpoints are 0,20,40,...,300 km/h. Output = damping '
    'modulation (stock: 0 below ~60 km/h, rising to ~0x4000 = full at 300 km/h = light steering at low '
    'speed, firm at high speed). Three mode curves (1/2/3) selected by 0xFEBF6480. Read by FUN_00078006; '
    'feeds the PWM solenoid on T54 via FUN_00024cb4 (ch 0x500). This is the "steering damper map" that '
    'commercial tools edit; set the enable byte 0x172F28 to 0x00 to disable the damper entirely.')
DAMPER_SCALARS = {
    0x172F28: ('Steering Damper :: Enable (0xFF=on, 0x00=disable)',
               'MASTER ESD ENABLE byte (u8). 0xFF (all stock reads) = damper active; 0x00 = output '
               'forced to zero (this is the commercial "Disable Steering Damper" setting); 0x80 = '
               'alternate branch. Read by FUN_00078058 / FUN_00078534.'),
    0x172E3A: ('Steering Damper :: Activation speed threshold',
               'Rear-wheel-speed threshold (u16) gating ESD activation in FUN_00077A8C.'),
}


def label_damper(body, name2val):
    """Relabel the decompile-confirmed steering-damper descriptors and scalars, and re-file them into
    the Steering Damper folder. Operates on the emitted block text, matching tables by their
    'descriptor @0xADDR' reference line and scalars by mmedaddress."""
    dval = name2val[DAMPER_CAT]
    n = 0

    def retitle_cat(block, new_title, note):
        b2 = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % escape(new_title), block, count=1)
        b2 = re.sub(r'<description>', '<description>%s\n\n' % escape(note), b2, count=1)
        b2 = re.sub(r'(<CATEGORYMEM index="0" category=")\d+(")',
                    r'\g<1>%d\g<2>' % dval, b2, count=1)
        # drop any extra CATEGORYMEM so the item sits only in the damper folder
        b2 = re.sub(r'\s*<CATEGORYMEM index="[1-9][0-9]*"[^/]*/>', '', b2)
        return b2

    # tables (XDFTABLE): locate by the "descriptor @0xADDR" reference line in the description
    def repl_table(m):
        nonlocal n
        blk = m.group(0)
        for addr, title in DAMPER_TABLES.items():
            if ('descriptor @0x%X' % addr) in blk:
                n += 1
                if addr in (0x1716AC, 0x1716C0, 0x1716D4):
                    note = DAMPER_SPEED_NOTE
                elif addr in DAMPER_NOTES:
                    note = DAMPER_NOTES[addr]
                else:
                    note = ('Electronic steering damper module table (decompile-confirmed; referenced '
                            'only by the ESD controller FUN_000784dc). Role within the modulation '
                            'chain not fully resolved - verify before changing.')
                return retitle_cat(blk, title, note)
        return blk
    body = re.sub(r'<XDFTABLE\b.*?</XDFTABLE>\s*', repl_table, body, flags=re.S)

    # scalars (XDFCONSTANT): locate by mmedaddress
    def repl_scalar(m):
        nonlocal n
        blk = m.group(0)
        am = re.search(r'mmedaddress="(0x[0-9A-Fa-f]+)"', blk)
        if am:
            addr = int(am.group(1), 16)
            if addr in DAMPER_SCALARS:
                n += 1
                title, note = DAMPER_SCALARS[addr]
                return retitle_cat(blk, title, note)
        return blk
    body = re.sub(r'<XDFCONSTANT\b.*?</XDFCONSTANT>\s*', repl_scalar, body, flags=re.S)
    return body, n


def recategorize(body, name2val):
    """Re-file only the decoded maps the Hayabusa master mis-categorised, by matching the map's own
    title prefix to the correct existing category. category values are 1-based. Returns (body,n)."""
    rules = [(p, name2val[n]) for p, n in RECAT if n in name2val]
    moved = [0]

    def fix(block):
        mt = re.search(r'<title>([^<]*)</title>', block)
        if not mt:
            return block
        title = mt.group(1)
        for pre, newcat in rules:
            if title.startswith(pre) or pre in title:
                new = re.sub(r'(<CATEGORYMEM index="0" category=")\d+(")',
                             r'\g<1>%d\g<2>' % newcat, block, count=1)
                if new != block:
                    moved[0] += 1
                return new
        return block

    body = re.sub(r'<XDFTABLE\b.*?</XDFTABLE>\n', lambda m: fix(m.group(0)), body, flags=re.S)
    return body, moved[0]


def prune_and_renumber(cats_xml, body):
    """Drop categories with no members (Hayabusa-inherited leftovers) and compact-renumber the rest,
    rewriting every CATEGORYMEM reference. CATEGORYMEM category="N" is 1-BASED (CATEGORY index N-1);
    category 0-index (root) is always kept."""
    used_idx = set(int(n) - 1 for n in re.findall(r'category="(\d+)"', body))  # value N -> index N-1
    used_idx.add(0)  # keep the TunerPro root category
    old = [(int(re.search(r'index="(0x[0-9A-Fa-f]+)"', c).group(1), 16), c)
           for c in re.findall(r'    <CATEGORY [^\n]*\n', cats_xml)]
    remap = {}  # old 0-based index -> new 0-based index
    new_cats = []
    for oldidx, line in old:
        if oldidx not in used_idx:
            continue
        newidx = len(new_cats)
        remap[oldidx] = newidx
        new_cats.append(re.sub(r'index="0x[0-9A-Fa-f]+"', 'index="0x%X"' % newidx, line))
    # rewrite each 1-based value V: old index V-1 -> new index -> new 1-based value
    body = re.sub(r'category="(\d+)"',
                  lambda m: 'category="%d"' % (remap[int(m.group(1)) - 1] + 1), body)
    return ''.join(new_cats), body, len(old) - len(new_cats)


# ---------------------------------------------------------------- scalar constants
SCALARS_JSON = os.path.join(ROOT, 'gsxr-1000/docs/scalars.json')


def load_scalars():
    import json
    if not os.path.exists(SCALARS_JSON):
        return []
    try:
        return json.load(open(SCALARS_JSON))
    except Exception:
        return []


# Native trace results (gsxr-1000/docs/traced.json): engine-RPM variable + scale, the map
# input variables resolved from the GSX-R's own lookup calls, and constants traced in the code.
# All derived from the GSX-R binary + Ghidra, NOT from the Hayabusa.
TRACED_JSON = os.path.join(ROOT, 'gsxr-1000/docs/traced.json')


def load_traced():
    import json
    try:
        t = json.load(open(TRACED_JSON))
    except Exception:
        return {}, {}, {}
    mi = {}
    for d, r in t.get('map_inputs', {}).items():
        mi[int(d, 16)] = r
    meaning = t.get('ram_meaning', {})
    consts = {}
    for a, title in t.get('constants', {}).items():
        consts[int(a, 16)] = title
    # attach meaning lookups onto each map's inputs
    for d, r in mi.items():
        r['_meaning'] = meaning
    return mi, consts, meaning


def traced_inputs_line(desc_addr, traced_map):
    r = traced_map.get(desc_addr)
    if not r:
        return ''
    meaning = r.get('_meaning', {})
    bits = []
    for role in ('x', 'y'):
        if role in r:
            ram = r[role]
            m = meaning.get(ram, '')
            bits.append('%s = %s%s' % (role.upper(), ram, (' (%s)' % m) if m else ''))
    return ('GSX-R TRACED INPUTS (from this ECU\'s lookup calls): %s.' % '; '.join(bits)) if bits else ''


SCALAR_CONST = '''  <XDFCONSTANT uniqueid="0x%(uid)X" flags="0x0">
    <title>%(title)s</title>
    <description>%(desc)s</description>
    <CATEGORYMEM index="0" category="%(cat)d" />
    <EMBEDDEDDATA mmedtypeflags="0x02" mmedaddress="0x%(addr)X" mmedelementsizebits="%(bits)d" mmedmajorstridebits="0" mmedminorstridebits="0" />
    <units>raw</units>
    <decimalpl>0</decimalpl>
    <datatype>0</datatype>
    <unittype>0</unittype>
    <DALINK index="0" />
    <MATH equation="X"><VAR id="X" /></MATH>
  </XDFCONSTANT>
'''
SCALAR_FLAG = '''  <XDFFLAG uniqueid="0x%(uid)X">
    <title>%(title)s</title>
    <description>%(desc)s</description>
    <CATEGORYMEM index="0" category="%(cat)d" />
    <EMBEDDEDDATA mmedaddress="0x%(addr)X" mmedelementsizebits="8" mmedmajorstridebits="0" mmedminorstridebits="0" />
    <mask>0x80</mask>
  </XDFFLAG>
'''


# Map a context map title to a short, reliable subsystem tag (from the reading function).
SUBSYS = [
    ('Launch Control', 'Launch Control'), ('Quickshifter', 'Quickshifter'),
    ('TC -', 'Traction Control'), ('Traction', 'Traction Control'),
    ('Rev Limiter', 'Rev/Speed Limiter'), ('Per-Gear Limiter', 'Rev/Speed Limiter'),
    ('Anti-Lift', 'Anti-Lift'), ('Pitch', 'Anti-Lift'), ('Cruise', 'Cruise Control'),
    ('ETV', 'Throttle/ETV'), ('Throttle', 'Throttle/ETV'), ('PWR', 'Throttle/ETV'),
    ('Ignition', 'Ignition'), ('Fuel', 'Fuel'), ('Accel Enrich', 'Fuel'),
    ('Injector', 'Fuel'), ('Idle', 'Idle/Fan'), ('Fan', 'Idle/Fan'),
    ('HO2', 'O2/Closed-Loop'), ('Closed Loop', 'O2/Closed-Loop'),
    ('Sensor', 'Sensors'), ('Speed Monitor', 'Speed/Wheel'), ('Wheel', 'Speed/Wheel'),
    ('IMU', 'IMU/Chassis'), ('Lean', 'IMU/Chassis'), ('Gear', 'Gear'),
    ('DTC', 'Diagnostics'), ('Monitor', 'Diagnostics'), ('EVAP', 'Diagnostics'),
    ('Engine Brake', 'Engine Brake'), ('Ride Mode', 'Ride Modes'),
]


def subsystem(ctx):
    """Reliable subsystem tag from the context-map titles (the function's named maps), or ''."""
    for title in ctx:
        for key, tag in SUBSYS:
            if key.lower() in title.lower():
                return tag
    return ''


def scalar_blocks(b, scalars, cat, sw, name2idx=None):
    """Emit XDFCONSTANT/XDFFLAG for each decompiler-discovered scalar, valued from this read.

    Where the reading function also reads a named (Hayabusa-ported) map, the scalar's title is
    prefixed with that subsystem - a reliable area tag from the decompile, not a value guess - and
    the scalar is filed under that subsystem's "Scalars - X" folder (falling back to the generic
    decompiler-scalar category when the tag has no dedicated folder).
    """
    name2idx = name2idx or {}

    def scalar_cat(sub):
        return name2idx.get(SCALAR_CAT_NAME.get(sub, ''), cat)

    out = []
    uid = 0x100000
    tagged = 0
    for s in scalars:
        addr = s['addr']
        bits = s['width'] * 8
        val = int.from_bytes(b[addr:addr + s['width']], 'little')
        # a code-traced constant: emit with its real name + evidence, skip the generic path
        if addr in TRACED_CONSTS:
            desc = ('TRACED FROM GSX-R CODE: %s. VALUE %s: %d (raw). Confirm the exact engage '
                    'point on a bench before relying on it.' % (TRACED_CONSTS[addr], sw, val))
            out.append(SCALAR_CONST % dict(uid=uid, title=escape(TRACED_CONSTS[addr][:60]),
                                           desc=escape(desc), cat=cat, addr=addr, bits=bits))
            uid += 1
            continue
        ctx = (s.get('context') or [])[:2]
        sub = subsystem(s.get('context') or [])
        if sub:
            tagged += 1
        thiscat = scalar_cat(sub)
        pre = ('%s :: ' % sub) if sub else ''
        ctx_line = (' Near maps: %s.' % '; '.join(ctx)) if ctx else ''
        func = (' fn %s' % s['func']) if s.get('func') else ''
        is_flag = s.get('is_flag') and (b[addr] & 0x7f) == 0  # a clean 0x80/0x00 toggle in THIS read
        if is_flag:
            desc = ('Decompiler-found flag (UNVERIFIED): 0x80 toggle read by ECU code '
                    '(%d ref/%d fn%s). %s: 0x%02X.%s'
                    % (s['refs'], s['nfuncs'], func, sw, b[addr], ctx_line))
            out.append(SCALAR_FLAG % dict(uid=uid, title=escape('%sFlag @0x%X (bit7)' % (pre, addr)),
                                          desc=escape(desc), cat=thiscat, addr=addr))
        else:
            desc = ('Decompiler-found scalar (UNVERIFIED): u%d read by ECU code (%d ref/%d fn%s). '
                    'VALUE %s: %d.%s'
                    % (bits, s['refs'], s['nfuncs'], func, sw, val, ctx_line))
            out.append(SCALAR_CONST % dict(uid=uid,
                                           title=escape('%sScalar @0x%X (u%d)' % (pre, addr, bits)),
                                           desc=escape(desc), cat=thiscat, addr=addr, bits=bits))
        uid += 1
    return out, uid - 0x100000, tagged


# ---------------------------------------------------------------- generate
TRACED_MAP = {}
TRACED_CONSTS = {}


def generate(binpath, outpath, sw, part):
    global SW, TRACED_MAP, TRACED_CONSTS
    SW = sw
    TRACED_MAP, TRACED_CONSTS, _ = load_traced()
    b = open(binpath, 'rb').read()
    ref = open(HAYA_REF_BIN, 'rb').read()
    mb = master_blocks()
    ml = map_links()

    gd = scan(b)
    hd = scan(ref)
    for h in hd:
        h['m'] = mb.get(h['a'])
        h['ml'] = ml.get(h['a'])

    hs = [(h['t'], h['c'], h['r']) for h in hd]
    gs = [(g['t'], g['c'], g['r']) for g in gd]
    g2h = {}
    for ai, bi, size in difflib.SequenceMatcher(a=hs, b=gs, autojunk=False).get_matching_blocks():
        for k in range(size):
            g2h[bi + k] = ai + k

    cats_xml, UNMATCHED, SCALARCAT, NAME2VAL = category_block()

    stats = dict(HIGH=0, MED=0, GENERIC=0)
    blocks = []
    uid = 0x4000
    for gi, d in enumerate(gd):
        hi = g2h.get(gi)
        m = hd[hi]['m'] if hi is not None else None
        if m is not None:
            # confidence by axis-byte identity
            hh = hd[hi]
            xb = axis_info(m['block'], 'x')
            xbits = xb['bits'] if xb else 16
            same_x = read_axis(b, d['xp'], d['c'], xbits) == read_axis(ref, hh['xp'], hh['c'], xbits)
            same_y = True
            if d['r'] > 0:
                yb = axis_info(m['block'], 'y')
                ybits = yb['bits'] if yb else 16
                same_y = read_axis(b, d['yp'], d['r'], ybits) == read_axis(ref, hh['yp'], hh['r'], ybits)
            conf = 'HIGH' if (same_x and same_y) else 'MED'
            blocks.append(ported_block(b, d, m, conf, sw, hd[hi].get('ml')))
            stats[conf] += 1
        else:
            blocks.append(generic_block(b, d, uid, UNMATCHED))
            uid += 1
            stats['GENERIC'] += 1

    # decompiler-discovered scalar constants / flags (code cross-reference analysis)
    scalars = load_scalars()
    sblocks, nscalar, ntagged = scalar_blocks(b, scalars, SCALARCAT, sw, NAME2VAL)
    blocks.extend(sblocks)

    deftitle = 'Suzuki GSX-R1000 M7 %s (%s) - ported from Hayabusa Gen3 (auto)' % (sw, part)
    desc = ('Suzuki GSX-R1000 M7 (RH850), 2 MB read, sw %s (ECM %s). %d maps auto-ported from '
            'Hayabusa Gen3 via on-bin descriptors (%d HIGH, %d MED=verify, %d unknown) + %d '
            'scalars/flags found by Ghidra V850 decompile (generic titles + context hints, '
            'UNVERIFIED). Scaling is the Hayabusa\'s, unverified here. Re-stamp field-1 CRC '
            '(0x10000-0x1FFAFB @0x1FFAFE) with tools/fix_field1_crc.py. UNVERIFIED ON HARDWARE.'
            % (sw, part, len(gd), stats['HIGH'], stats['MED'], stats['GENERIC'], nscalar))

    body = ''.join(blocks)
    # re-file the decoded maps the Hayabusa master mis-categorised so folder names match contents
    body, nmoved = recategorize(body, NAME2VAL)
    # relabel the decompile-confirmed steering-damper maps/flag into their own folder
    body, ndamper = label_damper(body, NAME2VAL)
    # drop categories with no members (Hayabusa-inherited empty folders) and compact-renumber
    cats_xml, body, npruned = prune_and_renumber(cats_xml, body)

    header = '''<!-- Written by make_gsxr_xdf.py - GSX-R1000 M7, ported from Hayabusa Gen3 -->
<XDFFORMAT version="1.70">
  <XDFHEADER>
    <flags>0x1</flags>
    <deftitle>%s</deftitle>
    <description>%s</description>
    <author>Clint Chipley / Claude</author>
    <BASEOFFSET offset="0" subtract="0" />
    <DEFAULTS datasizeinbits="8" sigdigits="2" outputtype="1" signed="0" lsbfirst="1" float="0" />
    <REGION type="0xFFFFFFFF" startaddress="0x0" size="0x200000" regioncolor="0x0" regionflags="0x0" name="Binary File" desc="2 MB full read" />
%s  </XDFHEADER>
''' % (escape(deftitle), escape(desc), cats_xml)

    with open(outpath, 'w') as f:
        f.write(header)
        f.write(body)
        f.write('</XDFFORMAT>\n')
    return stats, len(gd), nscalar, npruned


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    _, binpath, outpath, sw, part = sys.argv
    st, n, nsc, npruned = generate(binpath, outpath, sw, part)
    print('%s: %d descriptors + %d scalars -> %s'
          % (os.path.basename(binpath), n, nsc, os.path.basename(outpath)))
    print('   HIGH=%(HIGH)d  MED=%(MED)d  GENERIC=%(GENERIC)d' % st)
    print('   pruned %d empty categories' % npruned)
