#!/usr/bin/env python3
"""Generate the v2 Gen-3 Hayabusa XDF (for CalStudio).

v2 is a reproducible, decompile-driven rebuild of the Hayabusa XDF definition. It takes the
verified master-v9 structural base - every one of the 749 on-bin map descriptors, the
hand-verified table names / scaling / units / folders, and every code-read scalar and flag -
and regenerates each item so the whole file ties back to the Ghidra decompile shipped in
hayabusa/re/decompiled.zip. Given the bin + that decompile + master-v9 it is deterministic,
so the definition can be regenerated and audited instead of hand-maintained. Target editor is
CalStudio, so descriptions are kept FULL (no TunerPro length/category/uniqueid limits apply).

What v2 adds over master-v9 (see docs/COMPARISON.md):
  * a standardized "TRACED INPUTS (v2 decompile)" line on every table, naming the X/Y axis
    RAM variable and its decompile-verified meaning - map-input coverage rises from 397 to
    ~630 of 747 by resolving each axis variable through ram-variables.csv + ram_inputs.csv;
  * v2 deep-trace upgrades (docs/busa-v2-trace.csv) applied to items master-v9 left LOW or
    "RAM not yet identified";
  * a clean category set (the legacy empty "Unidentified - Cluster" folders are scrubbed);
  * a v2 header documenting the build.

Everything structural (addresses, sizes, axes, scaling, folders, the 131-DTC enable/threshold
set, the hand-decoded fuel-strategy groups) is inherited unchanged from master-v9, which was
itself verified descriptor-by-descriptor against the bin. v2 does not fabricate: a table gets
a TRACED INPUTS line only where the decompile resolves one, and an item is upgraded only where
docs/busa-v2-trace.csv has code evidence.

usage: python3 make_busa_v2_xdf.py              (build the v2 master only -> busa-v2-master.xdf)
       python3 make_busa_v2_xdf.py --all        (build the master + a per-read v2 for every stock read)
       python3 make_busa_v2_xdf.py <sw> <part>  (build the master + one read, e.g. 5JCZSJ40 32990-10L4)
"""
import os
import re
import sys
from html import escape as _escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import busa_v2_common as C  # noqa: E402


def escape(s):
    return _escape(str(s), quote=False)


