"""Offline preparation only: detach spare TPS readers and reserve a boost profile.

This does NOT install race_control.c into the ECU or claim a physical PWM driver.
The first TPS base/blend pair per cylinder and all neutral TPS maps stay intact.
"""
import struct
import xml.etree.ElementTree as ET

PROFILE_ADDRESS = 0x170440  # Cyl 1 TPS spare 1 Z storage (2600 bytes)
PROFILE_SIZE = 576
DESCRIPTOR = 0x156478
DETACH_ADDRESS = 0x453B0
DETACH_BASE = bytes.fromhex('66e2')
DETACH_PATCH = bytes.fromhex('62e2')  # Ghidra V850E3V5 assembler: cmp 0x2,r28


def profile_bytes():
    b = bytearray(PROFILE_SIZE)
    b[:8] = b'RACEWG01'
    def word(offset, value):
        struct.pack_into('<H', b, offset, value)
    word(8, PROFILE_SIZE)
    word(10, 1)
    b[12] = 0  # core disabled; no firmware runtime installed
    b[13] = 0  # zero-based O2 channel 1
    for offset, value in {14:31, 16:1000, 18:9000, 20:27000, 22:5000,
                          24:0, 26:0, 28:3000, 30:3000, 32:400, 34:4600,
                          36:400, 38:4600, 40:50, 42:50, 44:600}.items():
        word(offset, value)
    for i in range(16):
        word(64 + 2*i, i*1000)
    for i in range(7):
        word(96 + 2*i, i)
    # Targets and base duty remain zero. They are NOT an engine/boost tune.
    return bytes(b)


def embedded(parent, address, bits=16, **extra):
    return ET.SubElement(parent, 'EMBEDDEDDATA',
                         mmedtypeflags='0x02', mmedaddress='0x%X' % address,
                         mmedelementsizebits=str(bits), mmedmajorstridebits='0',
                         mmedminorstridebits='0', **{k:str(v) for k,v in extra.items()})


def math(parent, equation):
    m = ET.SubElement(parent, 'MATH', equation=equation)
    ET.SubElement(m, 'VAR', id='X')


def prepare(image, root):
    if image[DETACH_ADDRESS:DETACH_ADDRESS+2] != DETACH_BASE:
        raise ValueError('TPS lookup loop does not match audited cmp 6,r28')
    # The original descriptor has one pointer, slot 2 of the six-table family.
    needle = struct.pack('<I', DESCRIPTOR)
    occurrences = [i for i in range(len(image)-3) if image[i:i+4] == needle]
    if occurrences != [0x17EBEC]:
        raise ValueError('unexpected TPS spare descriptor consumer')
    if struct.unpack_from('<I', image, DESCRIPTOR+12)[0] != PROFILE_ADDRESS:
        raise ValueError('TPS spare descriptor data pointer changed')
    old = None
    for table in root.findall('XDFTABLE'):
        z = table.find("XDFAXIS[@id='z']/EMBEDDEDDATA")
        if z is not None and int(z.get('mmedaddress'),16) == PROFILE_ADDRESS:
            if (int(z.get('mmedcolcount')), int(z.get('mmedrowcount')),
                    int(z.get('mmedelementsizebits'))) != (26,50,16):
                raise ValueError('unexpected TPS spare dimensions')
            old = table
            break
    if old is None:
        raise ValueError('missing TPS spare definition')
    image[DETACH_ADDRESS:DETACH_ADDRESS+2] = DETACH_PATCH
    image[PROFILE_ADDRESS:PROFILE_ADDRESS+PROFILE_SIZE] = profile_bytes()
    root.remove(old)
    header = root.find('XDFHEADER')
    category = max(int(c.get('index'),16) for c in header.findall('CATEGORY')) + 1
    ET.SubElement(header, 'CATEGORY', index='0x%X' % category,
                  name='21 Boost preparation - NO ECU runtime driver')
    used = {int(e.get('uniqueid'),16) for e in root if e.get('uniqueid')}
    uid = 0xF000
    def item(tag, title, address, eq, units, bits=16):
        nonlocal uid
        while uid in used:
            uid += 1
        used.add(uid)
        e = ET.SubElement(root, tag, uniqueid='0x%X' % uid, flags='0x0')
        uid += 1
        ET.SubElement(e,'title').text = 'RESERVED (runtime absent) :: ' + title
        ET.SubElement(e,'description').text = (
            'Stored calibration only. Portable controller source is NOT installed in ECU. '
            'No solenoid/pressure feedback behavior is enabled by editing this item. '
            'Original TPS spare reader is detached. @0x%X' % address)
        ET.SubElement(e,'CATEGORYMEM',index='0',category=str(category+1))
        if tag == 'XDFCONSTANT':
            embedded(e, address, bits)
            ET.SubElement(e,'units').text = units
            ET.SubElement(e,'decimalpl').text = '2'
            ET.SubElement(e,'datatype').text = '0'
            ET.SubElement(e,'unittype').text = '0'
            ET.SubElement(e,'DALINK',index='0')
            math(e,eq)
        return e
    for address, title, units in ((PROFILE_ADDRESS+128,'Hat pressure target vs RPM / gear','PSI'),
                                  (PROFILE_ADDRESS+352,'Base solenoid duty vs RPM / gear','%')):
        t = item('XDFTABLE',title,address,'X/100',units)
        for name, addr, count, unit in [('x',PROFILE_ADDRESS+64,16,'RPM'),
                                      ('y',PROFILE_ADDRESS+96,7,'gear (0=N)')]:
            ax = ET.SubElement(t,'XDFAXIS',id=name,uniqueid='0x0')
            embedded(ax,addr,mmedcolcount=count)
            ET.SubElement(ax,'units').text = unit
            ET.SubElement(ax,'indexcount').text = str(count)
            ET.SubElement(ax,'decimalpl').text = '0'
            ET.SubElement(ax,'embedinfo',type='1')
            ET.SubElement(ax,'datatype').text = '0'
            ET.SubElement(ax,'unittype').text = '0'
            ET.SubElement(ax,'DALINK',index='0')
            math(ax,'X')
        z = ET.SubElement(t,'XDFAXIS',id='z')
        embedded(z,address,mmedrowcount=7,mmedcolcount=16)
        ET.SubElement(z,'units').text=units
        ET.SubElement(z,'decimalpl').text='2'
        ET.SubElement(z,'outputtype').text='1'
        math(z,'X/100')
    for off,title,unit,eq in [(20,'MAP absolute ceiling','kPa abs','X/100'),
                             (22,'Hat pressure ceiling','PSI','X/100'),
                             (24,'Hat PI proportional gain','duty bp/PSI','X'),
                             (26,'Hat PI integral gain','duty bp/(PSI*s)','X')]:
        item('XDFCONSTANT',title,PROFILE_ADDRESS+off,eq,unit)
    return {'status':'PREPARATION ONLY - controller source is not installed in ECU',
            'profile_address':PROFILE_ADDRESS,'profile_size':PROFILE_SIZE,
            'profile_signature':'RACEWG01','enabled':False,'o2_channel':1,
            'pwm_hz':31,'hat_target_units':'PSI * 100','duty_units':'basis points',
            'detached_lookup':{'address':DETACH_ADDRESS,'base':DETACH_BASE.hex(),
                               'patch':DETACH_PATCH.hex(),'effect':'six TPS lookups reduced to first two per cylinder'},
            'preserved':'main/blend TPS pair and neutral TPS tables; stock fault fallback',
            'runtime_driver_installed':False,'controller_source':'race/control/race_control.c'}
