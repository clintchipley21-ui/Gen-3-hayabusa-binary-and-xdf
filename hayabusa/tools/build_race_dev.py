#!/usr/bin/env python3
"""Build an OFFLINE DEVELOPMENT SD + ALS + air-shift image, XDF and manifest.

No boost-output driver or full MAP-based base ignition is installed. TPS fuel
storage remains live in fault paths and MUST NOT be repurposed by this builder.
Accepts exact supported stock reads only; existing edited/patch images are rejected.
"""
import argparse
import bisect
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import apply_patches as ap
import make_stock_xdfs as ms

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'stock/5JCZSJ40/5JCZSJ40.bin': '676daf1c0048e9d0622b4ab2466f3e98e22e29623185d1c602698700f63c0c8d',
    'race/old/SD-v3.bin': '1c9551cc4f176a799dbd886f37824c84e0535a347c8f8dcd63f08caf61f0247c',
    'race/Busa-SD-v4.1.bin': '5af12da86686cd6441b1d8a319f99bd2b92521daf50c4d3f762eedeebc6fa7c0',
    'race/als/autoshift.bin': 'dc9fcddcd9c86c46bd3a4c1895305762eb6663a39d86cf7d7fc61032e931026a',
    'race/Busa-SD-v6.xdf': '0387ed644800a7193b743db7e8a341d3376b802dd2b1353e9b8d1e3b935431ff',
}
STOCK_HASHES = {
    '68f9a893797f8dceb00d600529872a5ff5470f18b63db4067e6e360082a1a4f7': '5JCZSJ00',
    'c790a44631ea78ee17e5dbcb35a4b8a1ae1a91fd0de5772634c5e2a14bb32e54': '5JCZSJ10',
    '9d10bf24949bdee43e860a688ccab1110680e0d6f95f45839b848ec4d46510a1': '5JCZSJ20',
    'a3a81f3e443d9456abefa927ef0862066282b97ed1a13ca4dd9379d9243079bf': '5JCZSJ30',
    '676daf1c0048e9d0622b4ab2466f3e98e22e29623185d1c602698700f63c0c8d': '5JCZSJ40',
    'a112eb07d29ae270a7e0759fb225bb44e987ce3a97e3378b50db2cdc21a31b56': '5JCZSJA0',
    '1d2fa485bc5a80d36922eac7be2e83bf80b906f1bb7339c8853fe231edca37d2': '5JCZSNC0',
}
SD_TABLES = {0x159BB8, 0x15E460, 0x162D08, 0x1675B0,
             0x16BEB8, 0x16CAD4, 0x16D6F0, 0x16E30C, 0x188214, 0x188598}
PROVISIONAL_A, PROVISIONAL_B = 0.307429, -12.6
# Supplier-published 312.5-kPa normalized span / -11.25-kPa offset.
# Assumes a ratiometric 10-bit ADC; not a bench-validated OEM sensor definition.
GM_55567257_CANDIDATE = (312.5 / 1023, -11.25, 270)
CRC_ADDRS = {0x1FFAFE, 0x1FFAFF}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def reference(path):
    data = (ROOT / path).read_bytes()
    if sha(data) != PINS[path]:
        raise ValueError('reference SHA-256 mismatch: ' + path)
    return data


def ranges(addresses):
    result = []
    for a in sorted(addresses):
        if result and a == result[-1][1]:
            result[-1][1] += 1
        else:
            result.append([a, a + 1])
    return result


def read_u16(data, address):
    return int.from_bytes(data[address:address + 2], 'little')


def write_int(data, address, value, width):
    data[address:address + width] = int(value).to_bytes(width, 'little')


def interpolate(xs, ys, x):
    i = max(0, min(len(xs) - 2, bisect.bisect_right(xs, x) - 1))
    x = max(xs[0], min(xs[-1], x))
    return ys[i] + (ys[i + 1] - ys[i]) * (x - xs[i]) / (xs[i + 1] - xs[i])


