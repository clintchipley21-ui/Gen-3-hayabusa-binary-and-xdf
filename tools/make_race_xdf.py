#!/usr/bin/env python3
"""Build the race-software XDF (v6) from the stock master XDF plus the race-specific definitions.

Race XDF v6 = everything in stock/master (v9.3: quickshifter decode, top-speed limiter, unit audit,
traced auto-defined items) + the definitions that only make sense on the SD bins, taken from the SD-v5
race XDF (race/old/SD-v5.xdf):
  - the 8 speed-density fuel maps (X = raw IAP ADC shown as kPa for the 3-bar sensor),
  - the ALS timing-retard and boost spark-retard maps (ex Trim B) and the boost-spark enable weight,
  - the SD description of the blend-threshold curve,
  - IAP / AP sensor gain and offset, the neutral/clutch fuel-map gate, the IAP circuit fault thresholds,
  - the 9 rolling anti-lag settings at 0xBF000 (not present in a stock bin).
Every VALUES / STOCK line is then recomputed from the SD-v4.1 bin, and items the race software changed
(versus stock 5JCZSJ40) are marked. TunerPro limits from make_stock_xdfs.py apply.

usage: python3 tools/make_race_xdf.py          (from the repo root)
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_stock_xdfs as ms  # noqa: E402
import xdf_userfriendly as uf  # noqa: E402
import xdf_patches as xp  # noqa: E402

ROOT = ms.ROOT
RACE_SRC = os.path.join(ROOT, 'race/old/SD-v5.xdf')
SD_BIN = os.path.join(ROOT, 'race/Busa-SD-v4.1.bin')
STOCK_J40 = os.path.join(ROOT, 'stock/5JCZSJ40/5JCZSJ40.bin')
OUT = os.path.join(ROOT, 'race/Busa-SD-v6.xdf')

# race-specific definitions, keyed by data address (tables: Z data address)
OVERRIDE_TABLES = {0x159BB8, 0x15E460, 0x162D08, 0x1675B0, 0x16BEB8, 0x16CAD4, 0x16D6F0, 0x16E30C,
                   0x188214, 0x188598, 0x1828C0, 0x154E20}
OVERRIDE_CONSTS = {0x18EF58, 0x18EF5A, 0x18EF5E, 0x18EF60, 0x182626, 0x1547E0, 0x1547E2}
ADD_CONSTS = {0xBF000, 0xBF001, 0xBF002, 0xBF004, 0xBF006, 0xBF008, 0xBF00A, 0xBF00C, 0xBF00E}

HEADER = ('Hayabusa Gen 3 race software SD (speed density on a 3-bar MAP, boost spark retard, rolling anti-lag) '
          'for race/Busa-SD-v4.1.bin. XDF v6 = stock XDF v9.3 + race definitions. SD fuel and '
          'boost/ALS spark maps: X = raw IAP ADC, kPa = X*0.307429-12.6 (provisional 3-bar). Values are from SD-v4.1; '
          'items the race software changed are marked. Re-stamp field-1 CRC after editing. Start in folder 00; '
          'full item notes: docs/xdf-notes.csv.')
DIFFERS = ('DIFFERS FROM STOCK 5JCZSJ40 in the SD-v4.1 bin (changed by the race software): '
           'free-text "stock" remarks above describe the stock calibration.')

BLOCK = re.compile(r'<(XDFTABLE|XDFCONSTANT|XDFFLAG) uniqueid="(0x[0-9A-Fa-f]+)"[^>]*>.*?</\1>', re.S)


def key(kind, blk):
    if kind == 'XDFTABLE':
        z = re.search(r'<XDFAXIS id="z".*?mmedaddress="(0x[0-9A-Fa-f]+)"', blk, re.S)
        return ('T', int(z.group(1), 16))
    return ('C', int(re.search(r'mmedaddress="(0x[0-9A-Fa-f]+)"', blk).group(1), 16))


def categories(text):
    return {int(i, 16): n for i, n in re.findall(r'<CATEGORY index="(0x[0-9A-Fa-f]+)" name="([^"]*)"', text)}


def build_race():
    """Race XDF text before the user-friendly pass, plus counts for the summary line."""
    master = open(ms.MASTER, encoding='utf-8').read()
    race = open(RACE_SRC, encoding='utf-8').read()
    mcat, rcat = categories(master), categories(race)
    by_name = {n: i for i, n in mcat.items()}
    new_cats = []

    def remap(blk):
        def sub(m):
            name = rcat[int(m.group(1)) - 1]
            if name not in by_name:
                idx = max(list(mcat) + [by_name[n] for n in by_name]) + 1
                by_name[name] = idx
                new_cats.append((idx, name))
            return 'category="%d"' % (by_name[name] + 1)
        return re.sub(r'category="(\d+)"', sub, blk)

    race_blocks = {}
    for m in BLOCK.finditer(race):
        k = key(m.group(1), m.group(0))
        if (k[0] == 'T' and k[1] in OVERRIDE_TABLES) or (k[0] == 'C' and k[1] in OVERRIDE_CONSTS | ADD_CONSTS):
            race_blocks[k] = remap(m.group(0))
    missing = ({('T', a) for a in OVERRIDE_TABLES} | {('C', a) for a in OVERRIDE_CONSTS | ADD_CONSTS}) - set(race_blocks)
    if missing:
        sys.exit('race definitions not found: %s' % sorted(hex(a) for _, a in missing))

    # replace overlapping blocks (keep the master's uniqueid), then append the ALS settings
    out, last, used = [], 0, set()
    for m in BLOCK.finditer(master):
        k = key(m.group(1), m.group(0))
        out.append(master[last:m.start()])
        if k in race_blocks and k[1] not in ADD_CONSTS:
            blk = re.sub(r'uniqueid="0x[0-9A-Fa-f]+"', 'uniqueid="%s"' % m.group(2), race_blocks[k], count=1)
            out.append(blk)
            used.add(k)
        else:
            out.append(m.group(0))
        last = m.end()
    out.append(master[last:])
    text = ''.join(out)
    uids = {int(u, 16) for u in re.findall(r'uniqueid="(0x[0-9A-Fa-f]+)"', text)}
    nxt = 0xD100
    add = ''
    for a in sorted(ADD_CONSTS):
        while nxt in uids:
            nxt += 1
        blk = re.sub(r'uniqueid="0x[0-9A-Fa-f]+"', 'uniqueid="0x%X"' % nxt, race_blocks[('C', a)], count=1)
        uids.add(nxt)
        add += '  ' + blk + '\n'
    text = text.replace('</XDFFORMAT>', add + '</XDFFORMAT>')
    if new_cats:
        cat_xml = ''.join('    <CATEGORY index="0x%X" name="%s" />\n' % (i, escape(n)) for i, n in new_cats)
        text = text.replace('  </XDFHEADER>', cat_xml + '  </XDFHEADER>', 1)

    # recompute values from the SD bin; mark what the race software changed versus stock 5JCZSJ40
    ms.DIFFERS = DIFFERS
    sd = open(SD_BIN, 'rb').read()
    j40 = open(STOCK_J40, 'rb').read()
    text, n_diff = ms.build(text, j40, sd, 'SD-v4.1', '32990-10L4')
    # race-sourced items carry their own text: add the SD-v4.1 value so every item shows what is in the bin
    race_keys = {('T', a) for a in OVERRIDE_TABLES} | {('C', a) for a in OVERRIDE_CONSTS | ADD_CONSTS}

    def add_value(m):
        blk = m.group(0)
        if key(m.group(1), blk) not in race_keys or 'SD-v4.1 VALUE' in blk:
            return blk
        el = ET.fromstring(blk)
        z = el if m.group(1) != 'XDFTABLE' else [x for x in el.findall('XDFAXIS') if x.get('id') == 'z'][0]
        eq = ms.equation(z)
        vals = [ms.evaluate(eq, x) for x in ms.cells(sd, z)]
        units = (z.findtext('units') or '').strip()
        line = ('SD-v4.1 VALUE: %s %s (raw %d).' % (ms.fmt(vals[0]), units, ms.cells(sd, z)[0]) if len(vals) == 1
                else 'SD-v4.1 VALUES: %s to %s %s.' % (ms.fmt(min(vals)), ms.fmt(max(vals)), units))
        d = el.findtext('description') or ''
        new = ms.compact(d.replace('\n\nDIFFERS FROM', '\n\n' + line + '\n\nDIFFERS FROM', 1) if 'DIFFERS FROM' in d
                         else d + '\n\n' + line)
        return blk.replace('<description>' + escape(d, quote=False) + '</description>',
                           '<description>' + escape(new, quote=False) + '</description>', 1)
    text = BLOCK.sub(add_value, text)

    hdr = re.search(r'<deftitle>.*?</deftitle>\s*<description>.*?</description>', text, re.S)
    assert len(HEADER) <= ms.HEADER_MAX, len(HEADER)
    text = (text[:hdr.start()] + '<deftitle>Hayabusa Gen3 race software SD-v4.1 - XDF v6 (stock v9.3 base)</deftitle>\n'
            '    <description>%s</description>' % escape(HEADER, quote=False) + text[hdr.end():])
    return text, len(used), n_diff, len(new_cats)


def main():
    text, n_used, n_diff, n_new = build_race()
    ms.check(ET.fromstring(text))
    text = uf.finalize(text, race_changed_text='DIFFERS FROM STOCK 5JCZSJ40')
    uf.check(ET.fromstring(text))
    text = xp.inject(text)
    xp.check(text)
    open(OUT, 'w', encoding='utf-8').write(text)
    print('%s: %d race overrides, %d ALS settings added, %d items differ from stock 5JCZSJ40, %d new categories'
          % (os.path.relpath(OUT, ROOT), n_used, len(ADD_CONSTS), n_diff, n_new))


if __name__ == '__main__':
    main()
