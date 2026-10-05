#!/usr/bin/env python3
"""Final pass for the XDFs people open in TunerPro: workflow folders and short descriptions.

make_stock_xdfs.py and make_race_xdf.py call finalize() on every file they write. It:

  - replaces the category list with numbered workflow folders (00 Start Here, 01-06 fuel, 07-08 ignition,
    09-20 throttle / rider aids / race, 30-32 diagnostics, 40-41 settings and ETV safety, 80-99 reference).
    Every item gets exactly one main folder (CATEGORYMEM index 0), chosen from its title and its old
    categories by FOLDER_RULES (first match wins). Cross-cutting folders are added as extra memberships:
    00 Start Here (the maps most tunes start with), 20 Race (SD bins), 80 Low Confidence, 88 Switches,
    89 Unused / Flat;
  - cuts every item description to at most DESC_SHORT characters: a one-line summary, the value line from
    this bin, a confidence / differs tag and the address. Nothing else is lost: the full text of every item
    is in docs/xdf-notes.csv (written by `python3 tools/xdf_userfriendly.py`).

The file is edited as text, so element order and formatting stay as they were.

usage: python3 tools/xdf_userfriendly.py      (from the repo root: rewrites docs/xdf-notes.csv)
"""
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = os.path.join(ROOT, 'docs/xdf-notes.csv')
DESC_SHORT = 420
SUMMARY_MAX = 220
VALUE_MAX = 150

START = '00 Start Here - main maps and limits'
RACE = '20 Race - SD Fuel, Boost Spark, Anti-Lag'
LOW = '80 Low Confidence - log before changing'
SWITCHES = '88 All On/Off Switches (0x80 = ON)'
UNUSED = '89 Unused / Flat / Inactive - leave stock'

# Parent folders. TunerPro's Parameter Tree nests by each item's category-membership order (first = top),
# so giving a numbered folder a parent as its first membership makes it appear under that parent.
FUEL = 'Fuel'
IGN = 'Ignition'
THROTTLE = 'Throttle & Ride Modes'
LIMITS = 'Limiters, Launch & Shift'
CHASSIS = 'Traction & Chassis'
COMFORT = 'Cruise & Idle'
SENSORS = 'Sensors, ECU & IDs'
DIAG = 'Diagnostics'

# child folder number -> parent folder
PARENTS = {
    '01': FUEL, '02': FUEL, '03': FUEL, '04': FUEL, '05': FUEL, '06': FUEL,
    '07': IGN, '08': IGN,
    '09': THROTTLE, '10': THROTTLE,
    '11': LIMITS, '12': LIMITS, '13': LIMITS,
    '14': CHASSIS, '15': CHASSIS, '17': CHASSIS,
    '16': COMFORT, '18': COMFORT,
    '19': SENSORS, '40': SENSORS, '41': SENSORS, '99': SENSORS,
    '30': DIAG, '31': DIAG, '32': DIAG,
}

FOLDERS = [
    START,
    # parents (this order is the top-level tree order)
    FUEL, IGN, THROTTLE, LIMITS, CHASSIS, COMFORT, SENSORS, DIAG,
    # children, grouped under their parent (this order is the order within each parent)
    '01 Main Fuel Maps',
    '02 Strategy, Blend and Settings',
    '03 Injectors and Injection Timing',
    '04 Start, Warm-Up, Air Temp and Baro',
    '05 Accel Enrichment and Decel Cut',
    '06 Closed Loop (O2)',
    '07 Base Advance Maps',
    '08 Trims and Corrections',
    '09 Throttle (ETV) and Power Modes',
    '10 Ride Mode Presets',
    '11 Limiters - Rev, Per-Gear, Top Speed',
    '12 Launch Control',
    '13 Quickshifter',
    '14 Traction Control',
    '15 Anti-Lift, Pitch and Engine Brake',
    '17 IMU, Wheel Speed and Gear Position',
    '16 Cruise Control',
    '18 Idle and Cooling Fan',
    '19 Sensors and Scaling',
    '40 ECU Settings',
    '41 ETV Safety Monitor - do not edit',
    '99 IDs, Variant, Checksums - do not edit',
    '30 DTC On/Off',
    '31 DTC Thresholds and Lamp',
    '32 OBD, CAN, Meter, EVAP',
    # top-level folders without a parent
    RACE,
    LOW,
    SWITCHES,
    UNUSED,
]

