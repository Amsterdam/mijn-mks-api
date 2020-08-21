import os
from unittest import TestCase
from unittest.mock import patch

from mks.service import mks_client_bsn_hr

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_kvk_response.xml")


def get_xml_response_fixture(*args):
    with open(RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


class KvkHrTest(TestCase):
    @patch('mks.service.mks_client_bsn_hr._get_response', get_xml_response_fixture)
    def test_get(self):
        result = mks_client_bsn_hr.get_from_kvk('123456789')

        from pprint import pprint
        pprint(result)
