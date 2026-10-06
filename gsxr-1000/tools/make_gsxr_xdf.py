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
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))              # repo root
HAYA_MASTER = os.path.join(ROOT, 'stock/master/master-v9.xdf')
HAYA_REF_BIN = os.path.join(ROOT, 'stock/5JCZSJ10/5JCZSJ10.bin')
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
HAYA_DECOMP = os.path.join(ROOT, 're/decompiled.zip')


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
    desc = ('AUTO-DISCOVERED from the ECU map descriptor; no Hayabusa map aligned here, role '
            'unknown - log before changing.\n%s\n%s\n%s'
            % (axes_line(b, d, None, None), values_line(b, d, None, SW), reference_line(d)))
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
    il = inputs_line(ml)
    if il:
        parts.append(il)
    parts += [values_line(b, d, zi, sw), reference_line(d)]
    return retitle(blk, title, '\n'.join(parts))


# ---------------------------------------------------------------- categories
def category_block():
    txt = open(HAYA_MASTER).read()
    cats = re.findall(r'    <CATEGORY index="0x[0-9A-Fa-f]+" name="[^"]*" />\n', txt)
    maxidx = max(int(re.search(r'index="(0x[0-9A-Fa-f]+)"', c).group(1), 16) for c in cats)
    unmatched = maxidx + 1
    cats.append('    <CATEGORY index="0x%X" name="ZZ Unmatched / Auto-discovered (verify)" />\n'
                % unmatched)
    return ''.join(cats), unmatched


# ---------------------------------------------------------------- generate
def generate(binpath, outpath, sw, part):
    global SW
    SW = sw
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

    cats_xml, UNMATCHED = category_block()

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

    deftitle = 'Suzuki GSX-R1000 M7 %s (%s) - ported from Hayabusa Gen3 (auto)' % (sw, part)
    desc = ('Suzuki GSX-R1000 (M7, Renesas RH850), full 2 MB read, software %s (ECM %s). '
            'Map/curve definitions AUTO-PORTED from the Gen-3 Hayabusa master by aligning this '
            'bin\'s own ECU map descriptors (%d found) to the Hayabusa\'s. %d maps carried over '
            'from the Hayabusa (%d HIGH = breakpoints identical, %d MED = verify), %d auto-'
            'discovered with unknown role. Units/scaling are the Hayabusa\'s and UNVERIFIED on '
            'this ECU. Scalar constants/flags are NOT included (no descriptor). Field-1 CRC-16 '
            '(0x10000-0x1FFAFB, big-endian at 0x1FFAFE) must be re-stamped with '
            'tools/fix_field1_crc.py after editing. UNVERIFIED ON HARDWARE - bench first.'
            % (sw, part, len(gd), stats['HIGH'] + stats['MED'], stats['HIGH'], stats['MED'],
               stats['GENERIC']))

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
        f.write(''.join(blocks))
        f.write('</XDFFORMAT>\n')
    return stats, len(gd)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    _, binpath, outpath, sw, part = sys.argv
    st, n = generate(binpath, outpath, sw, part)
    print('%s: %d descriptors -> %s' % (os.path.basename(binpath), n, os.path.basename(outpath)))
    print('   HIGH=%(HIGH)d  MED=%(MED)d  GENERIC=%(GENERIC)d' % st)
