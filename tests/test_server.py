import json
import os
from unittest.mock import patch

from mks.server import application
from tma_saml import FlaskServerTMATestCase
from tma_saml.for_tests.cert_and_key import server_crt

from .test_mks_client_bsn_hr import BSN_HR_RESPONSE
from .test_mks_client_kvk_prs_hr import KVK_HR_PRS_RESPONSE

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
BSN_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_bsn_response.xml")
KVK_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_kvk_prs_response.xml")
NNP_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_nnp_response.xml")
RESPONSE_EMPTY_PATH = os.path.join(FIXTURE_PATH, "hr_empty_response.xml")


def get_bsn_xml_response_fixture(*args):
    with open(BSN_RESPONSE_PATH, 'rb') as response_file:
        return response_file.read().decode('utf-8')


def get_kvk_xml_response_fixture(*args):
    with open(KVK_RESPONSE_PATH, 'rb') as response_file:
        return response_file.read().decode('utf-8')


def get_nnp_xml_response_fixture(*args):
    with open(NNP_RESPONSE_PATH, 'rb') as response_file:
        return response_file.read().decode('utf-8')


def get_xml_response_empty_fixture(*args):
    with open(RESPONSE_EMPTY_PATH, 'rb') as response_file:
        return response_file.read().decode('utf-8')


def wrap_response(response_data, status: str = 'OK'):
    return {
        'content': json.loads(json.dumps(response_data, default=str)),
        'status': status
    }


@patch("mks.service.saml.get_tma_certificate", lambda: server_crt)
class HrBsnTest(FlaskServerTMATestCase):

    def setUp(self) -> None:
        self.client = self.get_tma_test_app(application)
        self.maxDiff = None

    def _get_expected(self):
        return wrap_response(BSN_HR_RESPONSE)

    @patch('mks.service.mks_client_bsn_hr._get_response', get_bsn_xml_response_fixture)
    def test_bsn(self):
        headers = self.add_digi_d_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected())

    @patch('mks.service.mks_client_bsn_hr._get_response', get_bsn_xml_response_fixture)
    @patch('mks.operations.get_raw_key', lambda: 'a')
    def test_bsn_raw(self):
        headers = self.add_digi_d_headers('999999990')
        self.client.set_cookie("", "access_token", 'a')
        response = self.client.get('/brp/hr/raw', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, get_bsn_xml_response_fixture())


@patch("mks.service.saml.get_tma_certificate", lambda: server_crt)
class HrKvkTest(FlaskServerTMATestCase):

    def setUp(self) -> None:
        self.client = self.get_tma_test_app(application)

    def _get_expected(self):
        return wrap_response(KVK_HR_PRS_RESPONSE)

    @patch('mks.service.mks_client_bsn_hr._get_response', get_kvk_xml_response_fixture)
    def test_get_hr(self):
        headers = self.add_e_herkenning_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected())

    @patch('mks.service.mks_client_bsn_hr._get_response', get_xml_response_empty_fixture)
    def test_empty(self):
        headers = self.add_e_herkenning_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        self.assertEqual(response.status_code, 204)

    @patch('mks.service.mks_client_bsn_hr._get_response', get_kvk_xml_response_fixture)
    @patch('mks.operations.get_raw_key', lambda: 'a')
    def test_bsn_raw(self):
        headers = self.add_e_herkenning_headers('999999990')
        self.client.set_cookie("", "access_token", 'a')
        response = self.client.get('/brp/hr/raw', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, get_kvk_xml_response_fixture())

    @patch('mks.operations.get_raw_key', lambda: 'a')
    def test_bsn_wrong_token(self):
        self.client.set_cookie("", "access_token", 'xx')
        response = self.client.get('/brp/hr/raw')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, 'no access without access token')
