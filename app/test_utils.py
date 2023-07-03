import os
from datetime import datetime, date
from unittest import TestCase
from unittest.mock import patch

from bs4 import BeautifulSoup
from app.helpers import decrypt, encrypt

from app.model.stuf_utils import (
    to_bool,
    to_datetime,
    to_int,
    to_string,
    as_postcode,
    to_date,
    is_nil,
    geboortedatum_to_string,
)

jwk_string = "RsKzMu5cIx92FSzLZz1RmsdLg7wJQPTwsCrkOvNNlqg"

def wrap(xmlstring):
    xmlstring = f"""
        <?xml version='1.0' encoding='UTF-8'?>
        <wrap xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        {xmlstring}
        </wrap>
    """
    tree = BeautifulSoup(xmlstring, features="lxml-xml")
    return tree

@patch.dict(os.environ, {"MKS_JWT_KEY": jwk_string})
class UtilsTest(TestCase):
    def _get_value(self, xml, tag_name):
        tree = BeautifulSoup(xml, features="lxml-xml")
        value = tree.find(tag_name).text
        return value

    def test_to_bool(self):
        self.assertFalse(to_bool(self._get_value("<a>0</a>", "a")))
        self.assertFalse(to_bool(self._get_value("<a>n</a>", "a")))
        self.assertFalse(to_bool(self._get_value("<a></a>", "a")))
        self.assertFalse(to_bool(self._get_value("<a />", "a")))

        self.assertTrue(to_bool(self._get_value("<a>1</a>", "a")))
        self.assertTrue(to_bool(self._get_value("<a>j</a>", "a")))

    def test_encrypt_decrypt(self):
        original_value = "1234567890"

        encrypted = encrypt(original_value)
        self.assertNotEqual(encrypted, original_value)

        decrypted = decrypt(encrypted)
        self.assertEqual(decrypted, original_value)

    def test_to_datetime(self):
        value = self._get_value("<a>201231</a>", "a")
        self.assertEqual(to_datetime(value), datetime(2012, 3, 1, 0, 0))

        value = self._get_value("<a></a>", "a")
        self.assertEqual(to_datetime(value), None)

    def test_to_date(self):
        value = self._get_value("<a>20120301</a>", "a")
        self.assertEqual(to_date(value), date(2012, 3, 1))

        value = self._get_value("<a></a>", "a")
        self.assertEqual(to_date(value), None)

    def test_to_int(self):
        value = self._get_value("<a>1</a>", "a")
        self.assertEqual(to_int(value), 1)

        value = self._get_value("<a>2</a>", "a")
        self.assertEqual(to_int(value), 2)

        value = self._get_value("<a>1234567890123456</a>", "a")
        self.assertEqual(to_int(value), 1234567890123456)

        value = self._get_value("<a>aa</a>", "a")
        with self.assertRaises(ValueError):
            to_int(value)

        value = self._get_value("<a></a>", "a")
        self.assertEqual(to_int(value), None)

        value = self._get_value("<a/>", "a")
        self.assertEqual(to_int(value), None)

    def test_to_string(self):
        value = self._get_value("<a>1</a>", "a")
        self.assertEqual(to_string(value), "1")
        value = self._get_value("<a>abc</a>", "a")
        self.assertEqual(to_string(value), "abc")

    def test_to_postcode(self):
        value = self._get_value("<a>1234AA</a>", "a")
        self.assertEqual(as_postcode(value), "1234 AA")

        value = self._get_value("<a>1234aa</a>", "a")
        self.assertEqual(as_postcode(value), "1234 AA")

        value = self._get_value("<a>1234</a>", "a")
        self.assertEqual(as_postcode(value), None)

        value = self._get_value("<a>aa</a>", "a")
        self.assertEqual(as_postcode(value), None)

    def test_is_nil(self):
        s = wrap('<a xsi:nil="true">1234AA</a>')
        self.assertTrue(is_nil(s.find("a")))

        s = wrap("<a><b>1</b><b>2</b></a>")
        self.assertFalse(is_nil(s.find_all("b")))

        self.assertTrue(is_nil([]))

    def test_geboortedatum_to_string(self):
        dates = [["J","00 00 0000"], ["M", "00 00 1957"], ["D", "00 July 1957"], ["V", "1 July 1957"]]

        for testDate in dates:
            xml = wrap(f"<BG:geboortedatum StUF:indOnvolledigeDatum=\"{testDate[0]}\">19570701</BG:geboortedatum>")
            tag = xml.find("geboortedatum")
            value = tag.string

            self.assertEqual(geboortedatum_to_string(value, tag), testDate[1])
