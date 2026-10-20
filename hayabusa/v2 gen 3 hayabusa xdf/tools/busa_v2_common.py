#!/usr/bin/env python3
"""Shared helpers for the v2 Gen-3 Hayabusa XDF build.

Everything the v2 generator needs that is sourced from the Ghidra decompile and the repo
docs: RAM-variable meanings, the per-map traced X/Y inputs (from re/decompiled.zip's
map_links.csv), the scalar/flag role traces (docs/autodef-trace.csv), and the DTC table
(docs/dtc-table.csv).

The v2 build is reproducible: given the bin, the shipped decompile artifacts and master-v9,
it deterministically regenerates the enhanced definition. This module carries no tuning data
of its own - only joins over the decompile output.
"""
import csv
import io
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)                         # "v2 gen 3 hayabusa xdf"
HAYA = os.path.dirname(V2)                          # hayabusa/
ROOT = os.path.dirname(HAYA)                        # repo root

MASTER = os.path.join(HAYA, 'stock/master/master-v9.xdf')
REF_BIN = os.path.join(HAYA, 'stock/5JCZSJ10/5JCZSJ10.bin')
DECOMP_ZIP = os.path.join(HAYA, 're/decompiled.zip')
RAMVARS = os.path.join(HAYA, 'docs/ram-variables.csv')
AUTODEF = os.path.join(HAYA, 'docs/autodef-trace.csv')
DTC = os.path.join(HAYA, 'docs/dtc-table.csv')
# v2-local deep-trace additions (RAM names resolved in this project; may be absent on first run)
V2_RAMNAMES = os.path.join(V2, 'docs/busa-v2-ram-names.csv')
V2_TRACE = os.path.join(V2, 'docs/busa-v2-trace.csv')


def _zip_text(name):
    with zipfile.ZipFile(DECOMP_ZIP) as z:
        return z.read(name).decode('utf-8', 'replace')


def norm_ram(v):
    """'RAM_0xFEF02644' / 'fef02644' / '0xFEF02644' -> '0xFEF02644', else None."""
    if not v:
        return None
    m = re.search(r'([fF][eE][fF]0[0-9A-Fa-f]{4}|[fF][eE][bB][fF][0-9A-Fa-f]{4})', v)
    if m:
        return '0x' + m.group(1).upper()
    m = re.search(r'0x([0-9A-Fa-f]{6,8})', v)
    return ('0x' + m.group(1).upper()) if m else None


def ram_meanings():
    """RAM addr (0xUPPER) -> dict(meaning, unit, conv, conf, src).

    Curated docs/ram-variables.csv first (hand-verified), then the decompile-inferred
    ram_inputs.csv, then any v2-local additions. Earlier sources win.
    """
    out = {}
    for r in csv.DictReader(open(RAMVARS)):
        a = norm_ram(r['ram_address'])
        if a:
            out[a] = dict(meaning=(r['meaning'] or r['name']).strip(), unit=r['display_unit'].strip(),
                          conv=r['conversion'].strip(), conf=r['confidence'].strip(), src='curated')
    try:
        for r in csv.DictReader(io.StringIO(_zip_text('ram_inputs.csv'))):
            a = norm_ram(r['ram'])
            if a and a not in out and r['inferred'].strip():
                out[a] = dict(meaning=r['inferred'].strip(), unit='', conv='', conf='inferred',
                              src='decompile')
    except Exception:
        pass
    if os.path.exists(V2_RAMNAMES):
        for r in csv.DictReader(open(V2_RAMNAMES)):
            a = norm_ram(r['ram_address'])
            if a:
                out[a] = dict(meaning=r['meaning'].strip(), unit=r.get('unit', '').strip(),
                              conv=r.get('conversion', '').strip(),
                              conf=r.get('confidence', 'v2-traced').strip(), src='v2')
    return out


def map_inputs():
    """descriptor addr (int) -> dict(x, xmean, y, ymean, func, xconf, yconf).

    Joins the decompile map_links.csv (per-map X/Y axis RAM variable + any meaning it
    already carried) with ram_meanings() so an axis whose variable is known but whose
    meaning was blank now resolves. This is the coverage lift at the heart of v2.
    """
    rm = ram_meanings()
    out = {}
    for r in csv.DictReader(io.StringIO(_zip_text('map_links.csv'))):
        if not r.get('descriptor'):
            continue
        try:
            da = int(r['descriptor'], 16)
        except ValueError:
            continue
        rec = dict(func=(r.get('function') or '').strip(), x=None, xmean='', y=None, ymean='',
                   xconf='', yconf='')
        for ax in ('x', 'y'):
            raw = (r.get('%s_input' % ax) or '').strip()
            given = (r.get('%s_input_meaning' % ax) or '').strip()
            var = norm_ram(raw)
            rec[ax] = var
            # prefer the hand-verified curated meaning for this axis variable; fall back to the
            # meaning the decompile already carried, then to any decompile/v2-inferred meaning
            if var and var in rm and rm[var]['src'] == 'curated':
                rec[ax + 'mean'] = rm[var]['meaning']
                rec[ax + 'conf'] = rm[var]['conf']
            elif given:
                rec[ax + 'mean'] = given
                rec[ax + 'conf'] = 'decompile'
            elif var and var in rm:
                rec[ax + 'mean'] = rm[var]['meaning']
                rec[ax + 'conf'] = rm[var]['conf']
        # a descriptor can appear at several call sites; keep the record that resolves the
        # most axis meanings (and never lose a resolved axis to a later blank one)
        prev = out.get(da)
        if prev is None:
            out[da] = rec
        else:
            for ax in ('x', 'y'):
                if not prev[ax + 'mean'] and rec[ax + 'mean']:
                    prev[ax], prev[ax + 'mean'], prev[ax + 'conf'] = rec[ax], rec[ax + 'mean'], rec[ax + 'conf']
            if not prev['func'] and rec['func']:
                prev['func'] = rec['func']
    return out