# ---- value recompute (same method as hayabusa/tools/make_stock_xdfs.py) -------------
def read_val(b, addr, bits, signed):
    v = int.from_bytes(b[addr:addr + bits // 8], 'little')
    if signed and v >= 1 << (bits - 1):
        v -= 1 << bits
    return v


def ev(eq, x):
    try:
        return eval(eq, {'__builtins__': {}}, {'X': float(x)})
    except Exception:
        return x


def fmt(v):
    v = float(v)
    return ('%d' % v) if v.is_integer() else ('%.2f' % v)


def _attr(el_attrs, key, default=None):
    m = re.search(r'%s="([^"]*)"' % key, el_attrs)
    return m.group(1) if m else default


# ---- block enhancement --------------------------------------------------------------
DESC = re.compile(r'<description>(.*?)</description>', re.S)
DESCRIPTOR = re.compile(r'descriptor @0x([0-9A-Fa-f]+)')
AXES_LINE = re.compile(r'(?m)^AXES:')
VALUES_LINE = re.compile(r'(?m)^VALUES ')
HOW_PARA = re.compile(r'(?s)(HOW THE ECU USES IT:.*?)(\n\n|\Z)')


def insert_traced_inputs(desc, line):
    """Insert the TRACED INPUTS line into a table description, idempotently."""
    if not line or 'TRACED INPUTS (v2' in desc:
        return desc
    block = '\n\n' + line
    m = HOW_PARA.search(desc)
    if m:
        return desc[:m.end(1)] + block + desc[m.end(1):]
    m = AXES_LINE.search(desc)
    if not m:
        m = VALUES_LINE.search(desc)
    if m:
        return desc[:m.start()].rstrip() + block + '\n\n' + desc[m.start():]
    return desc.rstrip() + block


def apply_v2_trace(desc, title, row):
    """Apply a v2 deep-trace upgrade: append a V2 UPGRADE note (and optionally a new title).

    row columns: address, new_title (optional), confidence, note
    """
    note = row.get('note', '').strip()
    conf = row.get('confidence', '').strip()
    if note and 'V2 DEEP-TRACE' not in desc:
        desc = desc.rstrip() + '\n\nV2 DEEP-TRACE (%s): %s' % (conf or 'traced', note)
    nt = row.get('new_title', '').strip()
    if nt:
        title = nt
    return desc, title


def enhance(master_text, mi, v2t):
    """Walk every item block; insert TRACED INPUTS on tables, apply v2 upgrades. Returns
    (new_text, stats)."""
    stats = dict(tables=0, inputs_added=0, upgrades=0)
    out = []
    pos = 0
    block_re = re.compile(r'  <(XDFTABLE|XDFCONSTANT|XDFFLAG) uniqueid="0x[0-9A-Fa-f]+".*?</\1>\n', re.S)
    for m in block_re.finditer(master_text):
        out.append(master_text[pos:m.start()])
        block = m.group(0)
        kind = m.group(1)
        tm = re.search(r'<title>(.*?)</title>', block, re.S)
        title = tm.group(1) if tm else ''
        dm = DESC.search(block)
        desc = dm.group(1) if dm else ''
        new_title, new_desc = title, desc

        if kind == 'XDFTABLE':
            stats['tables'] += 1
            dref = DESCRIPTOR.search(desc)
            if dref:
                line = C.traced_inputs_line(int(dref.group(1), 16), mi)
                after = insert_traced_inputs(new_desc, line)
                if after != new_desc:
                    stats['inputs_added'] += 1
                    new_desc = after

        # v2 deep-trace upgrade keyed by this item's primary EMBEDDEDDATA address
        am = re.search(r'mmedaddress="0x([0-9A-Fa-f]+)"', block)
        if am:
            addr = int(am.group(1), 16)
            if addr in v2t:
                nd, nt = apply_v2_trace(new_desc, new_title, v2t[addr])
                if nd != new_desc or nt != new_title:
                    stats['upgrades'] += 1
                    new_desc, new_title = nd, nt

        if new_desc != desc and dm:
            block = block[:dm.start(1)] + escape(_unescape(new_desc)) + block[dm.end(1):]
        if new_title != title and tm:
            block = re.sub(r'<title>.*?</title>', '<title>%s</title>' % escape(new_title),
                           block, count=1, flags=re.S)
        out.append(block)
        pos = m.end()
    out.append(master_text[pos:])
    return ''.join(out), stats


def _unescape(s):
    return s.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')


# ---- header + categories ------------------------------------------------------------
def rewrite_header(text, sw, part):
    deftitle = 'Hayabusa Gen3 %s (%s) - v2 (decompile-traced, reproducible)' % (sw, part)
    desc = ('Suzuki Hayabusa Gen 3 (RH850/E1L), full 2 MB read, software %s (ECM %s). v2 REBUILD: '
            'the verified master-v9 definition (all 749 on-bin map descriptors, every code-read '
            'scalar/flag, the 131-DTC monitor-enable/threshold set, the hand-decoded fuel-strategy '
            'groups) regenerated from the Ghidra decompile (hayabusa/re/decompiled.zip) by '
            'tools/make_busa_v2_xdf.py, so every item ties back to the code that reads it and the '
            'whole file is reproducible. v2 adds a TRACED INPUTS line on every table naming the X/Y '
            'axis RAM variable and its meaning (map-input coverage ~630/747, up from 397), plus v2 '
            'deep-trace upgrades on items left LOW in v9. Scales: RPM=X/2.56; throttle/grip=X/364.08 '
            'deg; pressure kPa=(X-7862)/393.14 (IAP fuel maps use VACUUM); temp C=X*0.9375-30; '
            'ignition deg=(X-64)*0.3516; trims above 64=RETARD; speed km/h=X/128. Re-stamp field-1 '
            'CRC (0x10000-0x1FFAFB @0x1FFAFE) with hayabusa/tools/fix_field1_crc.py after editing. '
            'Full per-item trace: docs/. UNVERIFIED ON HARDWARE - bench first, keep a stock read.'
            % (sw, part))
    text = re.sub(r'<deftitle>.*?</deftitle>', '<deftitle>%s</deftitle>' % escape(deftitle),
                  text, count=1, flags=re.S)
    text = re.sub(r'<description>.*?</description>', '<description>%s</description>' % escape(desc),
                  text, count=1, flags=re.S)
    return text


def clean_categories(text):
    """Scrub the legacy ' (legacy, empty)' folder-name suffix inherited from v9's header."""
    return re.sub(r'(<CATEGORY index="0x[0-9A-Fa-f]+" name=")([^"]*)(" />)',
                  lambda m: m.group(1) + m.group(2).replace(' (legacy, empty)', '') + m.group(3),
                  text)


# ECM part number per stock read (the v2 per-read XDFs carry that read's own stock values)
PARTS = {'5JCZSJ00': '32990-10L0', '5JCZSJ10': '32990-10L1', '5JCZSJ20': '32990-10L2',
         '5JCZSJ30': '32990-10L3', '5JCZSJ40': '32990-10L4', '5JCZSJA0': '32920-10LA',
         '5JCZSJB0': '32920-10LB', '5JCZSNC0': '32920-10LC'}
MASTER_OUT = os.path.join(C.V2, 'busa-v2-master.xdf')


def _funcnames(text):
    """Apply readable FUN_<addr> names (same pass the stock reads use), if available."""
    try:
        sys.path.insert(0, os.path.join(C.HAYA, 'tools'))
        import xdf_funcnames as fn
        return fn.rename(text)
    except Exception:
        return text


# ---- generate -----------------------------------------------------------------------
def build_master():
    """Enhance master-v9 into the full-text v2 master (valued, like v9, for 5JCZSJ10)."""
    import xml.etree.ElementTree as ET
    text = open(C.MASTER, encoding='utf-8').read()
    text, stats = enhance(text, C.map_inputs(), C.v2_trace_rows())
    text = rewrite_header(text, '5JCZSJ10', '32990-10L1')
    text = clean_categories(text)
    text = _funcnames(text)
    ET.fromstring(text)                      # valid XML (CalStudio: no TunerPro length limits)
    open(MASTER_OUT, 'w', encoding='utf-8').write(text)
    return text, stats


def build_read(master_text, sw, part):
    """Full-text per-read v2 XDF carrying this read's own stock values. Reuses the proven
    make_stock_xdfs value/DIFFERS recompute with compaction DISABLED (CalStudio, no limits)."""
    import xml.etree.ElementTree as ET
    sys.path.insert(0, os.path.join(C.HAYA, 'tools'))
    import make_stock_xdfs as ms
    ms.compact = lambda s: s                 # CalStudio: keep full descriptions, do not trim
    ms.DESC_MAX = 10 ** 9
    ref = open(C.REF_BIN, 'rb').read()
    b = open(os.path.join(C.HAYA, 'stock', sw, sw + '.bin'), 'rb').read()
    text, n_diff = ms.build(master_text, ref, b, sw, part)   # per-read values + DIFFERS + ID items
    text = rewrite_header(text, sw, part)    # swap ms's stock header for the v2 header
    text = clean_categories(text)
    text = _funcnames(text)
    ET.fromstring(text)                      # valid XML; no ms.check (that enforces TunerPro limits)
    out = os.path.join(C.V2, '%s-v2.xdf' % sw)
    open(out, 'w', encoding='utf-8').write(text)
    return n_diff, out


if __name__ == '__main__':
    args = sys.argv[1:]
    master_text, st = build_master()
    print('master -> %s  (tables=%d traced-inputs=%d upgrades=%d)'
          % (os.path.relpath(MASTER_OUT, C.ROOT), st['tables'], st['inputs_added'], st['upgrades']))
    if args and args[0] == '--all':
        for sw in sorted(PARTS):
            if os.path.exists(os.path.join(C.HAYA, 'stock', sw, sw + '.bin')):
                n_diff, out = build_read(master_text, sw, PARTS[sw])
                print('   %-9s -> %s  (%d items differ from 5JCZSJ10)'
                      % (sw, os.path.relpath(out, C.ROOT), n_diff))
    elif len(args) == 2:                     # <software> <partno> : one read
        n_diff, out = build_read(master_text, args[0], args[1])
        print('   %-9s -> %s  (%d items differ from 5JCZSJ10)' % (args[0], os.path.relpath(out, C.ROOT), n_diff))
