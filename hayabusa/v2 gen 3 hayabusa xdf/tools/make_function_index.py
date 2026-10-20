#!/usr/bin/env python3
"""Build the function-index spreadsheet for the v2 Hayabusa XDFs (for CalStudio).

One row per decompiled function referenced anywhere in the definition, with:
  address, fun_handle, name (readable if identified, else blank), subsystem,
  xdf_refs (how many XDF items cite it), maps_read (sample tables it looks up),
  signals_read (RAM sensor variables it reads), functional_note.

The functional_note is synthesised even for un-named functions from what the function actually
touches in the decompile (the maps it interpolates + the sensor variables feeding them), so every
function has a usable description rather than a bare FUN_ handle.

All eight stock Hayabusa reads share byte-identical code (0x10000-0x14FFFF), so this one index
applies to every Hayabusa v2 XDF; it is written once as docs/function-index.csv and, for literal
per-file parity in CalStudio, copied to <software>-function-index.csv beside each XDF.

usage: python3 make_function_index.py
"""
import csv
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import busa_v2_common as C  # noqa: E402

REGISTRY = os.path.join(C.HAYA, 'docs/function-registry.csv')
FUNC_NAMES = os.path.join(C.HAYA, 'docs/function-names.csv')
OUT = os.path.join(C.V2, 'docs/function-index.csv')

SUBSYS_KEYS = [
    ('Quickshifter', 'Quickshifter'), ('Launch', 'Launch Control'), ('TC ', 'Traction Control'),
    ('Traction', 'Traction Control'), ('Limiter', 'Limiters'), ('IGN', 'Ignition'),
    ('Ignition', 'Ignition'), ('TPS', 'Fuel'), ('IAP', 'Fuel'), ('Injector', 'Fuel'),
    ('Fuel', 'Fuel'), ('Accel Enrich', 'Fuel'), ('Decel', 'Fuel'), ('ETV', 'Throttle/ETV'),
    ('Throttle', 'Throttle/ETV'), ('PWR', 'Throttle/ETV'), ('Ride Mode', 'Ride Modes'),
    ('Idle', 'Idle/Fan'), ('Fan', 'Idle/Fan'), ('HO2', 'O2/Closed Loop'), ('Cruise', 'Cruise'),
    ('Engine Brake', 'Engine Brake'), ('Anti-Lift', 'Anti-Lift'), ('Pitch', 'Anti-Lift'),
    ('Wheel Speed', 'Wheel/IMU'), ('IMU', 'Wheel/IMU'), ('Gear', 'Gear'), ('DTC', 'Diagnostics'),
    ('Monitor', 'Diagnostics'), ('Sensor', 'Sensors'), ('OBD', 'Diagnostics'), ('Meter', 'Meter/CAN'),
]


def func_hex(a):
    return 'FUN_%08X' % a


def main():
    names = {}
    for r in csv.DictReader(open(FUNC_NAMES)):
        if r.get('address', '').startswith('0x'):
            names[int(r['address'], 16)] = r['name'].strip()

    # function -> maps it reads (from the decompile map_links.csv); and the maps' axis meanings
    fmaps = {}
    for r in csv.DictReader(io.StringIO(C._zip_text('map_links.csv'))):
        fn = (r.get('function') or '').strip()
        if not fn:
            continue
        m = re.search(r'([0-9a-fA-F]{4,})', fn)
        if not m:
            continue
        a = int(m.group(1), 16)
        sigs = []
        for ax in ('x_input_meaning', 'y_input_meaning'):
            v = (r.get(ax) or '').strip()
            if v:
                sigs.append(v)
        fmaps.setdefault(a, {'maps': [], 'sigs': set()})
        fmaps[a]['maps'].append(r['table'].strip())
        fmaps[a]['sigs'].update(sigs)

    def subsystem(maps):
        for t in maps:
            for key, tag in SUBSYS_KEYS:
                if key.lower() in t.lower():
                    return tag
        return ''

    rows = []
    for r in csv.DictReader(open(REGISTRY)):
        try:
            a = int(r['address'], 16)
        except ValueError:
            continue
        name = names.get(a, '') or ('' if r['name'].strip().lower() == 'unidentified' else r['name'].strip())
        mm = fmaps.get(a, {'maps': [], 'sigs': set()})
        maps = list(dict.fromkeys(mm['maps']))
        sub = subsystem(maps)
        sigs = sorted(mm['sigs'])
        if name:
            note = name
        elif maps:
            note = 'reads %d map(s), e.g. %s' % (len(maps), '; '.join(maps[:2]))
        else:
            note = 'referenced in XDF notes; role not individually identified'
        rows.append((r['address'], func_hex(a), name, sub, r.get('references_in_notes', ''),
                     '; '.join(maps[:3]), ', '.join(sigs[:4]), note))
    rows.sort(key=lambda x: int(x[0], 16))
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(('address', 'fun_handle', 'name', 'subsystem', 'xdf_refs',
                    'maps_read', 'signals_read', 'functional_note'))
        w.writerows(rows)
    named = sum(1 for r in rows if r[2])
    withmaps = sum(1 for r in rows if r[5])
    print('%s: %d functions (%d named, %d with decompiled map reads)'
          % (os.path.relpath(OUT, C.ROOT), len(rows), named, withmaps))
    # literal per-read copies (identical code across all 8 stock reads)
    import shutil
    for sw in ('5JCZSJ00', '5JCZSJ10', '5JCZSJ20', '5JCZSJ30', '5JCZSJ40', '5JCZSJA0', '5JCZSJB0', '5JCZSNC0'):
        if os.path.exists(os.path.join(C.V2, '%s-v2.xdf' % sw)):
            shutil.copyfile(OUT, os.path.join(C.V2, '%s-function-index.csv' % sw))
    print('   copied per-read function-index CSVs beside each XDF')


if __name__ == '__main__':
    main()