def traced_inputs_line(desc_addr, mi):
    """GSXR-style 'TRACED INPUTS' line for a table, or '' when nothing resolves."""
    r = mi.get(desc_addr)
    if not r:
        return ''
    bits = []
    for ax in ('x', 'y'):
        var, mean, conf = r[ax], r[ax + 'mean'], r[ax + 'conf']
        if not var and not mean:
            continue
        s = '%s = %s' % (ax.upper(), mean or 'signal')
        if var:
            s += ' (RAM %s)' % var
        if conf and conf not in ('high', 'decompile'):
            s += ' [%s]' % conf
        bits.append(s)
    if not bits:
        return ''
    tail = (' Read by %s.' % r['func']) if r['func'] else ''
    return 'TRACED INPUTS (v2 decompile): %s.%s' % ('; '.join(bits), tail)


def dtc_rows():
    """List of dicts from docs/dtc-table.csv (index, DTC, Description, Lamp byte address...)."""
    return list(csv.DictReader(open(DTC)))


def autodef_rows():
    """address(int) -> role-trace dict from docs/autodef-trace.csv."""
    out = {}
    for r in csv.DictReader(open(AUTODEF)):
        try:
            out[int(r['address'], 16)] = r
        except (ValueError, KeyError):
            pass
    return out


def v2_trace_rows():
    """address(int) -> v2 deep-trace upgrade dict, if docs/busa-v2-trace.csv exists."""
    out = {}
    if os.path.exists(V2_TRACE):
        for r in csv.DictReader(open(V2_TRACE)):
            try:
                out[int(r['address'], 16)] = r
            except (ValueError, KeyError):
                pass
    return out


# ---- value legends + code-grounded unit inheritance --------------------------------
def ram_conv():
    """RAM addr (0xUPPER) -> (unit, equation, meaning) from the curated ram-variables.csv.
    equation is a TunerPro MATH expression in X (the raw value), e.g. 'X/2.56'."""
    out = {}
    for r in csv.DictReader(open(RAMVARS)):
        a = norm_ram(r['ram_address'])
        if a:
            out[a] = (r['display_unit'].strip(), (r['conversion'].strip() or 'X'), r['meaning'].strip())
    return out


_FEF = re.compile(r'fef0[0-9a-fA-F]{4}')


def const_unit_map():
    """address(int) -> (unit, equation, meaning, ramvar) for every auto-defined THRESHOLD scalar
    whose decompiled code line compares it against exactly one known sensor RAM variable. That
    makes the scalar's unit the sensor's unit (the v9.2 re-pairing method, applied by code). Only
    these high-confidence cases are offered for a unit upgrade; everything else keeps raw + a legend.
    """
    rc = ram_conv()
    out = {}
    for a, r in autodef_rows().items():
        if r.get('role') != 'threshold':
            continue
        vs = [v for v in dict.fromkeys('0x' + x.upper() for x in _FEF.findall(r.get('code', ''))) if v in rc]
        if len(vs) == 1:
            unit, eq, meaning = rc[vs[0]]
            if unit and unit.lower() != 'raw':
                out[a] = (unit, eq, meaning, vs[0])
    return out


V2_DTC_NAMES = os.path.join(V2, 'docs/manual-dtc-names.csv')


def dtc_by_lamp_addr():
    """lamp-byte address (int) -> (code, bin_description, official_SAE_name) joining the bin's
    DTC table (docs/dtc-table.csv) with the service-manual official names (manual-dtc-names.csv)."""
    man = {}
    if os.path.exists(V2_DTC_NAMES):
        for r in csv.DictReader(open(V2_DTC_NAMES)):
            man[r['code'].strip()] = r['official_name_SAE'].strip()
    out = {}
    for r in dtc_rows():
        try:
            a = int(r['Lamp byte address'], 16)
        except (ValueError, KeyError):
            continue
        code = re.match(r'([PCU]\d{4})', r['DTC'].strip())
        code = code.group(1) if code else r['DTC'].strip()
        out[a] = (r['DTC'].strip(), r.get('Description', '').strip(), man.get(code, ''))
    return out


def flag_legend(mask):
    """Human legend for a flag's on/off meaning, by its bit mask."""
    m = int(mask, 16) if isinstance(mask, str) else mask
    if m == 0x80:
        return 'LEGEND: bit 7 (mask 0x80) - 0x80 = ON / enabled, 0x00 = OFF / disabled.'
    if m == 0x01:
        return ('LEGEND: bit 0 (mask 0x01) - 1 = this DTC monitor turns ON the MIL / warning lamp, '
                '0 = lamp disabled for this DTC (monitor may still run).')
    if m == 0x40:
        return 'LEGEND: bit 6 (mask 0x40) - 0x40 = set / enabled, 0x00 = clear / disabled.'
    bit = (m.bit_length() - 1) if m else 0
    return 'LEGEND: bit %d (mask 0x%02X) - set = enabled, clear = disabled.' % (bit, m)


if __name__ == '__main__':
    mi = map_inputs()
    xres = sum(1 for r in mi.values() if r['xmean'])
    yres = sum(1 for r in mi.values() if r['ymean'])
    print('map_inputs: %d maps; X meaning %d, Y meaning %d' % (len(mi), xres, yres))
    rm = ram_meanings()
    print('ram meanings: %d (curated+decompile+v2)' % len(rm))
    print('dtc rows: %d; autodef rows: %d; v2 trace rows: %d'
          % (len(dtc_rows()), len(autodef_rows()), len(v2_trace_rows())))