def sensor_rescale(image, root, slope, offset, ceiling):
    """Re-axis AND resample all SD/retard Z rows in physical pressure units.

    The provisional transfer in the original project is an assumption, not a GM
    part-number specification. Callers must supply the measured/datasheet curve.
    """
    if not all(math.isfinite(v) for v in (slope, offset, ceiling)) or slope <= 0:
        raise ValueError('sensor values must be finite and slope positive')
    if not 100 < ceiling <= 300:
        raise ValueError('pressure ceiling must be >100 and <=300 kPa absolute')
    gain = round(393.14 * slope * 10925 / 32)
    bias = round(32768 + 393.14 * offset)
    if not (0 < gain <= 65535 and 0 <= bias <= 65535):
        raise ValueError('sensor curve cannot be represented by stock conversion')
    source = bytes(image)
    updates = {}
    found = set()
    for table in root.findall('XDFTABLE'):
        z = table.find("XDFAXIS[@id='z']/EMBEDDEDDATA")
        if z is None:
            continue
        address = int(z.get('mmedaddress'), 16)
        if address not in SD_TABLES:
            continue
        found.add(address)
        x = table.find("XDFAXIS[@id='x']")
        xe = x.find('EMBEDDEDDATA')
        xa = int(xe.get('mmedaddress'), 16)
        n = int(xe.get('mmedcolcount'))
        old = [read_u16(source, xa + i * 2) * PROVISIONAL_A + PROVISIONAL_B for i in range(n)]
        # Keep the original non-uniform spacing, limited to this sensor's ceiling.
        desired = [20 + (p - old[0]) * (ceiling - 20) / (old[-1] - old[0]) for p in old]
        raw = [round((p - offset) / slope) for p in desired]
        low_fault = read_u16(image, 0x1547E0)
        high_fault = read_u16(image, 0x1547E2)
        if raw[0] <= low_fault or raw[-1] >= high_fault:
            raise ValueError('axis extends into IAP circuit-fault region; use a lower ceiling or correct sensor curve')
        if any(a >= b for a, b in zip(raw, raw[1:])):
            raise ValueError('sensor axis is not strictly increasing')
        actual = [r * slope + offset for r in raw]
        for i, value in enumerate(raw):
            a = xa + i * 2
            encoded = value.to_bytes(2, 'little')
            if a in updates and updates[a] != encoded:
                raise ValueError('inconsistent shared axis')
            updates[a] = encoded
        rows, cols = int(z.get('mmedrowcount')), int(z.get('mmedcolcount'))
        width = int(z.get('mmedelementsizebits')) // 8
        if cols != n or z.get('mmedmajorstridebits', '0') != '0' or z.get('mmedminorstridebits', '0') != '0':
            raise ValueError('unexpected SD table layout')
        for row in range(rows):
            base = address + row * cols * width
            values = [int.from_bytes(source[base + i * width:base + (i + 1) * width], 'little') for i in range(cols)]
            for i, pressure in enumerate(actual):
                write_int(image, base + i * width, round(interpolate(old, values, pressure)), width)
        x.find('MATH').set('equation', 'X*%.12g%+.12g' % (slope, offset))
    if found != SD_TABLES:
        raise ValueError('missing SD/retard definitions')
    for a, value in updates.items():
        image[a:a + 2] = value
    write_int(image, 0x18EF58, gain, 2)
    write_int(image, 0x18EF5A, bias, 2)
    return {'id': 'user-specified transfer', 'kpa_per_adc_count': slope,
            'kpa_offset': offset, 'ceiling_kpa_absolute': ceiling,
            'gain': gain, 'offset_word': bias, 'verified_on_hardware': False}