# (folder number, regex on the title, regex on the item's old main category); first match wins
FOLDER_RULES = [
    ('99', r'^(ID ::|Software Nr|Market Variant|Variant)', r'Checksums|xdf moto bin|^ECU Info|Market Variant'),
    ('17', r'^Wheel Speed ::', None),
    ('02', r'^Fuel Blend', None),
    ('20', r'^(ALS |Boost Spark|ALS Timing)|Rolling Anti-Lag', r'Rolling Anti-Lag'),
    ('01', r'^(TPS|IAP|SD \(abs MAP\)) - ', None),
    ('20', None, r'Speed Density \(SD bins\)'),
    ('03', r'^(Injector|Injection Timing|Fuel :: Baro Correction \| (Primary|Secondary) Injectors)', r'^(Scalars - )?Injectors|Secondary Injection'),
    ('05', r'^(Accel Enrichment|Decel)', r'Deceleration Fuel Cut'),
    ('04', r'^(Cranking|Afterstart|Start Prime|Fuel :: (Afterstart|ECT|Baro|IAT|Key-On|Warm))', None),
    ('02', r'^(Fuel|SWITCH Fuel|Fuel Blend)', r'^(Scalars - )?Fuel|Neutral/Clutch-In'),
    ('06', None, r'HO2'),
    ('07', r'^IGN :: Advance', None),
    ('08', r'^(IGN|Ignition|SWITCH Ignition)', r'^(Scalars - )?Ignition'),
    ('41', None, r'ETV Monitor'),
    ('12', r'^Launch', r'Launch Control'),
    ('13', r'^Quickshifter', r'Quickshifter'),
    ('11', r'Limiter|Rev Limit|Fuel-Cut Gear-Sensor', r'^(Scalars - )?Limiters'),
    ('09', r'^(ETV|Throttle)', r'Throttle By Wire|Other ETV Maps'),
    ('10', None, r'Ride Mode Presets'),
    ('14', None, r'Traction Control'),
    ('15', None, r'Anti-Lift|Pitch Control|Engine Brake'),
    ('16', None, r'Cruise Control'),
    ('17', None, r'IMU|Gear Dependent|Rider Aids'),
    ('18', None, r'Idle Control|Fan Control'),
    ('30', None, r'Monitor Enables'),
    ('31', None, r'DTC Lamp|Monitor Thresholds|Diagnostics - Monitors|Emissions DTCs'),
    ('32', None, r'OBD|Meter / CAN|EVAP'),
    ('19', None, r'Sensor'),
    ('89', None, r'Unused / Inactive'),
    ('40', None, r'ECU Settings|ECU Info'),
]

# extra membership: the items most tunes start with
START_RULES = (r'^(TPS|IAP) - (In Gear|Neutral/Clutch-In) \| Cyl \d$', r'^SD \(abs MAP\) - ', r'^IGN :: Advance Timing',
               r'^Injector Deadtime', r'^Rev Limiter \(', r'^Per-Gear Limiter( Enable$| \| 6th)',
               r'^Launch Control \| Level \d \| (Soft Cut start|Hard Cut)', r'^Quickshifter :: Master Disable',
               r'^ETV - PWR 1 \|', r'^ALS (Enable|Max Active Time)$')

HEADS = ('STOCK', 'VALUES', 'SD-v4.1 VALUE', 'AXES', 'REFERENCE', 'HOW THE ECU USES IT', 'HOW IT WORKS', 'TUNING NOTES',
         'CONFIDENCE', 'Previous title', 'DIFFERS FROM', 'CODE ', 'STARTING VALUES')
BLOCK = re.compile(r'<(XDFTABLE|XDFCONSTANT|XDFFLAG) uniqueid="(0x[0-9A-Fa-f]+)"[^>]*>.*?</\1>', re.S)


def folder_number(title, old):
    main = old[0] if old else ''
    for num, t_re, c_re in FOLDER_RULES:
        if (t_re and re.search(t_re, title)) or (c_re and re.search(c_re, main)):
            return num
    return '40'


