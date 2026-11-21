#!/usr/bin/env python3
"""Build a maps/curves XDF for a Gen-3 Hayabusa read on the "other" software line
(5JCU* / 5JE0*) from the read's OWN on-bin map descriptors.

Why this is needed (and why the 5JCZ XDFs do NOT apply here): the 5JCU/5JE0 line is a
different build from the 5JCZ line the master XDF was made for. Its code is ~97% different
and its calibration descriptor table is relocated - only 202 of 748 descriptors sit at the
same address as 5JCZ, and a straight address copy misreads ~70% of tables. But every
Suzuki Gen-3 read carries a self-describing 20-byte map-descriptor table (type, cols, rows,
flag, little-endian X/Y/data pointers). This script:

  1. scans the TARGET read for its own descriptors (true addresses in this bin);
  2. scans the 5JCZSJ10 reference for its descriptors and attaches each one's named master
     definition (scaling, axis widths, title) from stock/master/master-v9.xdf;
  3. sequence-aligns the two descriptor lists by (type, cols, rows) in calibration order
     (748 of 749 align for 5JCU/5JE0);
  4. for each aligned target descriptor, reuses the master map's name + scaling but points
     every axis at the TARGET read's own pointers and recomputes the value range;
  5. descriptors with no 5JCZ counterpart become generic "Unknown Map/Curve" items.

HIGH = breakpoints byte-identical to the 5JCZ map (same map, confident). MED = aligned by
order but breakpoints differ (title is a strong guess - verify). The result contains only
the descriptor-backed maps/curves; the ~2,900 scalar constants/flags have no descriptor and
must come from a 5JCU/5JE0 Ghidra decompile (same two-phase approach as the GSX-R XDFs).

  usage: python3 tools/make_other_xdf.py TARGET.bin OUT.xdf SW PART
  e.g.   python3 tools/make_other_xdf.py stock/other/5JCUSJ40-full.bin \\
                 stock/other/5JCUSJ40-full.xdf 5JCUSJ40 32990-10L4

Note on 5JE0SJ00: the native read omits the front 64 KB, so address it with the 2 MB-padded
5JE0SJ00-2mb.bin (front filled with 0xFF; the field-1 CRC region 0x10000-0x1FFAFB is
unaffected). Re-stamp field-1 CRC after editing a read with tools/fix_field1_crc.py.
"""
import difflib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
# Reuse the proven descriptor scanner / master-parse / emit helpers from the GSX-R generator.
_G_PATH = os.path.join(ROOT, 'gsxr-1000', 'tools', 'make_gsxr_xdf.py')
_spec = importlib.util.spec_from_file_location('make_gsxr_xdf', _G_PATH)
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

REF_BIN = os.path.join(ROOT, 'hayabusa', 'stock', '5JCZSJ10', '5JCZSJ10.bin')
REF_SW = '5JCZSJ10'


def ported_block(b, d, m, conf, sw, ml=None):
    """Same address-swap + value recompute as the GSX-R porter, but worded for a same-model
    Hayabusa port (not cross-model to the GSX-R)."""
    blk = m['block']
    is2d = d['r'] > 0
    xi = G.axis_info(blk, 'x')
    yi = G.axis_info(blk, 'y') if is2d else None
    zi = G.axis_info(blk, 'z')
    blk, _ = G._set_axis_addr(blk, 'x', d['xp'])
    if is2d:
        blk, _ = G._set_axis_addr(blk, 'y', d['yp'])
        blk, _ = G._set_axis_addr(blk, 'z', d['dp'])
    else:
        blk, _ = G._set_axis_addr(blk, 'z', d['yp'])
    base = m['title']
    if conf == 'HIGH':
        head = ('PORTED FROM %s master (HIGH: breakpoints byte-identical to the 5JCZ map, same '
                'Gen-3 model, almost certainly the same map). Scaling/units carried over; the '
                'addresses and values are THIS read\'s own, taken from its on-bin descriptor table.'
                % REF_SW)
        title = base
    else:
        head = ('PORTED FROM %s master (MED: same type/size and aligned by calibration order, but '
                'breakpoints differ from 5JCZ - the title is a strong guess, VERIFY before trusting). '
                'Scaling/units carried over; addresses and values are this read\'s own.' % REF_SW)
        title = base + '  [UNCONFIRMED]'
    parts = [head, G.axes_line(b, d, xi, yi)]
    il = G.inputs_line(ml)
    if il:
        parts.append(il + '  (from the 5JCZ decompile; code offsets differ on this line - '
                          'treat the signal meaning as a hint, not a verified address).')
    parts += [G.values_line(b, d, zi, sw), G.reference_line(d)]
    return G.retitle(blk, title, '\n'.join(parts))


