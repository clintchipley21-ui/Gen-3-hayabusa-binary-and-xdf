#!/usr/bin/env python3
"""Cross-compile the boost core for V850E3V5, independently of an ECU adapter.

Produces relocatable objects, disassembly and metadata ONLY. It does not patch a
BIN, choose ECU hooks/pins, allocate runtime RAM, or claim target execution tests.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prefix',required=True,help='tool prefix, e.g. /opt/cross/bin/v850-elf-')
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--profile-bin',type=Path,help='optional prepared development image for emulator self-test fixture')
    a=p.parse_args()
    if a.out.exists():
        p.error('output exists; use a fresh directory')
    source=Path(__file__).resolve().parent
    flags=['-mv850e3v5','-Os','-std=c99','-ffreestanding','-fno-builtin',
           '-fno-common','-fno-pic','-fno-stack-protector',
           '-msda=0','-mtda=0','-mzda=0','-Wall','-Wextra','-Werror']
    compiler=a.prefix+'gcc'
    version=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0]
    a.out.mkdir(parents=True)
    objects=[]
    for name,file in [('race_control','race_control.c'),('race_memory','freestanding/memory.c')]:
        obj=a.out/(name+'.o')
        subprocess.run([compiler,*flags,'-I'+str(source/'freestanding'),
                        '-c',str(source/file),'-o',str(obj)],check=True)
        # GNU V850 GAS can emit an unreferenced undefined r31 symbol for
        # register operands. objcopy refuses removal if a relocation uses it.
        subprocess.run([a.prefix+'objcopy','--strip-symbol=r31',str(obj)],check=True)
        disasm=subprocess.check_output([a.prefix+'objdump','-dr',str(obj)],text=True)
        (a.out/(name+'.disassembly.txt')).write_text(disasm)
        undefined=subprocess.check_output([a.prefix+'nm','-u',str(obj)],text=True)
        objects.append({'object':obj.name,'source':file,
                        'source_sha256':hashlib.sha256((source/file).read_bytes()).hexdigest(),
                        'sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
                        'undefined_symbols':undefined.splitlines()})
    combined=a.out/'race_control.reference.o'
    subprocess.run([a.prefix+'ld','-r',str(a.out/'race_control.o'),
                    str(a.out/'race_memory.o'),'-o',str(combined)],check=True)
    undefined=subprocess.check_output([a.prefix+'nm','-u',str(combined)],text=True)
    if undefined.strip():
        raise RuntimeError('unexpected unresolved target dependencies: '+undefined)
    (a.out/'race_control.reference.disassembly.txt').write_text(
        subprocess.check_output([a.prefix+'objdump','-dr',str(combined)],text=True))
    manifest={'status':'V850E3V5 RELOCATABLE REFERENCE OBJECTS - NO ECU RUNTIME INSTALLED',
              'compiler':version,'flags':flags,'objects':objects,
              'combined_object_sha256':hashlib.sha256(combined.read_bytes()).hexdigest(),
              'combined_undefined_symbols':[],
              'target_execution_tested':False,'ecu_adapter_installed':False,
              'note':'Self-contained target core; ECU ABI/hooks/RAM/IO remain to be validated before firmware linking.'}
    if a.profile_bin:
        image=a.profile_bin.read_bytes()
        profile=image[0x170440:0x170440+576]
        if len(image)!=0x200000 or profile[:8]!=b'RACEWG01':
            raise ValueError('expected prepared 2-MiB image and RACEWG01 profile')
        (a.out/'profile_fixture.h').write_text('static const unsigned char profile_fixture[576]={'+','.join(map(str,profile))+'};\n')
        test=a.out/'test.o'
        subprocess.run([compiler,*flags,'-I'+str(source/'freestanding'),'-I'+str(a.out),
                        '-c',str(source/'test_target.c'),'-o',str(test)],check=True)
        subprocess.run([a.prefix+'objcopy','--strip-symbol=r31',str(test)],check=True)
        elf=a.out/'selftest.elf'
        subprocess.run([a.prefix+'ld','-Ttext=0xc0000','-e','_race_target_selftest',
                        str(test),str(combined),'-o',str(elf)],check=True)
        subprocess.run([a.prefix+'objcopy','-O','binary',str(elf),str(a.out/'selftest.bin')],check=True)
        if subprocess.check_output([a.prefix+'nm','-u',str(elf)],text=True).strip():
            raise RuntimeError('self-test has unresolved symbols')
        manifest['selftest']={'load_address':'0xc0000','entry_address':'0xc0000',
            'profile_sha256':hashlib.sha256(profile).hexdigest(),
            'flat_image_sha256':hashlib.sha256((a.out/'selftest.bin').read_bytes()).hexdigest(),
            'note':'Emulator-only fixture; never flash to ECU'}
    (a.out/'reference-build.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':
    main()