def folders_for(title, old, desc):
    """Main folder first, then the cross-cutting folders the item belongs to."""
    by_num = {f[:2]: f for f in FOLDERS}
    out = [by_num[folder_number(title, old)]]
    parent = PARENTS.get(out[0][:2])      # nest under a parent (first membership = tree top)
    if parent:
        out = [parent] + out
    joined = ' | '.join(old)
    if any(re.search(r, title) for r in START_RULES):
        out.append(START)
    if re.search(r'Speed Density|Rolling Anti-Lag', joined) and RACE not in out:
        out.append(RACE)
    if confidence(desc) == 'LOW':
        out.append(LOW)
    if 'Switches & Toggles' in joined or title.startswith('SWITCH '):
        out.append(SWITCHES)
    if re.search(r'Flat Maps|Unused / Inactive', joined) or re.search(r'\((unused|inactive|flat)', title):
        if UNUSED not in out:
            out.append(UNUSED)
    return out


LEVELS = {'HIGH': 'HIGH', 'MEDIUM': 'MEDIUM', 'LOW': 'LOW', 'VERIFIED': 'VERIFIED', 'TRACED': 'HIGH',
          'CONFIRMED': 'HIGH', 'HAND-DECODED': 'MEDIUM'}


def confidence(desc):
    for pat in (r'(?:TRACED|DECODED) \([^)]*confidence ([\w-]+)\)', r'^CONFIDENCE: ([\w-]+)', r'Confidence: ([\w-]+)'):
        m = re.search(pat, desc, re.M | re.I)
        if m and m.group(1).upper() in LEVELS:
            return LEVELS[m.group(1).upper()]
    return ''


def _cut(s, n):
    s = ' '.join(s.split())
    if len(s) <= n:
        return s
    end = max(s.rfind('. ', 0, n - 3), s.rfind('; ', 0, n - 3))
    if end >= n // 2:
        return s[:end + 1] if s[end] == '.' else s[:end] + '...'
    return s[:s.rfind(' ', 0, n - 3)].rstrip(',;:') + '...'


def summary(desc):
    # code excerpts ("USAGE (decompiled...):" lines) stay in the notes CSV only
    desc = re.sub(r'USAGE \([^)]*\):.*?(?=COMPARED WITH|\n\n|\Z)', '', desc, flags=re.S)
    paras = [p.strip() for p in desc.split('\n\n') if p.strip()]
    for p in paras:
        m = re.match(r'(?:TRACED|DECODED) \([^)]*\): (.*)', p, re.S)
        if m:
            s = m.group(1).split('\nCODE ')[0]
            return _cut(re.sub(r'^FUN_[0-9A-Fa-f]+: ', '', s), SUMMARY_MAX)
    for p in paras:
        if not p.startswith(HEADS):
            return _cut(re.sub(r'^FUNCTION: ', '', p), SUMMARY_MAX)
    return ''


def value_line(desc):
    lines = []
    for p in desc.split('\n\n'):
        p = p.strip()
        if p.startswith(('VALUES', 'STOCK', 'SD-v4.1 VALUE')):
            p = p.split('\n')[0]
            lines.append(_cut(re.sub(r'\s*ADDRESS 0x[0-9A-Fa-f]+, \d+-bit\.?', '', p), VALUE_MAX))
    return lines


def address(blk):
    z = re.search(r'<XDFAXIS id="z".*?mmedaddress="(0x[0-9A-Fa-f]+)"', blk, re.S) or \
        re.search(r'mmedaddress="(0x[0-9A-Fa-f]+)"', blk)
    return '0x%X' % int(z.group(1), 16) if z else ''


def short_desc(desc, addr, race_changed_text):
    parts = [summary(desc)] + value_line(desc)
    tags = []
    conf = confidence(desc)
    if conf:
        tags.append('Confidence %s.' % conf)
    if race_changed_text and race_changed_text in desc:
        tags.append('CHANGED BY RACE SOFTWARE vs stock.')
    elif 'DIFFERS FROM 5JCZSJ10' in desc:
        tags.append('DIFFERS FROM 5JCZSJ10 (notes describe 5JCZSJ10).')
    if 'NOT tunable' in desc or 'do not edit' in desc.lower():
        tags.append('Do not edit.')
    tags.append('@%s - full notes: docs/xdf-notes.csv' % addr)
    parts.append(' '.join(tags))
    out = '\n'.join(p for p in parts if p)
    while len(out) > DESC_SHORT:  # only the summary is variable enough to need it
        parts[0] = _cut(parts[0], len(parts[0]) - (len(out) - DESC_SHORT) - 4)
        out = '\n'.join(p for p in parts if p)
    return out


