#!/usr/bin/env python3
"""Re-stamp the field-1 CRC of a Gen 3 Hayabusa 2 MB read (5JCZSJ10 / 5JCZSJ40).

CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF, no reflection, no xorout) over
file offsets 0x10000..0x1FFAFB inclusive, stored BIG-endian at 0x1FFAFE.
Verified against the stock 5JCZSJ10 read (stored 0x7DA2 == computed 0x7DA2).
Field 3 (0x1FFEF8) is NOT touched - see the XDF "Checksums / Signatures" notes.

usage: python3 fix_field1_crc.py tuned.bin            (writes in place, prints old/new)
       python3 fix_field1_crc.py tuned.bin --check    (only reports)
"""
import sys, binascii
fn = sys.argv[1]
b = bytearray(open(fn, 'rb').read())
assert len(b) == 0x200000, 'expected a full 2 MB read'
assert b[0x1FFAF4:0x1FFAFC] == bytes.fromhex('00000100fbfa1f00'), 'field-1 range words not found - wrong file?'
calc = binascii.crc_hqx(bytes(b[0x10000:0x1FFAFC]), 0xFFFF)
stored = int.from_bytes(b[0x1FFAFE:0x1FFB00], 'big')
print('stored 0x%04X  computed 0x%04X  %s' % (stored, calc, 'OK' if stored == calc else 'MISMATCH'))
if '--check' not in sys.argv and stored != calc:
    b[0x1FFAFE:0x1FFB00] = calc.to_bytes(2, 'big')
    open(fn, 'wb').write(b)
    print('written')
