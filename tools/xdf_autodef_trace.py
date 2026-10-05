#!/usr/bin/env python3
"""Apply the code trace of the AUTO-DEFINED constants (docs/autodef-trace.csv) to an XDF, in place (v9.3).

The CSV was produced by tracing every auto-defined calibration constant through the decompiled
5JCZSJ40 code (re/decompiled.zip):
  - which RAM variable it is compared with, written to, filtered, counted against or passed to,
  - the meaning of that RAM variable, proven from the code that writes it (sensor ADC channel,
    copies, filters and clamps of verified variables), and
  - one line of code showing the use.
For each row this script rewrites the item's title and description, and its unit only where the
trace proves it (`equation` / `units` columns filled). Items renamed by hand in v9.1/v9.2 are not in
the CSV. Confidence: HIGH = role read directly from the code (comparison with a verified variable,
switch test, counter, filter, direct write); MEDIUM = role known but the other side is not identified;
LOW = the trace could not resolve the use.

usage: python3 tools/xdf_autodef_trace.py <file.xdf> <reference.bin> <sw label in STOCK lines>
Idempotent: a second run changes nothing.
"""
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, 'docs', 'autodef-trace.csv')
BLOCK = re.compile(r'<XDFCONSTANT uniqueid="(0x[0-9A-Fa-f]+)"[^>]*>.*?</XDFCONSTANT>', re.S)


def fmt(v, dec):
    return ('%.' + str(dec) + 'f') % v if dec else '%d' % round(v)


def rewrite(blk, row, b, sw):
    addr = int(row['address'], 16)
    if int(re.search(r'mmedaddress="(0x[0-9A-Fa-f]+)"', blk).group(1), 16) != addr:
        return blk
    bits = int(row['bits'])
    if row['units']:
        blk = re.sub(r'<MATH equation="[^"]*">', '<MATH equation="%s">' % row['equation'], blk, count=1)
        blk = re.sub(r'<units>.*?</units>', '<units>%s</units>' % escape(row['units'], quote=False), blk, count=1)
        blk = re.sub(r'<decimalpl>\d+</decimalpl>', '<decimalpl>%s</decimalpl>' % row['decimals'], blk, count=1)
    eq = re.search(r'<MATH equation="([^"]*)"', blk).group(1)
    units = re.search(r'<units>(.*?)</units>', blk).group(1) if '<units>' in blk else 'raw'
    dm = re.search(r'<decimalpl>(\d+)</decimalpl>', blk)
    dec = int(dm.group(1)) if dm else 0
    signed = int(re.search(r'mmedtypeflags="(0x[0-9A-Fa-f]+)"', blk).group(1), 16) & 1 if 'mmedtypeflags' in blk else 0
    raw = int.from_bytes(b[addr:addr + bits // 8], 'little', signed=bool(signed))
    v = eval(eq, {'X': raw})
    desc = 'TRACED (v9.3, confidence %s): %s' % (row['confidence'], row['sentence'])
    if row['code']:
        desc += '\nCODE %s: %s' % (row['function'], row['code'])
    desc += '\n\nSTOCK (%s): %s %s (raw %d / 0x%X). ADDRESS 0x%X, %d-bit.' % (
        sw, fmt(v, dec), units, raw, raw & ((1 << bits) - 1), addr, bits)
    blk = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % escape(row['title'], quote=False), blk, count=1)
    blk = re.sub(r'<description>.*?</description>', lambda m: '<description>%s</description>' % escape(desc, quote=False),
                 blk, count=1, flags=re.S)
    return blk


def apply(text, b, sw):
    rows = {r['uid']: r for r in csv.DictReader(open(CSV, encoding='utf-8'))}
    out, last = [], 0
    for m in BLOCK.finditer(text):
        row = rows.get(m.group(1))
        out.append(text[last:m.start()])
        out.append(rewrite(m.group(0), row, b, sw) if row else m.group(0))
        last = m.end()
    out.append(text[last:])
    text = ''.join(out)
    # items corrected by hand in v9.2 keep their text but are no longer unverified
    text = re.sub(r'(verified from code, v9\.2\)\.(?:(?!</description>).)*?)CONFIDENCE: AUTO-DEFINED from code cross-references[^<\n]*',
                  lambda m: m.group(1) + 'CONFIDENCE: VERIFIED (v9.2) - the compared RAM variable and the unit were checked against the code.',
                  text, flags=re.S)
    ET.fromstring(text)
    return text


if __name__ == '__main__':
    path, binp, sw = sys.argv[1:4]
    old = open(path, encoding='utf-8').read()
    new = apply(old, open(binp, 'rb').read(), sw)
    open(path, 'w', encoding='utf-8').write(new)
    print('%s: %s' % (path, 'updated' if new != old else 'no changes'))