def finalize(text, notes=None, race_changed_text=None):
    """Return text with workflow folders and short descriptions. If notes is a list, append
    (address, type, title, folder, full description) for every item."""
    old_cats = {int(i, 16): n for i, n in re.findall(r'<CATEGORY index="(0x[0-9A-Fa-f]+)" name="([^"]*)"', text)}
    if old_cats and all(n in FOLDERS for n in old_cats.values()):
        sys.exit('finalize() called twice on the same text')

    def folders_of(blk):
        el = ET.fromstring(blk)
        title = el.findtext('title') or ''
        desc = el.findtext('description') or ''
        old = [old_cats[int(c.get('category')) - 1] for c in el.findall('CATEGORYMEM')]
        return title, desc, folders_for(title, old, desc)

    # only the folders this file uses (the race folder is empty in a stock XDF), in FOLDERS order
    used = {f for m in BLOCK.finditer(text) for f in folders_of(m.group(0))[2]}
    folders_used = [f for f in FOLDERS if f in used]
    index = {f: i for i, f in enumerate(folders_used)}

    def item(m):
        blk = m.group(0)
        title, desc, folders = folders_of(blk)
        addr = address(blk)
        if notes is not None:
            notes.append((addr, m.group(1)[3:].lower(), title, folders[0], desc))
        mem = ''.join('    <CATEGORYMEM index="%d" category="%d" />\n' % (k, index[f] + 1)
                      for k, f in enumerate(folders))
        first = re.search(r'[ \t]*<CATEGORYMEM\b[^>]*/>', blk)
        if first:  # old memberships may share a line: drop them all, then the line they leave empty
            at = first.start()
            rest = re.sub(r'[ \t]*<CATEGORYMEM\b[^>]*/>', '', blk[at:])
            blk = blk[:at] + mem + (rest[1:] if rest.startswith('\n') else rest)
        else:
            at = blk.index('\n', blk.index('</description>' if '</description>' in blk else '</title>')) + 1
            blk = blk[:at] + mem + blk[at:]
        new = short_desc(desc, addr, race_changed_text)
        if '<description>' in blk:
            blk = re.sub(r'<description>.*?</description>', lambda _: '<description>%s</description>'
                         % escape(new, quote=False), blk, count=1, flags=re.S)
        else:
            blk = blk.replace('</title>', '</title>\n    <description>%s</description>' % escape(new, quote=False), 1)
        return blk

    text = BLOCK.sub(item, text)
    cat_xml = ''.join('    <CATEGORY index="0x%X" name="%s" />\n' % (i, escape(f)) for i, f in enumerate(folders_used))
    text = re.sub(r'(    <CATEGORY index="0x[0-9A-Fa-f]+" name="[^"]*" />\n)+', lambda _: cat_xml, text, count=1)
    return text


def check(root, max_desc=DESC_SHORT):
    """Every item has exactly one main folder, a known folder list and a short description."""
    names = [c.get('name') for c in root.find('XDFHEADER').findall('CATEGORY')]
    assert names and all(f in FOLDERS for f in names), names
    n = len(names)
    for e in root:
        if e.tag in ('XDFTABLE', 'XDFCONSTANT', 'XDFFLAG'):
            mems = e.findall('CATEGORYMEM')
            assert mems and mems[0].get('index') == '0', e.findtext('title')
            assert all(1 <= int(c.get('category')) <= n for c in mems), e.findtext('title')
            assert len(e.findtext('description') or '') <= max_desc, e.findtext('title')


def main():
    """Write docs/xdf-notes.csv: the full description of every item in the stock master and the race XDF."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import make_stock_xdfs as ms
    import make_race_xdf as mr
    stock, race = [], []
    finalize(open(ms.MASTER, encoding='utf-8').read(), stock)
    finalize(mr.build_race()[0], race)
    race_addrs = {'0x%X' % a for a in mr.OVERRIDE_TABLES | mr.OVERRIDE_CONSTS | mr.ADD_CONSTS}
    rows = [('stock (5JCZSJ10 values)',) + r for r in stock]
    rows += [('race SD-v6 (SD-v4.1 values)',) + r for r in race if r[0] in race_addrs]
    rows.sort(key=lambda r: (r[4], r[3], r[0]))
    with open(NOTES, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(('source', 'address', 'type', 'title', 'folder', 'full_notes'))
        w.writerows(rows)
    print('%s: %d stock items + %d race-specific rows' % (os.path.relpath(NOTES, ROOT), len(stock), len(rows) - len(stock)))
    import xdf_funcnames
    xdf_funcnames.main()        # refresh docs/function-registry.csv from the new notes


if __name__ == '__main__':
    main()
