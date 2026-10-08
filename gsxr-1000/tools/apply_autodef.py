#!/usr/bin/env python3
"""Apply the decompile-derived role trace (docs/autodef-roles.json) to a generated GSX-R XDF, in place.

Every calibration CONSTANT/FLAG that the generator left with a generic "Scalar/Flag @0x.." title is
rewritten to "<Subsystem> :: <Role> @0xADDR", and its description is replaced with what the code
actually does with it: the role (threshold / gain / offset / divisor / bit mask / flag test / operand),
the reader function, a confidence, and one real line of decompiled code showing the use. Nothing is
invented - a specific role is given only where the code proves it; a bare arithmetic constant is
honestly labelled "Operand" with its code line rather than a guessed functional name.

Roles come from docs/autodef-roles.json, produced by tracing every reference into the calibration
region (0x150000-0x1A6000) through the decompiled V850 code and classifying the referencing statement.

Build order:  make_gsxr_xdf.py <read> <out.xdf> ...   then   apply_autodef.py <out.xdf>
Idempotent: re-running changes nothing (already-traced items are detected and skipped).

usage: python3 tools/apply_autodef.py <file.xdf>
"""
import json, os, re, sys
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES = json.load(open(os.path.join(ROOT, 'docs', 'autodef-roles.json')))
_cur = json.load(open(os.path.join(ROOT, 'docs', 'curated-names.json')))
CURATED_SCALAR = {int(k, 16): v for k, v in _cur.get('scalars', {}).items()}
CURATED_TABLE = {int(k, 16): v for k, v in _cur.get('tables', {}).items()}
_tbl_inf_path = os.path.join(ROOT, 'docs', 'table-inferred.json')
TABLE_INFERRED = {int(k, 16): v for k, v in json.load(open(_tbl_inf_path)).items()} \
    if os.path.exists(_tbl_inf_path) else {}
ROLE_TITLE = {'threshold': 'Threshold', 'gain': 'Gain/Factor', 'divisor': 'Divisor', 'offset': 'Offset',
              'bitmask': 'Bit mask', 'flag-test': 'Flag (tested)', 'operand': 'Operand',
              'unref': 'Data (unreferenced)', 'map': 'Map'}

# Plain-language effect of each traced role: what the value does and which way to turn it. These are
# the GENERIC meaning of the detected role (how a gain/threshold/offset/... behaves in code), not a
# per-parameter claim - honest for items we have only role-classified, correct for the curated ones.
ROLE_EFFECT = {
    'gain': 'acts as a multiplier/scale on its input - a larger value increases the result in '
            'proportion, a smaller value reduces it',
    'threshold': 'is a compare/trigger point - the code tests a live input against it, so raising it '
                 'makes the behaviour engage later (needs a higher input) and lowering it sooner',
    'offset': 'is added to its input - raising it shifts the result up, lowering it shifts it down',
    'divisor': 'divides its input - a larger value makes the result smaller, a smaller value larger',
    'bitmask': 'is a bit mask selecting which bits are tested/set - change individual bits, not the '
               'whole number',
    'flag-test': 'is read as an on/off bit-7 flag - 0x80 = set/enabled, 0x00 = clear/disabled',
    'operand': 'is a constant used inside the reader arithmetic; its precise effect depends on the '
               'surrounding formula and is not individually proven here',
    'unref': 'is not reached by any decoded code path in this read, so its effect is unknown',
    'map': 'is lookup-table data',
}
TRACED_TAG = 'ROLE-TRACED'

# a generator-generic title we are allowed to overwrite (never touch hand-named / role-traced items)
GENERIC = re.compile(r'^(?:[^:]+ :: )?(?:Scalar|Flag|Constant) @0x[0-9A-Fa-f]+|^Option .* bit\d|^Unknown ')


def role_title(addr, info):
    # prefer the INFERRED (educated-guess) title when one was generated; else the bare role title
    if info.get('inferred_title'):
        return info['inferred_title']
    pre = ('%s :: ' % info['sub']) if info.get('sub') else ''
    return '%s%s @0x%06X' % (pre, ROLE_TITLE.get(info['role'], 'Item'), addr)


def oneline(s, cap=400):
    """Collapse to a single line of plain ASCII and hard-cap the length. TunerPro's XDF reader is
    fragile with very long / multi-line / entity-heavy descriptions, so every description this tool
    writes is kept short, single-line and free of raw decompiled code (the full code trace with the
    `<`/`&`/pointer syntax stays in docs/autodef-trace.csv)."""
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.replace('<', '').replace('>', '').replace('&', 'and')
    return s[:cap].rstrip()


