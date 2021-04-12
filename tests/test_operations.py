import os
from tma_saml import UserType
from unittest.mock import patch
from jwcrypto import jwk
from flask_testing.utils import TestCase

os.environ['TMA_CERTIFICATE'] = 'cert content'
os.environ['BRP_APPLICATIE'] = 'mijnAmsTestApp'
os.environ['BRP_GEBRUIKER'] = 'mijnAmsTestUser'
os.environ['MKS_BRP_ENDPOINT'] = 'https://example.com'


# ignoring E402: module level import not at top of file
from mks.operations import get_brp  # noqa: E402
from mks.server import application  # noqa: E402


FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response_0204.xml")


def get_xml_response_fixture(*args):
    with open(RESPONSE_PATH, 'rb') as response_file:
        return response_file.read().decode("utf-8")


def get_jwt_key_test():
    key = jwk.JWK.generate(kty='oct', size=256)
    return key


class BRPTests(TestCase):

    def create_app(self):
        app = application
        app.config['TESTING'] = True
        return app

    @patch('mks.operations.get_bsn_from_saml_token', lambda: '123456789')
    @patch('mks.operations.get_type', lambda x: UserType.BURGER)
    @patch('mks.model.stuf_utils.get_jwt_key', get_jwt_key_test)
    @patch('mks.service.mks_client_02_04._get_response', get_xml_response_fixture)
    def test_get_brp(self):
        data = get_brp()
        self.assertEqual(data['persoon']['bsn'], '000000001')
        self.assertEqual(data['verbintenis']['soortVerbintenisOmschrijving'], 'Huwelijk')
        self.assertEqual(data['crossRefNummer'], 'test2')
        self.assertEqual(len(data['kinderen']), 1)

    @patch('mks.operations.get_bsn_from_saml_token', lambda: '123456789')
    @patch('mks.operations.get_type', lambda x: UserType.BURGER)
    @patch('mks.model.stuf_utils.get_jwt_key', get_jwt_key_test)
    @patch('mks.service.mks_client_02_04._get_response', get_xml_response_fixture)
    def test_api_call(self):
        response = self.client.get('/brp/brp')

        json = response.json
        self.assertEqual(json['persoon']['bsn'], '000000001')
        self.assertEqual(json['adres']['huisletter'], None)
        self.assertEqual(json['adres']['postcode'], '1011 PN')
        self.assertEqual(json['crossRefNummer'], 'test2')

    @patch('mks.operations.get_bsn_from_saml_token', lambda: '123456789')
    @patch('mks.service.mks_client_02_04._get_response', get_xml_response_fixture)
    @patch('mks.operations.get_raw_key', lambda: 'a')
    def test_brp_raw(self):
        self.client.set_cookie("", "access_token", 'a')
        response = self.client.get('/brp/brp/raw')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, get_xml_response_fixture())

    @patch('mks.operations.get_bsn_from_saml_token', lambda: '123456789')
    @patch('mks.service.mks_client_02_04._get_response', get_xml_response_fixture)
    @patch('mks.operations.get_raw_key', lambda: 'a')
    def test_brp_raw_wrong_token(self):
        # no token set
        response = self.client.get('/brp/brp/raw')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, 'no access without access token')

        self.client.set_cookie("", "access_token", 'aa')
        response = self.client.get('/brp/brp/raw')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, 'no access without access token')


class StatusTest(TestCase):
    def create_app(self):
        app = application
        app.config['TESTING'] = True
        return app

    def test_status_call(self):
        response = self.client.get('/status/health')
        self.assert200(response)