def build(base, sensor=None):
    if len(base) != ap.SIZE:
        raise ValueError('expected exactly 2 MiB')
    variant = STOCK_HASHES.get(sha(base))
    if variant is None:
        raise ValueError('unsupported/modified base; 5JCZSJB0 requires a separate SD calibration port')
    stock = reference('stock/5JCZSJ40/5JCZSJ40.bin')
    sd3 = reference('race/old/SD-v3.bin')
    sd4 = reference('race/Busa-SD-v4.1.bin')
    reference('race/als/autoshift.bin')
    image = bytearray(base)
    writes = []
    def install(name, a, expected, replacement):
        if bytes(image[a:a + len(expected)]) != expected:
            raise ValueError('%s base mismatch at 0x%X' % (name, a))
        image[a:a + len(replacement)] = replacement
        writes.append({'feature': name, 'address': a, 'length': len(replacement)})
    sd_addresses = {i for i, (s, d) in enumerate(zip(stock, sd3)) if s != d} - CRC_ADDRS
    for a, end in ranges(sd_addresses):
        install('speed-density v3', a, stock[a:end], sd3[a:end])
    entries = ap.entries(stock, sd4)
    for name in ('antilag', 'autoshift'):
        for a, expected, replacement in entries[name]:
            # ALS intentionally replaces the SD-v3 neutral boost-retard map.
            if name == 'antilag' and a == 0x188214:
                expected = sd3[a:a + len(replacement)]
            install(name, a, expected, replacement)
    if image[0xBF000] != 0 or image[0xBF010:0xBF012] != b'\0\0':
        raise ValueError('race feature defaults must be OFF')
    root = ET.fromstring(reference('race/Busa-SD-v6.xdf').decode('utf-8'))
    if sensor is not None:
        sensor_info = sensor_rescale(image, root, *sensor)
    else:
        sensor_info = {'id': 'inherited PROVISIONAL 3-bar assumption; not a verified GM transfer',
                       'kpa_per_adc_count': PROVISIONAL_A, 'kpa_offset': PROVISIONAL_B,
                       'ceiling_kpa_absolute': 300, 'verified_on_hardware': False}
    ap.crc_stamp(image)
    # Refresh per-image values, including variant-specific calibration kept from the base.
    # ms.build appends these two identity definitions unconditionally.
    for item in list(root):
        if item.get('uniqueid') in ('0xC00D', '0xC00E'):
            root.remove(item)
    text, _ = ms.build(ET.tostring(root, encoding='unicode'), stock, image, 'Race-dev', ms.PARTS[variant])
    root = ET.fromstring(text)
    root.find('XDFHEADER/deftitle').text = 'Hayabusa %s - Race DEVELOPMENT (SD / ALS / air-shift)' % variant
    root.find('XDFHEADER/description').text = (
        'OFFLINE DEVELOPMENT: ' + variant + ' + SD/ALS/air-shift. ALS and shift OFF. '
        'TPS fallback remains active: DO NOT reuse its storage. Base spark remains TPS-based '
        'with MAP retard. No boost-output driver. Sensor transfer requires calibration. '
        'Field 3 unchanged/unverified; bench validation required. See manifest and development notes.')
    for table in root.findall('XDFTABLE'):
        z = table.find("XDFAXIS[@id='z']/EMBEDDEDDATA")
        if z is None:
            continue
        address = int(z.get('mmedaddress'), 16)
        if address in (0x1544D4, 0x154500):
            table.find('title').text = 'HO2 correction/diagnostic limit - driver role UNVERIFIED'
            table.find('description').text = (
                'Do not use this as a wastegate PWM duty map. Its readers compare sums of '
                'HO2 correction values; a physical heater driver has not been established. '
                'Original heater-duty title was a low-confidence inference. @0x%X' % address)
        title = table.find('title')
        if title is not None and (title.text or '').startswith('TPS -'):
            title.text = 'TPS STORAGE - NOT RELEASED :: ' + title.text
            table.find('description').text = (
                'Original TPS table storage retained. The ECU still reads this table family; '
                'main TPS maps remain selectable during IAP faults. Blend/spare selection varies. '
                'Do not repurpose until all consumers are addressed. @0x%X' % address)
        if address in SD_TABLES and sensor is not None:
            table.find('description').text = (
                'Development SD/retard map, re-axised and linearly resampled in physical pressure '
                'for the supplied sensor transfer. Values are starting calibration only. '
                'Base ignition remains TPS-based. @0x%X' % address)
    for desc in root.findall('./*/description'):
        if desc.text and len(desc.text) > 420:
            desc.text = desc.text[:399] + ' [See source notes.]'
    changed = {i for i, (s, d) in enumerate(zip(base, image)) if s != d}
    manifest = {
        'status': 'OFFLINE DEVELOPMENT - NOT FLASH VALIDATED',
        'base_variant': variant, 'base_sha256': sha(base), 'image_sha256': sha(image),
        'reference_sha256': PINS, 'sensor': sensor_info,
        'features': {'sd_fuel': True, 'rolling_antilag': 'installed, OFF',
                     'airshift': 'installed, OFF; output unverified',
                     'map_based_base_ignition': False, 'map_based_retard': True,
                     'boost_output_control': False, 'tps_storage_reclaimed': False},
        'field1_crc': '%04X' % int.from_bytes(image[0x1FFAFE:0x1FFB00], 'big'),
        'field3': 'unchanged; enforcement/algorithm not established',
        'changed_byte_count': len(changed), 'install_regions': writes,
        'changed_ranges': [{'address': a, 'length': e - a} for a, e in ranges(changed)],
    }
    return bytes(image), ET.tostring(root, encoding='unicode') + '\n', manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stock_bin', type=Path)
    parser.add_argument('output_prefix', type=Path)
    parser.add_argument('--sensor-slope', type=float, help='kPa per raw ADC count, NOT kPa/V')
    parser.add_argument('--sensor-offset', type=float, help='kPa offset')
    parser.add_argument('--max-kpa', type=float, help='absolute pressure ceiling, e.g. 250 for a 2.5-bar range')
    parser.add_argument('--sensor-preset', choices=['gm-55567257-candidate'],
                        help='supplier-published transfer; ADC/electrical validation still required')
    args = parser.parse_args()
    if args.sensor_preset:
        if args.sensor_slope is not None or args.sensor_offset is not None:
            parser.error('preset cannot be combined with slope/offset overrides')
        values = (GM_55567257_CANDIDATE[0], GM_55567257_CANDIDATE[1],
                  args.max_kpa if args.max_kpa is not None else GM_55567257_CANDIDATE[2])
    else:
        values = (args.sensor_slope, args.sensor_offset, args.max_kpa)
    if any(v is not None for v in values) and not all(v is not None for v in values):
        parser.error('supply --sensor-slope, --sensor-offset and --max-kpa together')
    targets = [Path(str(args.output_prefix) + suffix) for suffix in ('.bin', '.xdf', '.json')]
    if any(p.exists() for p in targets) or args.stock_bin.resolve() in [p.resolve() for p in targets]:
        parser.error('output exists or would overwrite the input; use a new prefix')
    try:
        image, xdf, manifest = build(args.stock_bin.read_bytes(), values if values[0] is not None else None)
    except ValueError as error:
        parser.error(str(error))
    if args.sensor_preset:
        manifest['sensor'].update({
            'id': 'GM 55567257 CANDIDATE - supplier-published transfer, bench verification required',
            'source': 'https://dsxtuning.com/products/gm-3-bar-map-55567257',
            'assumption': '312.5 kPa normalized span, -11.25 kPa offset, ratiometric raw/1023',
        })
    targets[0].parent.mkdir(parents=True, exist_ok=True)
    targets[0].write_bytes(image)
    targets[1].write_text(xdf)
    targets[2].write_text(json.dumps(manifest, indent=2) + '\n')
    print('Built ' + ', '.join(map(str, targets)))
    print('OFFLINE DEVELOPMENT: no boost-output driver, no TPS storage reuse, no full SD base ignition.')


if __name__ == '__main__':
    main()