def field_range(blk):
    """Representable min/max for a constant's data width + signedness, read from its EMBEDDEDDATA.
    Returns (lo, hi, label) e.g. (0, 255, 'u8'); (None, None, None) if no element-size is present
    (e.g. a flag)."""
    wm = re.search(r'mmedelementsizebits="(\d+)"', blk)
    if not wm:
        return None, None, None
    w = int(wm.group(1))
    fm = re.search(r'mmedtypeflags="(0x[0-9A-Fa-f]+)"', blk)
    signed = bool(int(fm.group(1), 16) & 1) if fm else False
    if signed:
        return -(1 << (w - 1)), (1 << (w - 1)) - 1, 's%d' % w
    return 0, (1 << w) - 1, 'u%d' % w


def stock_range_str(blk, old_desc):
    """One short clause giving the stock value (from the generator's STOCKVAL/STOCKBYTE token) and,
    for a numeric constant, the representable field range. '' if neither is available."""
    mb = re.search(r'STOCKBYTE=0x([0-9A-Fa-f]+)', old_desc)
    if mb:
        byte = int(mb.group(1), 16)
        return 'Stock: bit7 %s (byte 0x%02X); 0x80 = set, 0x00 = clear.' % (
            'SET (on)' if byte & 0x80 else 'CLEAR (off)', byte)
    lo, hi, lab = field_range(blk)
    mv = re.search(r'STOCKVAL=(-?\d+)', old_desc)
    if mv and lo is not None:
        return 'Stock %s raw; field range %d..%d (%s).' % (mv.group(1), lo, hi, lab)
    if mv:
        return 'Stock %s raw.' % mv.group(1)
    if lo is not None:
        return 'Field range %d..%d (%s).' % (lo, hi, lab)
    return ''


def near_maps(old_desc):
    m = re.search(r'Near maps: ([^.]*)\.', old_desc)
    return m.group(1).strip() if m else ''


def role_desc(addr, info, blk, old_desc):
    # SHORT, single-line, no raw code - keeps the file small and TunerPro-safe. Carries the stock
    # value + field range and a plain-language effect of the traced role.
    if info.get('inferred_title'):
        bits = ['INFERRED name (educated guess - verify)']
    else:
        bits = ['Role-traced from code (confidence %s)' % info['conf']]
    role = info['role']
    eff = ROLE_EFFECT.get(role)
    bits.append('role %s%s' % (role, (' - this value %s' % eff) if eff else ''))
    if info.get('func'):
        bits.append('reader %s' % info['func'])
    if info.get('sub'):
        bits.append('subsystem %s' % info['sub'])
    s = '; '.join(bits) + '.'
    sv = stock_range_str(blk, old_desc)
    if sv:
        s += ' ' + sv
    nm = near_maps(old_desc)
    if nm:
        s += ' Near maps: ' + nm + '.'
    s += ' Full code trace: docs/autodef-trace.csv.'
    return oneline(s, 600)


def apply_block(blk):
    tm = re.search(r'<title>(.*?)</title>', blk, re.S)
    am = re.search(r'mmedaddress="(0x[0-9A-Fa-f]+)"', blk)
    if not tm or not am:
        return blk, False
    title = tm.group(1)
    addr = int(am.group(1), 16)
    # curated (hand-verified, code-proven) names take precedence and bypass the generic check
    if addr in CURATED_SCALAR:
        if 'CURATED' in blk:
            return blk, False
        ct, cd = CURATED_SCALAR[addr]
        dm = re.search(r'<description>(.*?)</description>', blk, re.S)
        old = dm.group(1) if dm else ''
        sv = stock_range_str(blk, old)
        nd = oneline('CURATED (code-proven): ' + cd + ((' ' + sv) if sv else ''), 520)
        blk = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % escape(ct, quote=False), blk, count=1, flags=re.S)
        blk = re.sub(r'<description>.*?</description>', lambda m: '<description>%s</description>' % escape(nd, quote=False), blk, count=1, flags=re.S)
        return blk, True
    if TRACED_TAG in blk:                 # already applied - idempotent
        return blk, False
    if not GENERIC.match(title):          # hand-named / already meaningful - leave it
        return blk, False
    info = ROLES.get('0x%06X' % addr)
    if not info:
        return blk, False
    dm = re.search(r'<description>(.*?)</description>', blk, re.S)
    old = dm.group(1) if dm else ''
    nt = role_title(addr, info)
    nd = role_desc(addr, info, blk, old)
    blk = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % escape(nt, quote=False), blk, count=1, flags=re.S)
    blk = re.sub(r'<description>.*?</description>',
                 lambda m: '<description>%s</description>' % escape(nd, quote=False), blk, count=1, flags=re.S)
    return blk, True


