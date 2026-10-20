#!/usr/bin/env python3
"""Enhance the GSX-R1000 M7 XDFs for CalStudio (no TunerPro limits):

  1. Fix the per-cylinder fuel-map labels. The Hayabusa->GSX-R port aligned maps by sequence
     order; the GSX-R fuel bank is SMALLER than the Hayabusa's (8 IAP 30x50 + 8 TPS 26x50, with
     NO blend/spare maps vs the Hayabusa's 28+28), so the order-port scattered the Hayabusa's
     per-cylinder labels (IAP Cyl1 full + Cyl2 partial, TPS only "Cyl4 spares", cyl 3/4 "missing").
     This relabels those 16 descriptors positionally: In-Gear Cyl 1-4 then Neutral/Clutch Cyl 1-4,
     for each of IAP and TPS, all tagged [UNCONFIRMED] (breakpoints differ from the Hayabusa).

  2. Add a value legend to every flag (0x80=ON/0x00=OFF; bit0=MIL-enable for DTC lamps) and every
     constant (meaningful-unit note, or raw), matching the Hayabusa v2 pass.

Operates in place on the four committed M7 XDFs; idempotent (skips work already applied).

usage: python3 gsxr-1000/tools/enhance_gsxr_xdf.py
"""
import glob
import os
import re
import xml.etree.ElementTree as ET
from html import escape as _escape

HERE = os.path.dirname(os.path.abspath(__file__))
M7 = os.path.join(os.path.dirname(HERE), 'M7')


def escape(s):
    return _escape(str(s), quote=False)


# descriptor address -> corrected fuel-map title (addresses identical across all four M7 reads)
# Fallback only: make_gsxr_xdf.py now owns the fuel relabel and writes a "CORRECTED LABEL (v2)"
# note, so this pass detects that note and skips. These titles match the generator's (code-confirmed
# In-Gear/Neutral via the 0x1560E4 pointer array + FUN_0004536C/FUN_0004543E).
FUEL_NOTE = ('CORRECTED LABEL (v2, code-confirmed): GSX-R fuel bank = 8 IAP + 8 TPS maps in one '
             'pointer array at 0x1560E4 (each split 4 In-Gear + 4 Neutral/Clutch). In-gear read by '
             'FUN_0004536C, neutral by FUN_0004543E (neutral/clutch flag 0xFEF0271D bit0). Cylinder '
             'number within each group is by position. Values GSX-R-specific - verify.')
FUEL = {}
for i, a in enumerate([0x157084, 0x1570dc, 0x157134, 0x15718c, 0x1571e4, 0x15723c, 0x157294, 0x1572ec]):
    cond = 'In Gear' if i < 4 else 'Neutral/Clutch-In'
    FUEL[a] = 'IAP - %s | Cyl %d' % (cond, (i % 4) + 1)
for i, a in enumerate([0x15733c, 0x15738c, 0x1573dc, 0x15742c, 0x15747c, 0x1574cc, 0x15751c, 0x15756c]):
    cond = 'In Gear' if i < 4 else 'Neutral/Clutch-In'
    FUEL[a] = 'TPS - %s | Cyl %d' % (cond, (i % 4) + 1)


def flag_legend(mask):
    m = int(mask, 16)
    if m == 0x80:
        return 'LEGEND: bit 7 (mask 0x80) - 0x80 = ON / enabled, 0x00 = OFF / disabled.'
    if m == 0x01:
        return ('LEGEND: bit 0 (mask 0x01) - 1 = this DTC turns ON the MIL / warning lamp, '
                '0 = lamp disabled for this DTC.')
    bit = (m.bit_length() - 1) if m else 0
    return 'LEGEND: bit %d (mask 0x%02X) - set = enabled, clear = disabled.' % (bit, m)


def enhance(text):
    stats = dict(fuel=0, flag_legends=0, const_legends=0)

    def fix_table(m):
        blk = m.group(0)
        dm = re.search(r'descriptor @0x([0-9A-Fa-f]+)', blk)
        if not dm:
            return blk
        addr = int(dm.group(1), 16)
        if addr in FUEL and 'CORRECTED LABEL' not in blk:
            stats['fuel'] += 1
            blk = re.sub(r'<title>.*?</title>', '<title>%s</title>' % escape(FUEL[addr]),
                         blk, count=1, flags=re.S)
            blk = re.sub(r'<description>', '<description>%s\n\n' % escape(FUEL_NOTE), blk, count=1)
        return blk

    text = re.sub(r'<XDFTABLE\b.*?</XDFTABLE>', fix_table, text, flags=re.S)

    def fix_flag(m):
        blk = m.group(0)
        if 'LEGEND:' in blk:
            return blk
        mk = re.search(r'<mask>(0x[0-9A-Fa-f]+)</mask>', blk)
        if not mk:
            return blk
        stats['flag_legends'] += 1
        leg = escape(flag_legend(mk.group(1)))
        if '</description>' in blk:
            return blk.replace('</description>', '\n\n' + leg + '</description>', 1)
        return re.sub(r'(</title>)', r'\1\n    <description>%s</description>' % leg, blk, count=1)

    text = re.sub(r'<XDFFLAG\b.*?</XDFFLAG>', fix_flag, text, flags=re.S)

    def fix_const(m):
        blk = m.group(0)
        if 'LEGEND' in blk:
            return blk
        um = re.search(r'<units>(.*?)</units>', blk, re.S)
        unit = (um.group(1).strip() if um else 'raw')
        if unit.lower() != 'raw':
            eqm = re.search(r'<MATH equation="([^"]*)"', blk)
            eq = eqm.group(1) if eqm else 'X'
            leg = 'LEGEND: displayed in %s%s (X = raw value).' % (
                unit, (' via %s' % eq) if eq not in ('', 'X') else '')
        else:
            leg = 'LEGEND: raw value; no physical unit assigned (decompiler-discovered scalar).'
        stats['const_legends'] += 1
        leg = escape(leg)
        if '</description>' in blk:
            return blk.replace('</description>', '\n\n' + leg + '</description>', 1)
        return re.sub(r'(</title>)', r'\1\n    <description>%s</description>' % leg, blk, count=1)

    text = re.sub(r'<XDFCONSTANT\b.*?</XDFCONSTANT>', fix_const, text, flags=re.S)
    return text, stats


def main():
    for p in sorted(glob.glob(os.path.join(M7, '*.xdf'))):
        text = open(p, encoding='utf-8').read()
        text, st = enhance(text)
        ET.fromstring(text)  # valid XML
        open(p, 'w', encoding='utf-8').write(text)
        print('%s: fuel-relabelled=%d flag-legends=%d const-legends=%d'
              % (os.path.basename(p), st['fuel'], st['flag_legends'], st['const_legends']))


if __name__ == '__main__':
    main()
