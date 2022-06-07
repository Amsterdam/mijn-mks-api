import os
from unittest import TestCase
from unittest.mock import patch

from app.service import mks_client_hr

from app.test_mks_client_kvk_prs_hr import KVK_HR_EENMANSZAAK_RESPONSE

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
BSN_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_bsn_response.xml")
BSN_NO_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_bsn_no_hr_response.xml")


def get_bsn_xml_response_fixture(*args):
    with open(BSN_RESPONSE_PATH, "rb") as response_file:
        return response_file.read().decode("utf-8")


def get_bsn_no_hr_xml_response_fixture(*args):
    with open(BSN_NO_RESPONSE_PATH, "rb") as response_file:
        return response_file.read().decode("utf-8")


class BsnHrTest(TestCase):
    @patch("app.service.mks_client_hr._get_response", get_bsn_xml_response_fixture)
    def test_get(self):
        result = mks_client_hr.get_from_bsn("123456789")
        self.maxDiff = None
        self.assertEqual(result, KVK_HR_EENMANSZAAK_RESPONSE)

    @patch(
        "app.service.mks_client_hr._get_response", get_bsn_no_hr_xml_response_fixture
    )
    def test_no_hr_get(self):
        result = mks_client_hr.get_from_bsn("123456789")
        self.assertEqual(result, None)
