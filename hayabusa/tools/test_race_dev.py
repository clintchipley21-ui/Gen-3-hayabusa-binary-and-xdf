"""Offline integration checks: firmware composition, variant containment and sensor resampling."""
import binascii
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_race_dev as race
import apply_patches as ap


class RaceBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock = race.reference('stock/5JCZSJ40/5JCZSJ40.bin')
        cls.sd = race.reference('race/Busa-SD-v4.1.bin')
        cls.image, cls.xdf, cls.manifest = race.build(cls.stock)

    def test_j40_matches_existing_sd41_plus_assembled_airshift(self):
        expected = bytearray(self.sd)
        for a, base, patch in ap.entries(self.stock, self.sd)['autoshift']:
            self.assertEqual(expected[a:a + len(base)], base)
            expected[a:a + len(patch)] = patch
        ap.crc_stamp(expected)
        self.assertEqual(self.image, expected)
        self.assertEqual(self.image[0xBF000], 0)
        self.assertEqual(self.image[0xBF010:0xBF012], b'\0\0')
        crc = binascii.crc_hqx(self.image[0x10000:0x1FFAFC], 0xFFFF)
        self.assertEqual(crc, int.from_bytes(self.image[0x1FFAFE:0x1FFB00], 'big'))
        self.assertEqual(self.image[0x1FFB00:], self.stock[0x1FFB00:])

    def test_supported_variants_preserve_every_unrelated_byte(self):
        allowed = {i for i, (a, b) in enumerate(zip(self.stock, self.image)) if a != b}
        for variant in race.STOCK_HASHES.values():
            with self.subTest(variant=variant):
                base = (race.ROOT / ('stock/%s/%s.bin' % (variant, variant))).read_bytes()
                image, _, manifest = race.build(base)
                self.assertEqual(manifest['base_variant'], variant)
                differences = {i for i, (a, b) in enumerate(zip(base, image)) if a != b}
                self.assertEqual(differences, allowed)
                self.assertEqual(image[0x1FFAE4:0x1FFAF0], base[0x1FFAE4:0x1FFAF0])
                self.assertEqual(image[0x1A4708:0x1A4E0A], base[0x1A4708:0x1A4E0A])

    def test_no_tps_storage_repurposed_and_no_fake_boost_driver(self):
        root = ET.fromstring(self.xdf)
        count = 0
        for table in root.findall('XDFTABLE'):
            if table.findtext('title', '').startswith('TPS STORAGE'):
                count += 1
                z = table.find("XDFAXIS[@id='z']/EMBEDDEDDATA")
                a = int(z.get('mmedaddress'), 16)
                n = int(z.get('mmedrowcount')) * int(z.get('mmedcolcount')) * int(z.get('mmedelementsizebits')) // 8
                self.assertEqual(self.stock[a:a + n], self.image[a:a + n])
        self.assertEqual(count, 28)
        self.assertFalse(self.manifest['features']['boost_output_control'])
        self.assertFalse(self.manifest['features']['map_based_base_ignition'])
        self.assertFalse(root.findall('XDFPATCH'))
        ids = [t.get('uniqueid') for t in root if t.tag in ('XDFTABLE', 'XDFCONSTANT', 'XDFFLAG')]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(len(d.text or '') <= 420 for d in root.findall('./*/description')))
        self.assertLessEqual(len(root.findtext('XDFHEADER/description')), 480)

    def test_custom_transfer_250_kpa_resamples_in_physical_units(self):
        # Synthetic transfer for testing only, not a GM part-number calibration.
        image, xdf, manifest = race.build(self.stock, (0.26, -10, 250))
        root = ET.fromstring(xdf)
        old_root = ET.fromstring(self.xdf)
        original = {int(t.find("XDFAXIS[@id='z']/EMBEDDEDDATA").get('mmedaddress'), 16): t
                    for t in old_root.findall('XDFTABLE')}
        for table in root.findall('XDFTABLE'):
            z = table.find("XDFAXIS[@id='z']/EMBEDDEDDATA")
            a = int(z.get('mmedaddress'), 16)
            if a not in race.SD_TABLES:
                continue
            x = table.find("XDFAXIS[@id='x']/EMBEDDEDDATA")
            xa, n = int(x.get('mmedaddress'), 16), int(x.get('mmedcolcount'))
            values = [race.read_u16(image, xa + i * 2) for i in range(n)]
            self.assertTrue(all(l < r for l, r in zip(values, values[1:])))
            self.assertAlmostEqual(values[-1] * .26 - 10, 250, delta=.13)
            self.assertIn('0.26', table.find("XDFAXIS[@id='x']/MATH").get('equation'))
            # Last column at 250 kPa must match interpolation of the OLD 250-kPa
            # curve, rather than incorrectly relabeling the OLD 300-kPa cell.
            old_x = original[a].find("XDFAXIS[@id='x']/EMBEDDEDDATA")
            old_a = int(old_x.get('mmedaddress'), 16)
            pressures = [race.read_u16(self.image, old_a + i * 2) * race.PROVISIONAL_A + race.PROVISIONAL_B for i in range(n)]
            w = int(z.get('mmedelementsizebits')) // 8
            old_values = [int.from_bytes(self.image[a + i * w:a + (i + 1) * w], 'little') for i in range(n)]
            expected = round(race.interpolate(pressures, old_values, 250))
            actual = int.from_bytes(image[a + (n - 1) * w:a + n * w], 'little')
            self.assertEqual(actual, expected)
        self.assertEqual(manifest['sensor']['ceiling_kpa_absolute'], 250)
        # Preserve stock baro scale and TPS fallback data.
        self.assertEqual(image[0x18EF5E:0x18EF62], self.stock[0x18EF5E:0x18EF62])
        self.assertEqual(image[0x16EF28:0x181000], self.image[0x16EF28:0x181000])

    def test_reject_unknown_edited_or_unported_base(self):
        bad = bytearray(self.stock)
        bad[0x123456] ^= 1
        for data in (bytes(bad), self.image, self.stock[:-1],
                     (race.ROOT / 'stock/5JCZSJB0/5JCZSJB0.bin').read_bytes()):
            with self.assertRaises(ValueError):
                race.build(data)

    def test_reject_unrepresentable_or_faulting_transfers(self):
        for sensor in ((0, 0, 250), (float('nan'), 0, 250), (.1, -10, 250),
                       (.26, -1000, 250), (.26, -10, 350)):
            with self.subTest(sensor=sensor), self.assertRaises(ValueError):
                race.build(self.stock, sensor)

    def test_gm_candidate_endpoints_and_build(self):
        a, b, ceiling = race.GM_55567257_CANDIDATE
        # 0.5/4.5 V at a 5-V reference correspond to 20/270 kPa.
        self.assertAlmostEqual(a * (1023 * .5 / 5) + b, 20)
        self.assertAlmostEqual(a * (1023 * 4.5 / 5) + b, 270)
        image, xdf, manifest = race.build(self.stock, (a, b, ceiling))
        self.assertEqual(manifest['sensor']['ceiling_kpa_absolute'], 270)
        self.assertNotEqual(image[0x18EF58:0x18EF5C], self.image[0x18EF58:0x18EF5C])


if __name__ == '__main__':
    unittest.main()
