#!/usr/bin/env python3
"""Build one stock XDF per Gen 3 Hayabusa read from the master stock v9 XDF.

Every 5JCZSJ* read in stock/reads/ has the same code and calibration layout as 5JCZSJ10
(every byte that differs between the reads lies inside an item the XDF defines), so the
definitions themselves carry over unchanged. Per read, this script:

  - recomputes every "VALUES (stock ...)" line (tables) and "STOCK (...)" line
    (constants and flags) from that read,
  - adds "THIS READ DIFFERS FROM 5JCZSJ10" to every item whose bytes differ, because the
    free-text remarks ("flat in stock", "stock 255", ...) were written for 5JCZSJ10,
  - adds two items the master does not define: the ECM ID string at 0x1FFAE4 and the
    variant word at 0x1B957C (both differ between reads),
  - writes a short per-read header (long header text crashes TunerPro).

The file is edited as text, so formatting and element order stay exactly as in the master.

usage: python3 tools/make_stock_xdfs.py            (from the repo root)
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, 'stock/xdf/Hayabusa-Gen3-5JCZSJ10-stock-v9.xdf')
REF_BIN = os.path.join(ROOT, 'stock/reads/32990-10L1x-5JCZSJ10.bin')
OUT_DIR = os.path.join(ROOT, 'stock/xdf/per-read')
REF_SW = '5JCZSJ10'

BLOCK = re.compile(r'(  <(XDFTABLE|XDFCONSTANT|XDFFLAG) uniqueid="(0x[0-9A-Fa-f]+)".*?</\2>\n)', re.S)


def read_val(b, addr, bits, signed):
    v = int.from_bytes(b[addr:addr + bits // 8], 'little')
    if signed and v >= 1 << (bits - 1):
        v -= 1 << bits
    return v


def evaluate(eq, x):
    return eval(eq, {'__builtins__': {}}, {'X': x})


def fmt(v):
    if float(v).is_integer():
        return '%d' % v if v != 0 else '0.00'
    return '%.2f' % v


def embedded(el):
    e = el.find('EMBEDDEDDATA')
    addr = int(e.get('mmedaddress'), 16)
    bits = int(e.get('mmedelementsizebits', '8'))
    signed = int(e.get('mmedtypeflags', '0x0'), 16) & 1
    rows = int(e.get('mmedrowcount') or 1)
    cols = int(e.get('mmedcolcount') or 1)
    major = int(e.get('mmedmajorstridebits') or 0)
    minor = int(e.get('mmedminorstridebits') or 0)
    return addr, bits, signed, rows, cols, major, minor


def cells(b, el):
    """Raw values of a table Z axis or a constant, honouring strides."""
    addr, bits, signed, rows, cols, major, minor = embedded(el)
    step = (minor or bits) // 8
    row = (major or cols * bits) // 8 if major > 0 else cols * step
    return [read_val(b, addr + r * row + c * step, bits, signed) for r in range(rows) for c in range(cols)]


def span(el):
    addr, bits, _, rows, cols, major, minor = embedded(el)
    step = (minor or bits) // 8
    row = (major or cols * bits) // 8 if major > 0 else cols * step
    return addr, addr + (rows - 1) * row + (cols - 1) * step + bits // 8


def equation(el):
    m = el.find('MATH')
    return m.get('equation') if m is not None else 'X'


def item_bytes(b, kind, el):
    if kind == 'XDFFLAG':
        a = int(el.find('EMBEDDEDDATA').get('mmedaddress'), 16)
        return b[a:a + 1]
    if kind == 'XDFCONSTANT':
        s, e = span(el)
        return b[s:e]
    out = b''
    for ax in el.findall('XDFAXIS'):
        if ax.find('EMBEDDEDDATA') is not None and ax.find('EMBEDDEDDATA').get('mmedaddress'):
            s, e = span(ax)
            out += b[s:e]
    return out


SAME_SUFFIX = ' - every cell the same, so the function is probably disabled or unused in this calibration.'
VALUES_LINE = re.compile(r'^VALUES \(stock ' + REF_SW + r'\): (\S+) to (\S+) (.*?)(\.|' + re.escape(SAME_SUFFIX) + r')$')
STOCK_CONST = re.compile(r'^STOCK \(' + REF_SW + r'\): (\S+) (.*?)\(raw (\S+) / 0x[0-9A-F]+\)\.(.*)$')
STOCK_FLAG = re.compile(r'^STOCK \(' + REF_SW + r'\): 0x[0-9A-F]{2} \(monitor (ON|OFF)\)\.(.*)$')


def rewrite_desc(desc, kind, el, b, sw, differs):
    lines = desc.split('\n')
    for i, line in enumerate(lines):
        m = VALUES_LINE.match(line)
        if m and kind == 'XDFTABLE':
            z = [a for a in el.findall('XDFAXIS') if a.get('id') == 'z'][0]
            eq = equation(z)
            vals = [evaluate(eq, x) for x in cells(b, z)]
            lo, hi = min(vals), max(vals)
            lines[i] = 'VALUES (stock %s): %s to %s %s%s' % (sw, fmt(lo), fmt(hi), m.group(3), SAME_SUFFIX if lo == hi else '.')
            continue
        m = STOCK_CONST.match(line)
        if m and kind == 'XDFCONSTANT':
            raw = cells(b, el)[0]
            _, bits, signed, *_ = embedded(el)
            v = evaluate(equation(el), raw)
            hexraw = raw & ((1 << bits) - 1) if raw < 0 else raw
            lines[i] = 'STOCK (%s): %s %s(raw %d / 0x%X).%s' % (sw, fmt(v), m.group(2), raw, hexraw, m.group(4))
            continue
        m = STOCK_FLAG.match(line)
        if m and kind == 'XDFFLAG':
            a = int(el.find('EMBEDDEDDATA').get('mmedaddress'), 16)
            mask = int(el.findtext('mask'), 16)
            on = b[a] & mask
            tail = m.group(2).replace('Stock %s already has' % REF_SW, 'Several stock calibrations ship with')
            lines[i] = 'STOCK (%s): 0x%02X (monitor %s).%s' % (sw, b[a], 'ON' if on else 'OFF', tail)
            continue
    out = '\n'.join(lines)
    if differs:
        out += ('\n\nTHIS READ DIFFERS FROM %s for this item. Any free-text "stock" remark above '
                '(e.g. "flat in stock") describes %s; the VALUES / STOCK line is this read.' % (REF_SW, REF_SW))
    return out


def header(sw, part, n_diff):
    return (
        'Suzuki Hayabusa Gen 3 (RH850/E1L), full 2 MB read, software %s (ECM %s). Stock fuel strategy '
        '(IAP vacuum / TPS blend), no patches. Built from the stock v9 XDF (verified on 5JCZSJ10): this read '
        'has identical code, and every byte that differs from 5JCZSJ10 lies inside an item defined here, so all '
        'addresses, sizes and axes are the same. VALUES / STOCK lines are recomputed from this read; %d items '
        'differ from 5JCZSJ10 and say so in their description. Scales: RPM = X/2.56; throttle/grip deg = X/364.08; '
        'kPa = (X-7862)/393.14; 8-bit temp C = X*0.9375-30; ignition deg = (X-64)*0.3516; trims above 64 = RETARD; '
        'km/h = X/128. Re-stamp the field-1 CRC after editing: python3 tools/fix_field1_crc.py. Field 3 (0x1FFEF8) '
        'is not handled. AUTO-DEFINED items come from code cross-references; log before changing them.'
        % (sw, part, n_diff))


NEW_ITEMS = '''  <XDFTABLE uniqueid="0xC00D" flags="0x0">
    <title>ID :: ECM Part String (ASCII bytes) @0x1FFAE4</title>
    <description>11 ASCII bytes just before the field-1 check data. Differs between reads: "ECM-010L0-0" on the 32990 parts, "32920-10LA*" / "LB*" / "LC*" on the 32920 parts. Not in a map descriptor; no code reference found. Identification only - do not edit.

VALUES (this read): {idtext}

REFERENCE: data @0x1FFAE4 (11 bytes).</description>
    <CATEGORYMEM index="0" category="30" />
    <XDFAXIS id="x" uniqueid="0x0">
      <EMBEDDEDDATA mmedelementsizebits="8" mmedmajorstridebits="0" mmedminorstridebits="0" />
      <indexcount>11</indexcount>
      <datatype>0</datatype>
      <unittype>0</unittype>
      <DALINK index="0" />
{labels}      <MATH equation="X">
        <VAR id="X" />
      </MATH>
    </XDFAXIS>
    <XDFAXIS id="y" uniqueid="0x0">
      <EMBEDDEDDATA mmedelementsizebits="16" mmedmajorstridebits="-32" mmedminorstridebits="0" />
      <indexcount>1</indexcount>
      <datatype>0</datatype>
      <unittype>0</unittype>
      <DALINK index="0" />
      <MATH equation="X">
        <VAR id="X" />
      </MATH>
    </XDFAXIS>
    <XDFAXIS id="z">
      <EMBEDDEDDATA mmedtypeflags="0x02" mmedaddress="0x1FFAE4" mmedelementsizebits="8" mmedrowcount="1" mmedcolcount="11" mmedmajorstridebits="0" mmedminorstridebits="0" />
      <units>ASCII code</units>
      <decimalpl>0</decimalpl>
      <min>0.000000</min>
      <max>255.000000</max>
      <outputtype>1</outputtype>
      <MATH equation="X">
        <VAR id="X" />
      </MATH>
    </XDFAXIS>
  </XDFTABLE>
  <XDFCONSTANT uniqueid="0xC00E" flags="0x0">
    <title>Market Variant :: Variant Word @0x1B957C (purpose unknown)</title>
    <description>32-bit word referenced from the pointer table at 0x1BA2B4. 0x88000001 on 5JCZSJ00 and 5JCZSNC0, 0 on the other stock reads. Purpose not decoded - leave as stock.

STOCK (this read): raw {raw} / 0x{rawhex}. ADDRESS 0x1B957C, 32-bit.</description>
    <CATEGORYMEM index="0" category="30" />
    <EMBEDDEDDATA mmedtypeflags="0x02" mmedaddress="0x1B957C" mmedelementsizebits="32" mmedmajorstridebits="0" mmedminorstridebits="0" />
    <units>raw</units>
    <decimalpl>0</decimalpl>
    <outputtype>3</outputtype>
    <datatype>0</datatype>
    <unittype>0</unittype>
    <DALINK index="0" />
    <MATH equation="X">
      <VAR id="X" />
    </MATH>
  </XDFCONSTANT>
'''


def build(master_text, ref, b, sw, part):
    n_diff = 0
    pieces = []
    last = 0
    for m in BLOCK.finditer(master_text):
        block, kind = m.group(1), m.group(2)
        el = ET.fromstring(block)
        differs = item_bytes(b, kind, el) != item_bytes(ref, kind, el)
        n_diff += differs
        d_el = el.find('description')
        new_block = block
        if d_el is not None and d_el.text:
            new_desc = rewrite_desc(d_el.text, kind, el, b, sw, differs)
            if new_desc != d_el.text:
                old_raw = '<description>' + escape(d_el.text, quote=False) + '</description>'
                if old_raw not in block:
                    sys.exit('description not found verbatim in block %s' % m.group(3))
                new_block = block.replace(old_raw, '<description>' + escape(new_desc, quote=False) + '</description>')
        pieces.append(master_text[last:m.start()])
        pieces.append(new_block)
        last = m.end()
    pieces.append(master_text[last:])
    text = ''.join(pieces)

    hdr = re.search(r'<deftitle>.*?</deftitle>\s*<description>.*?</description>', text, re.S)
    text = (text[:hdr.start()]
            + '<deftitle>Hayabusa Gen3 %s (%s) - Stock - v9</deftitle>\n    <description>%s</description>'
            % (sw, part, escape(header(sw, part, n_diff), quote=False))
            + text[hdr.end():])

    idb = b[0x1FFAE4:0x1FFAEF]
    labels = ''.join('      <LABEL index="%d" value="%d" />\n' % (i, i) for i in range(11))
    new = NEW_ITEMS.format(idtext=escape(idb.decode('ascii', 'replace')), labels=labels,
                           raw=int.from_bytes(b[0x1B957C:0x1B9580], 'little'),
                           rawhex='%08X' % int.from_bytes(b[0x1B957C:0x1B9580], 'little'))
    text = text.replace('</XDFFORMAT>', new + '</XDFFORMAT>')
    return text, n_diff


def main():
    master_text = open(MASTER, encoding='utf-8').read()
    ref = open(REF_BIN, 'rb').read()
    os.makedirs(OUT_DIR, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(ROOT, 'stock/reads/*-5JCZ*.bin'))):
        name = os.path.basename(path)[:-4]
        part, sw = name.split('-', 2)[0] + '-' + name.split('-', 2)[1][:-1], name.split('-', 2)[2]
        b = open(path, 'rb').read()
        text, n_diff = build(master_text, ref, b, sw, part)
        ET.fromstring(text)  # must still be valid XML
        out = os.path.join(OUT_DIR, 'Hayabusa-Gen3-%s-stock-v9.xdf' % sw)
        open(out, 'w', encoding='utf-8').write(text)
        print('%-10s %-11s %4d items differ from %s -> %s' % (sw, part, n_diff, REF_SW, os.path.relpath(out, ROOT)))


if __name__ == '__main__':
    main()
