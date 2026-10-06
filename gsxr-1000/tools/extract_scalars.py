#!/usr/bin/env python3
"""Recover GSX-R scalar constants/flags from a Ghidra V850 decompilation and write scalars.json.

Pipeline (see gsxr-1000/README.md "Decompilation"):
  1. Analyse a read in Ghidra headless with processor V850:LE:32:default, base 0x0, and the
     postscript tools/DumpCalXrefs.py -> a TSV of every code->calibration (0x150000-0x1B0000)
     reference: from_addr, to_addr, refType, mnemonic, containing_function.
  2. Do the same for the Hayabusa reference read (stock/5JCZSJ40) -> its TSV.
  3. Run this script. A "scalar" is a calibration address that ECU code loads/stores but that is
     NOT inside any map descriptor's data/axes span. Validated on the Hayabusa: this recovers 96%
     of the master's known constants/flags (addresses outside descriptor spans) with ~99% in-region
     recall. Each GSX-R scalar gets a context hint: the named (Hayabusa-ported) maps that the same
     function also reads.

usage: python3 extract_scalars.py <gsxr_calxrefs.tsv> <haya_calxrefs.tsv> <gsxr.bin> <out.json>
"""
import os, re, sys, json, difflib
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from make_gsxr_xdf import scan, HAYA_MASTER, HAYA_REF_BIN, ZBITS  # reuse the validated scanner

LO, HI = 0x150000, 0x1B0000
LOADW = {'ld.bu': 1, 'ld.b': 1, 'sld.bu': 1, 'sld.b': 1, 'ld.hu': 2, 'ld.h': 2, 'sld.hu': 2,
         'sld.h': 2, 'ld.w': 4, 'sld.w': 4}
STOREW = {'st.w': 4, 'sst.w': 4, 'st.h': 2, 'st.b': 1, 'sst.h': 2, 'sst.b': 1}


def spans(b):
    ds = scan(b)
    cov = set()
    dspan = {}
    for d in ds:
        a0, c, r, xp, yp, dp, t = d['a'], d['c'], d['r'], d['xp'], d['yp'], d['dp'], d['t']
        for a in range(a0, a0 + 20):
            cov.add(a)
        for a in range(xp, xp + c * 2):
            cov.add(a)
        if r > 0:
            for a in range(yp, yp + r * 2):
                cov.add(a)
            z, n = dp, r * c
        else:
            z, n = yp, c
        for a in range(z, z + n * (ZBITS[t] // 8)):
            cov.add(a)
        dspan[a0] = (min(xp, z, a0), max(xp + c * 2, z + n * (ZBITS[t] // 8)))
    return ds, cov, dspan


def load_xrefs(path):
    tgt = defaultdict(lambda: dict(refs=0, w=Counter(), funcs=Counter(), load=0, store=0))
    f2t = defaultdict(set)
    for ln in open(path):
        p = ln.rstrip('\n').split('\t')
        if len(p) < 2:
            continue
        to = int(p[1], 16)
        mn = p[3] if len(p) > 3 else ''
        fe = p[4] if len(p) > 4 and p[4] != '-' else None
        d = tgt[to]
        d['refs'] += 1
        if mn in LOADW:
            d['load'] += 1
            d['w'][LOADW[mn]] += 1
        elif mn in STOREW:
            d['store'] += 1
            d['w'][STOREW[mn]] += 1
        if fe:
            fe = int(fe, 16)
            d['funcs'][fe] += 1
            f2t[fe].add(to)
    return tgt, f2t


def scalars(cov, tgt):
    return {t: d for t, d in tgt.items()
            if LO <= t < HI and t not in cov and (d['load'] or d['store'])}


def main():
    gx, hx, gbin, out = sys.argv[1:5]
    HAYA = open(HAYA_REF_BIN, 'rb').read()
    GSXR = open(gbin, 'rb').read()
    hds, hcov, hdspan = spans(HAYA)
    gds, gcov, gdspan = spans(GSXR)
    htgt, hf2t = load_xrefs(hx)
    gtgt, gf2t = load_xrefs(gx)
    hsc, gsc = scalars(hcov, htgt), scalars(gcov, gtgt)

    txt = open(HAYA_MASTER).read()
    mc = set()
    for m in re.finditer(r'  <XDF(CONSTANT|FLAG) uniqueid=.*?</XDF\1>\n', txt, re.S):
        em = re.search(r'mmedaddress="0x([0-9A-Fa-f]+)"', m.group(0))
        if em:
            mc.add(int(em.group(1), 16))
    hit = sum(1 for t in hsc if t in mc)
    print('Hayabusa validation: %d scalars, %d match known master const/flag (%d%% precision)'
          % (len(hsc), hit, 100 * hit // max(1, len(hsc))))

    # named-map context: gsxr desc -> ported title; gsxr func -> set of those titles
    def axb(b, p, n):
        return bytes(b[p:p + n * 2])
    hs = [(d['t'], d['c'], d['r']) for d in hds]
    gs = [(d['t'], d['c'], d['r']) for d in gds]
    h2g = {}
    for ai, bi, size in difflib.SequenceMatcher(a=hs, b=gs, autojunk=False).get_matching_blocks():
        for k in range(size):
            h2g[ai + k] = bi + k
    mtitle = {}
    for m in re.finditer(r'  <XDFTABLE uniqueid=.*?</XDFTABLE>\n', txt, re.S):
        dref = re.search(r'descriptor @0x([0-9A-Fa-f]+)', m.group(0))
        ti = re.search(r'<title>(.*?)</title>', m.group(0), re.S)
        if dref and ti:
            mtitle[int(dref.group(1), 16)] = ti.group(1)
    gdesc_title = {}
    for ai, bi in h2g.items():
        ti = mtitle.get(hds[ai]['a'])
        if ti:
            gdesc_title[gds[bi]['a']] = ti
    gfunc_maps = defaultdict(set)
    for fe, ts in gf2t.items():
        for t in ts:
            for da, (lo, hi) in gdspan.items():
                if lo <= t < hi and da in gdesc_title:
                    gfunc_maps[fe].add(gdesc_title[da])
                    break

    recs = []
    for t in sorted(gsc):
        d = gsc[t]
        wid = d['w'].most_common(1)[0][0] if d['w'] else 1
        val = int.from_bytes(GSXR[t:t + wid], 'little')
        topf = d['funcs'].most_common(1)[0][0] if d['funcs'] else None
        ctx = set()
        for fe, _ in d['funcs'].most_common():
            ctx |= gfunc_maps.get(fe, set())
        recs.append(dict(addr=t, width=wid, value=val, refs=d['refs'], load=d['load'],
                         store=d['store'], nfuncs=len(d['funcs']),
                         func=('0x%06X' % topf if topf else ''), context=sorted(ctx)[:3],
                         is_flag=(wid == 1 and val in (0, 1, 0x80, 0xff))))
    json.dump(recs, open(out, 'w'))
    print('GSX-R scalars: %d (%d with a named-map context hint) -> %s'
          % (len(recs), sum(1 for r in recs if r['context']), out))


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    main()
