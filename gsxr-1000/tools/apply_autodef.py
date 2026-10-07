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
TRACED_TAG = 'ROLE-TRACED'

# a generator-generic title we are allowed to overwrite (never touch hand-named / role-traced items)
GENERIC = re.compile(r'^(?:[^:]+ :: )?(?:Scalar|Flag|Constant) @0x[0-9A-Fa-f]+|^Option .* bit\d|^Unknown ')


def role_title(addr, info):
    # prefer the INFERRED (educated-guess) title when one was generated; else the bare role title
    if info.get('inferred_title'):
        return info['inferred_title']
    pre = ('%s :: ' % info['sub']) if info.get('sub') else ''
    return '%s%s @0x%06X' % (pre, ROLE_TITLE.get(info['role'], 'Item'), addr)


def role_desc(addr, info, keep_tail):
    conf = info['conf']
    detail = info['detail']
    who = (' Read by %s%s.' % (info['func'], (' (%s)' % info['sub']) if info.get('sub') else '')) \
        if info.get('func') else ''
    code = ('\nCODE: %s' % info['code']) if info.get('code') else ''
    if info.get('inferred_title'):
        head = ('INFERRED (educated guess, NOT code-proven): name derived from the traced role'
                '%s plus the variable in the code line below; verify before trusting. '
                'Underlying role trace (confidence %s): %s.%s%s'
                % (' and the nearest named subsystem by address' if 'proximity' in info['inferred_title'] else '',
                   conf, detail, who, code))
    else:
        head = ('%s (confidence %s): %s.%s%s' % (TRACED_TAG, conf, detail, who, code))
    return head + ('\n\n' + keep_tail if keep_tail else '')


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
        tail = ''
        if dm:
            mt = re.search(r'(STOCK|VALUES|Bit |Ticked)\b.*', dm.group(1), re.S)
            if mt:
                tail = mt.group(0).strip()
        nd = 'CURATED (code-proven): ' + cd + ('\n\n' + tail if tail else '')
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
    # keep the stock-value tail of the old description (everything from "STOCK"/"VALUES"/"Bit " on)
    dm = re.search(r'<description>(.*?)</description>', blk, re.S)
    tail = ''
    if dm:
        old = dm.group(1)
        mt = re.search(r'(STOCK|VALUES|Bit |Ticked)\b.*', old, re.S)
        if mt:
            tail = mt.group(0).strip()
    nt = role_title(addr, info)
    nd = role_desc(addr, info, tail)
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
    nd = 'CURATED (code-proven): ' + cd + ('\n\n' + tail if tail else '')
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
    open(path, 'w').write(x)
    print('%s: role-traced %d constants/flags, %d curated tables, renamed %d Unknown tables' % (
        os.path.relpath(path, ROOT), n, nc_tab, nt_tab))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1])
