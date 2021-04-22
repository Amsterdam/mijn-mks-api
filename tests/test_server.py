import json
from unittest.mock import patch

from mks.server import application
from tma_saml.for_tests.cert_and_key import server_crt
from flask_testing.utils import TestCase
from .test_mks_client_bsn_hr import BSN_HR_RESPONSE, get_bsn_xml_response_fixture
from .test_mks_client_kvk_prs_hr import KVK_HR_PRS_RESPONSE, get_kvk_prs_xml_response_fixture, get_xml_response_empty_fixture
from .test_mks_client_kvk_mac_hr import KVK_HR_MAC_RESPONSE, get_kvk_mac_xml_response_fixture
from .test_mks_client_nnp_hr import NNP_HR_RESPONSE, get_nnp_xml_response_fixture
from tma_saml import FlaskServerTMATestCase
# from tma_saml.for_tests.fixtures import generate_saml_token_for_kvk, generate_saml_token_for_bsn


def wrap_response(response_data, status: str = 'OK'):
    return {
        'content': json.loads(json.dumps(response_data, default=str)),
        'status': status
    }


class HRTest(FlaskServerTMATestCase, TestCase):

    def create_app(self):

        application.config['TESTING'] = True
        application.testing = True
        return application

    def setUp(self) -> None:
        self.maxDiff = None


@patch("mks.service.saml.get_tma_certificate", lambda: server_crt)
class HrBsnTest(HRTest):

    def _get_expected(self):
        return wrap_response(BSN_HR_RESPONSE)

    @patch('mks.service.mks_client_hr._get_response_by_bsn', lambda bsn: get_bsn_xml_response_fixture())
    def test_bsn(self):
        headers = self.add_digi_d_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected())

    @patch('mks.operations._get_response_by_bsn', lambda bsn: get_bsn_xml_response_fixture())
    @patch('mks.operations.get_raw_key', lambda: 'a')
    def test_bsn_raw(self):
        headers = self.add_digi_d_headers('999999990')
        self.client.set_cookie("", "access_token", 'a')
        response = self.client.get('/brp/hr/raw', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, get_bsn_xml_response_fixture())


@patch("mks.service.saml.get_tma_certificate", lambda: server_crt)
class HrKvkPrsTest(HRTest):

    def _get_expected(self):
        return wrap_response(KVK_HR_PRS_RESPONSE)

    @patch('mks.service.mks_client_hr._get_response_by_kvk_number', lambda kvk_number: get_kvk_prs_xml_response_fixture())
    def test_get_prs_hr(self):
        headers = self.add_e_herkenning_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected())

    @patch('mks.service.mks_client_hr._get_response_by_kvk_number', lambda kvk_number: get_xml_response_empty_fixture())
    def test_empty(self):
        headers = self.add_e_herkenning_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        self.assertEqual(response.status_code, 204)

    @patch('mks.operations._get_response_by_kvk_number', lambda kvk_number: get_kvk_prs_xml_response_fixture())
    @patch('mks.operations.get_raw_key', lambda: 'a')
    def test_bsn_raw(self):
        headers = self.add_e_herkenning_headers('999999990')
        self.client.set_cookie("", "access_token", 'a')
        response = self.client.get('/brp/hr/raw', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, get_kvk_prs_xml_response_fixture())

    @patch('mks.operations.get_raw_key', lambda: 'a')
    def test_bsn_wrong_token(self):
        self.client.set_cookie("", "access_token", 'xx')
        response = self.client.get('/brp/hr/raw')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, 'no access without access token')


@patch("mks.service.saml.get_tma_certificate", lambda: server_crt)
class HrKvkMacTest(HRTest):

    def _get_expected(self):
        return wrap_response({**KVK_HR_MAC_RESPONSE, **NNP_HR_RESPONSE})

    @patch('mks.service.mks_client_hr._get_response_by_kvk_number', lambda kvk_number: get_kvk_mac_xml_response_fixture())
    @patch('mks.service.mks_client_hr._get_response_by_nnpid', lambda kvk_number: get_nnp_xml_response_fixture())
    def test_get_mac_hr(self):
        headers = self.add_e_herkenning_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected())