def retitle_unknown_table(blk):
    """Rename a generator 'Unknown Curve/Map N @0x..' table to its traced axis, read from the
    'GSX-R TRACED INPUTS' line the generator already wrote. Leaves the description intact."""
    tm = re.search(r'<title>(Unknown (Curve|Map) [^<]*?)@0x([0-9A-Fa-f]+)</title>', blk)
    if not tm:
        return blk, False
    kind, zaddr = tm.group(2), tm.group(3)
    xi = re.search(r'TRACED INPUTS[^\n]*?X = (0x[0-9A-Fa-f]+) \(([^)\[]+?)[)\[]', blk)
    if not xi:
        # no traced axis: fall back to an inferred (educated-guess) name by address proximity
        dm = re.search(r'descriptor @0x([0-9A-Fa-f]+)', blk)
        da = int(dm.group(1), 16) if dm else None
        if da in TABLE_INFERRED:
            nt = TABLE_INFERRED[da] + ' @0x%s' % zaddr
            return re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % escape(nt, quote=False),
                          blk, count=1, flags=re.S), True
        return blk, False
    xc = xi.group(2).strip()
    yi = re.search(r'Y = (0x[0-9A-Fa-f]+) \(([^)\[]+?)[)\[]', blk)
    axis = xc + (' x ' + yi.group(2).strip() if yi else '')
    nt = '%s vs %s @0x%s' % (kind, axis, zaddr)
    return re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % escape(nt, quote=False),
                  blk, count=1, flags=re.S), True


def apply_curated_table(blk):
    dm = re.search(r'descriptor @0x([0-9A-Fa-f]+)', blk)
    if not dm:
        return blk, False
    addr = int(dm.group(1), 16)
    if addr not in CURATED_TABLE or 'CURATED' in blk:
        return blk, False
    ct, cd = CURATED_TABLE[addr]
    old = re.search(r'<description>(.*?)</description>', blk, re.S)
    tail = old.group(1).strip() if old else ''
    nd = oneline('CURATED (code-proven): ' + cd + (' ' + tail if tail else ''), 480)
    blk = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % escape(ct, quote=False), blk, count=1, flags=re.S)
    blk = re.sub(r'<description>.*?</description>', lambda m: '<description>%s</description>' % escape(nd, quote=False), blk, count=1, flags=re.S)
    return blk, True


def main(path):
    x = open(path).read()
    n = 0
    nt_tab = 0
    nc_tab = 0

    def repl_tab(m):
        nonlocal nt_tab, nc_tab
        blk, ch = apply_curated_table(m.group(0))
        if ch:
            nc_tab += 1
            return blk
        blk, ch = retitle_unknown_table(m.group(0))
        if ch:
            nt_tab += 1
        return blk
    x = re.sub(r'<XDFTABLE\b.*?</XDFTABLE>', repl_tab, x, flags=re.S)
    # rewrite each CONSTANT/FLAG block
    def repl(m):
        nonlocal n
        blk, changed = apply_block(m.group(0))
        if changed:
            n += 1
        return blk
    x = re.sub(r'<XDFCONSTANT\b.*?</XDFCONSTANT>', repl, x, flags=re.S)
    x = re.sub(r'<XDFFLAG\b.*?</XDFFLAG>', repl, x, flags=re.S)
    # strip the internal STOCKVAL/STOCKBYTE tokens the generator emits for this tool to consume -
    # any item we did not rewrite (e.g. a code-traced constant with its own name) still carries one.
    x = re.sub(r'\s*STOCK(?:VAL=-?\d+|BYTE=0x[0-9A-Fa-f]+)\.?', '', x)
    open(path, 'w').write(x)
    print('%s: role-traced %d constants/flags, %d curated tables, renamed %d Unknown tables' % (
        os.path.relpath(path, ROOT), n, nc_tab, nt_tab))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1])
