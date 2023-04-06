import unittest

from contacts_parser import main

class TestVcfLineParser(unittest.TestCase):
    def test_value(self):
        line = "BEGIN:VCARD"
        regex_key = "init_contact"
        self.assertTrue(main.VcfLineParser(line).is_type(regex_key))
        line = "VERSION:2.1"
        regex_key = "version"
        self.assertTrue(main.VcfLineParser(line).is_type(regex_key))
        line="N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:;=41=74=65=6E=63=69=C3=B3=6E=20=61=6C=20=43=6C=69=65=6E=74=65;;;"
        expected_result = "Atención al Cliente"
        regex_key = "name_encoded"
        self.assertEqual(expected_result, main.VcfLineParser(line).get_value(regex_key))
        line="TEL;CELL:1004"
        expected_result = "1004"
        regex_key = "phone"
        self.assertEqual(expected_result, main.VcfLineParser(line).get_value(regex_key))
        line="TEL;HOME:123"
        expected_result = "123"
        regex_key = "phone"
        self.assertEqual(expected_result, main.VcfLineParser(line).get_value(regex_key))
        line="NOTE;ENCODING=QUOTED-PRINTABLE:=41=74=65=6E=63=69=C3=B3=6E=20=61=6C=20=43=6C=69=65=6E=74=65"
        expected_result = "Atención al Cliente"
        regex_key = "note_encoded"
        self.assertEqual(expected_result, main.VcfLineParser(line).get_value(regex_key))
        line="NOTE;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:=41=74=65=6E=63=69=C3=B3=6E=20=61=6C=20=43=6C=69=65=6E=74=65"
        expected_result = "Atención al Cliente"
        regex_key = "note_encoded"
        self.assertEqual(expected_result, main.VcfLineParser(line).get_value(regex_key))
        line="EMAIL;HOME:abc@foo.com"
        expected_result = "abc@foo.com"
        regex_key = "email"
        self.assertEqual(expected_result, main.VcfLineParser(line).get_value(regex_key))
