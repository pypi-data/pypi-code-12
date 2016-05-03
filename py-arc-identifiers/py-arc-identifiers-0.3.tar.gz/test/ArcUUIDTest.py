import base64
import unittest
import uuid

from ArcUUID.ArcUUID import ArcUUID
from ArcUUID.Ids import Ids


class ArcUUIDTest(unittest.TestCase):

    def test_unique_id_max(self):
        uuid_max = uuid.UUID('{7fffffff-ffff-ffff-7fff-ffffffffffff}')
        max_encoded = base64.b32encode(uuid_max.bytes)
        max_encoded = str(max_encoded).replace('=', '').replace('b\'', '').replace('\'', '')
        self.assertEqual("P7777777777767777777777774", max_encoded)
        self.assertEqual(ArcUUID.LENGTH, len(max_encoded))

    def test_unique_id_min(self):
        uuid_min = uuid.UUID('{80000000-0000-0000-8000-000000000000}')
        min_encoded = base64.b32encode(uuid_min.bytes)
        min_encoded = str(min_encoded).replace('=', '').replace('b\'', '').replace('\'', '')
        self.assertEqual("QAAAAAAAAAAABAAAAAAAAAAAAA", min_encoded)
        self.assertEqual(ArcUUID.LENGTH, len(min_encoded))
        self.assertIsNotNone(ArcUUID.from_string("QAAAAAAAAAAABAAAAAAAAAAAAA"))

    def test_unique_id(self):
        unique_id = str(ArcUUID.random_arc_uuid());
        self.assertEqual(len(unique_id), ArcUUID.LENGTH, "uuid length should be 26");

    def test_hardcoded_washington_post_uuid(self):
        wapoID = "PW5TIZPZINHXBPNQTAJRSISO3E"
        self.assertEqual(26, len(wapoID))
        wapoUUID = ArcUUID.from_string(wapoID)
        self.assertEqual(wapoUUID, Ids.WAPO)

    def test_arc_uuid_from_null_string_throws_exception(self):
        with self.assertRaises(ValueError):
            ArcUUID.from_string(None)

    def test_arc_uuid_with_too_long_string_throws_exception(self):
        with self.assertRaises(ValueError):
            ArcUUID.from_string("QAAAAAAAAAAABAAAAAAAAAAAAAQAAAAAAAAAAABAAAAAAAAAAAAA");

    def test_arc_uuid_with_not_base32_characters_throws_exception(self):
        with self.assertRaises(ValueError):
            ArcUUID.from_string("!@#$%^&*()================");

    def test_equals_contract(self):
        check1 = Ids.DEMO1
        check2 = ArcUUID.from_string("2HDHHWH45JAHDFRWJKX2TJDVFA")
        self.assertEqual(check1, check2)
        check3 = Ids.DEMO2
        check4 = ArcUUID.from_string("QFJBYOYVDZC35N2X33UBMMCUNI")
        self.assertNotEqual(check3, check4)

    def test_from_hex(self):
        arc_uuid_from_hex = ArcUUID.from_hex('7fffffff-ffff-ffff-7fff-ffffffffffff')
        self.assertEqual("P7777777777767777777777774", str(arc_uuid_from_hex))
        self.assertEqual(ArcUUID.LENGTH, len(str(arc_uuid_from_hex)))

        arc_uuid_from_hex_without_hyphen = ArcUUID.from_hex('7fffffffffffffff7fffffffffffffff')
        self.assertEqual("P7777777777767777777777774", str(arc_uuid_from_hex_without_hyphen))

        with self.assertRaises(ValueError):
            ArcUUID.from_hex('7fffffffffffffff7fffffffffffff')

    def test_is_valid_arc_uuid(self):
        valid_1 = str(ArcUUID.random_arc_uuid())
        valid_2 = str(ArcUUID.random_arc_uuid())
        valid_3 = "ANRKRFW4GMI6LAQQ6C6Y32IV6Y"
        invalid_1 = "123abc"
        invalid_2 = ""
        invalid_3 = "USJS6U4HPVFODL4NGWEL26KODQFQDAX"
        invalid_4 = "7fffffff-ffff-ffff-7fff-ffffffffffff"
        self.assertTrue(ArcUUID.is_valid_arc_uuid(valid_1))
        self.assertTrue(ArcUUID.is_valid_arc_uuid(valid_2))
        self.assertTrue(ArcUUID.is_valid_arc_uuid(valid_3))
        self.assertFalse(ArcUUID.is_valid_arc_uuid(invalid_1))
        self.assertFalse(ArcUUID.is_valid_arc_uuid(invalid_2))
        self.assertFalse(ArcUUID.is_valid_arc_uuid(invalid_3))
        self.assertFalse(ArcUUID.is_valid_arc_uuid(invalid_4))