def generate(binpath, outpath, sw, part):
    with open(binpath, 'rb') as f:
        b = f.read()
    with open(REF_BIN, 'rb') as f:
        ref = f.read()
    if len(b) != 0x200000:
        raise SystemExit('target must be a 2 MB image (0x200000); got 0x%X. For 5JE0SJ00 use the '
                         '2 MB-padded 5JE0SJ00-2mb.bin.' % len(b))

    mb = G.master_blocks()
    ml = G.map_links()
    gd = G.scan(b)
    hd = G.scan(ref)
    for h in hd:
        h['m'] = mb.get(h['a'])
        h['ml'] = ml.get(h['a'])

    hs = [(h['t'], h['c'], h['r']) for h in hd]
    gs = [(g['t'], g['c'], g['r']) for g in gd]
    g2h = {}
    for ai, bi, size in difflib.SequenceMatcher(a=hs, b=gs, autojunk=False).get_matching_blocks():
        for k in range(size):
            g2h[bi + k] = ai + k

    cats_xml, UNMATCHED, SCALARCAT, NAME2VAL = G.category_block()

    stats = dict(HIGH=0, MED=0, GENERIC=0)
    blocks = []
    uid = 0x4000
    for gi, d in enumerate(gd):
        hi = g2h.get(gi)
        m = hd[hi]['m'] if hi is not None else None
        if m is not None:
            hh = hd[hi]
            xb = G.axis_info(m['block'], 'x')
            xbits = xb['bits'] if xb else 16
            same_x = G.read_axis(b, d['xp'], d['c'], xbits) == G.read_axis(ref, hh['xp'], hh['c'], xbits)
            same_y = True
            if d['r'] > 0:
                yb = G.axis_info(m['block'], 'y')
                ybits = yb['bits'] if yb else 16
                same_y = G.read_axis(b, d['yp'], d['r'], ybits) == G.read_axis(ref, hh['yp'], hh['r'], ybits)
            conf = 'HIGH' if (same_x and same_y) else 'MED'
            blocks.append(ported_block(b, d, m, conf, sw, hh.get('ml')))
            stats[conf] += 1
        else:
            blocks.append(G.generic_block(b, d, uid, UNMATCHED))
            uid += 1
            stats['GENERIC'] += 1

    body = ''.join(blocks)
    cats_xml, body, npruned = G.prune_and_renumber(cats_xml, body)
    cats_xml, body, nsplit = G.split_oversized_categories(cats_xml, body)
    body, nrenum = G.renumber_item_uniqueids(body)

    deftitle = 'Suzuki Hayabusa Gen3 %s (%s) - maps from on-bin descriptors (auto)' % (sw, part)
    desc = ('Suzuki Hayabusa Gen3 (RH850/F1L), 2 MB read, sw %s (ECM %s), "other" line (5JCU/5JE0). '
            '%d maps/curves built from THIS read\'s on-bin descriptor table (%d HIGH = breakpoints '
            'match 5JCZ, %d MED = verify, %d unknown), definitions ported from the 5JCZSJ10 master. '
            'NOT compatible with 5JCZ XDFs (different build; descriptors relocated). Scalar '
            'constants/flags are NOT included - they have no descriptor and need a 5JCU/5JE0 Ghidra '
            'decompile. Re-stamp field-1 CRC (0x10000-0x1FFAFB @0x1FFAFE) with tools/fix_field1_crc.py '
            'after editing. UNVERIFIED ON HARDWARE - keep a stock read for recovery.'
            % (sw, part, len(gd), stats['HIGH'], stats['MED'], stats['GENERIC']))

    header = ('<!-- Written by make_other_xdf.py - Hayabusa Gen3 other-line (5JCU/5JE0), '
              'maps from on-bin descriptors -->\n'
              '<XDFFORMAT version="1.70">\n'
              '  <XDFHEADER>\n'
              '    <flags>0x1</flags>\n'
              '    <deftitle>%s</deftitle>\n'
              '    <description>%s</description>\n'
              '    <author>Clint Chipley / Claude</author>\n'
              '    <BASEOFFSET offset="0" subtract="0" />\n'
              '    <DEFAULTS datasizeinbits="8" sigdigits="2" outputtype="1" signed="0" '
              'lsbfirst="1" float="0" />\n'
              '    <REGION type="0xFFFFFFFF" startaddress="0x0" size="0x200000" regioncolor="0x0" '
              'regionflags="0x0" name="Binary File" desc="2 MB full read" />\n'
              '%s  </XDFHEADER>\n' % (G.escape(deftitle), G.escape(desc), cats_xml))

    with open(outpath, 'w') as f:
        f.write(header)
        f.write(body)
        f.write('</XDFFORMAT>\n')
    return stats, len(gd), npruned, nsplit, nrenum


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    _, binpath, outpath, sw, part = sys.argv
    st, n, npruned, nsplit, nrenum = generate(binpath, outpath, sw, part)
    print('%s: %d descriptor maps -> %s' % (os.path.basename(binpath), n, os.path.basename(outpath)))
    print('   HIGH=%(HIGH)d  MED=%(MED)d  GENERIC=%(GENERIC)d' % st)
    print('   pruned %d empty categories; split %d overflow folders; renumbered %d uniqueids'
          % (npruned, nsplit, nrenum))
