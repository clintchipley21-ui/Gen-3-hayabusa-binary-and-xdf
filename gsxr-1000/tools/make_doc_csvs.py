#!/usr/bin/env python3
"""Regenerate docs/map-inputs.csv and docs/variables.csv from docs/traced.json + the base read, so
the documentation always matches the traced state the XDF is built from. Run after updating
traced.json:  python3 tools/make_doc_csvs.py
"""
import os, re, csv, json, collections, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, 'M7', '32990-48L00.bin')
TRACED = os.path.join(ROOT, 'docs', 'traced.json')

spec = importlib.util.spec_from_file_location('mk', os.path.join(ROOT, 'tools', 'make_gsxr_xdf.py'))
mk = importlib.util.module_from_spec(spec); spec.loader.exec_module(mk)


def main():
    b = open(BIN, 'rb').read()
    descs = {d['a']: d for d in mk.scan(b)}
    t = json.load(open(TRACED))
    mi = {int(k, 16): v for k, v in t['map_inputs'].items()}
    meaning = t.get('ram_meaning', {})

    # ---- map-inputs.csv : one row per traced map, with dims + resolved X/Y var and meaning ----
    rows = []
    for a in sorted(mi):
        d = descs.get(a)
        dims = ('%dx%d' % (d.get('c', 0) or 0, d.get('r', 0) or 0)) if d else '?'
        r = mi[a]
        xr = r.get('x', ''); yr = r.get('y', '')
        rows.append(['0x%06X' % a, dims, xr, meaning.get(xr, ''), yr, meaning.get(yr, '')])
    with open(os.path.join(ROOT, 'docs', 'map-inputs.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['descriptor', 'dims', 'x_ram', 'x_meaning', 'y_ram', 'y_meaning'])
        w.writerows(rows)

    # ---- variables.csv : every RAM var used as a map axis, how many maps it feeds, and its role ----
    fed = collections.Counter(); axis_roles = collections.defaultdict(collections.Counter)
    for a, r in mi.items():
        for role in ('x', 'y'):
            if role in r:
                fed[r[role]] += 1; axis_roles[r[role]][role] += 1
    var = []
    for ram in sorted(fed, key=lambda k: -fed[k]):
        var.append([ram, fed[ram], meaning.get(ram, '(unlabelled)'),
                    '', json.dumps(dict(axis_roles[ram]))])
    with open(os.path.join(ROOT, 'docs', 'variables.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['ram_addr', 'maps_fed', 'role', 'detail', 'axis_roles'])
        w.writerows(var)

    print('map-inputs.csv: %d rows | variables.csv: %d vars' % (len(rows), len(var)))


if __name__ == '__main__':
    main()
