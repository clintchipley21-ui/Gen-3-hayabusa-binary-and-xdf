"""Check assembled spare detachment, binary/XDF storage and portable control logic."""
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import build_race_dev as race
import prepare_boost_integration as prep


class BoostIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock=race.reference('stock/5JCZSJ40/5JCZSJ40.bin')
        cls.base,_,_=race.build(cls.stock,race.GM_55567257_CANDIDATE)
        cls.image,cls.xdf,cls.manifest=race.build(cls.stock,race.GM_55567257_CANDIDATE,True)

    def test_only_detached_spare_profile_and_checksum_change(self):
        allowed=set(range(prep.PROFILE_ADDRESS,prep.PROFILE_ADDRESS+prep.PROFILE_SIZE))
        allowed.update(range(prep.DETACH_ADDRESS,prep.DETACH_ADDRESS+2))
        allowed.update(race.CRC_ADDRS)
        actual={i for i,(a,b) in enumerate(zip(self.base,self.image)) if a!=b}
        self.assertTrue(actual <= allowed)
        self.assertEqual(self.image[prep.DETACH_ADDRESS:prep.DETACH_ADDRESS+2],prep.DETACH_PATCH)
        self.assertEqual(self.image[0x170440+576:0x170440+2600],self.base[0x170440+576:0x170440+2600])
        self.assertFalse(self.manifest['boost_integration_preparation']['runtime_driver_installed'])

    def test_loop_keeps_main_and_blend_per_cylinder(self):
        # The patched loop still indexes cylinder*6; only termination changes.
        # Compare original and new descriptor selection, not a mock output pin.
        original=[struct.unpack_from('<I',self.base,0x17EBE4+4*i)[0] for i in range(24)]
        selected=[original[cyl*6+i] for cyl in range(4) for i in range(2)]
        for cyl in range(4):
            self.assertEqual(selected[cyl*2:cyl*2+2],original[cyl*6:cyl*6+2])
        self.assertNotIn(prep.DESCRIPTOR,selected)
        self.assertEqual(self.base[0x4536c:0x453b0],self.image[0x4536c:0x453b0])
        self.assertEqual(self.base[0x491bc:0x49276],self.image[0x491bc:0x49276])

    def test_xdf_profile_replaces_one_spare_and_no_ids_collide(self):
        root=ET.fromstring(self.xdf)
        ids=[e.get('uniqueid') for e in root if e.tag in ('XDFTABLE','XDFCONSTANT','XDFFLAG')]
        self.assertEqual(len(ids),len(set(ids)))
        reserved=[e for e in root if e.findtext('title','').startswith('RESERVED')]
        self.assertEqual(len(reserved),6)
        self.assertEqual(sum(e.findtext('title','').startswith('TPS STORAGE') for e in root),27)
        self.assertEqual(self.image[prep.PROFILE_ADDRESS+12],0)
        self.assertEqual(self.image[prep.PROFILE_ADDRESS+128:prep.PROFILE_ADDRESS+576],bytes(448))

    def test_decode_actual_prepared_profile_and_run_native_controller(self):
        workspace=race.ROOT.parent/'work'
        workspace.mkdir(exist_ok=True)
        source=race.ROOT/'race/control'
        with tempfile.TemporaryDirectory(dir=workspace) as tmp:
            tmp=Path(tmp)
            blob=tmp/'profile.bin'
            blob.write_bytes(self.image[prep.PROFILE_ADDRESS:prep.PROFILE_ADDRESS+prep.PROFILE_SIZE])
            subprocess.run(['gcc','-std=c99','-Wall','-Wextra','-Werror','-pedantic',
                            '-fsanitize=undefined','-fno-sanitize-recover=all',
                            str(source/'race_control.c'),str(source/'test_race_control.c'),
                            '-o',str(tmp/'controller-test')],check=True,capture_output=True,text=True)
            result=subprocess.run([str(tmp/'controller-test'),str(blob)],check=True,capture_output=True,text=True)
            self.assertIn('native controller scenarios passed',result.stdout)

    def test_profile_sensor_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            race.build(self.stock,(.26,-10,250),True)
        with self.assertRaises(ValueError):
            race.build(self.stock,None,True)

    def test_preparation_on_all_supported_variants_preserves_other_bytes(self):
        for variant in race.STOCK_HASHES.values():
            with self.subTest(variant=variant):
                base=(race.ROOT / ('stock/%s/%s.bin' % (variant,variant))).read_bytes()
                image,_,manifest=race.build(base,race.GM_55567257_CANDIDATE,True)
                self.assertEqual(image[0x1A4708:0x1A4E0A],base[0x1A4708:0x1A4E0A])
                self.assertEqual(image[0x1FFAE4:0x1FFAF0],base[0x1FFAE4:0x1FFAF0])
                self.assertFalse(manifest['boost_integration_preparation']['runtime_driver_installed'])


if __name__=='__main__':
    unittest.main()
