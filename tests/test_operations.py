import os
# ignoring E402: module level import not at top of file
os.environ['TMA_CERTIFICATE'] = 'cert content'  # noqa: E402
os.environ['BRP_APPLICATIE'] = 'mijnAmsTestApp'  # noqa: E402
os.environ['BRP_GEBRUIKER'] = 'mijnAmsTestUser'  # noqa: E402
os.environ['MKS_BRP_ENDPOINT'] = 'https://example.com'  # noqa: E402


from unittest.mock import patch

from flask_testing.utils import TestCase
from mks.operations import get_brp
from mks.server import application


FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response.xml")


def get_xml_response_fixture(*args):
    with open(RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


class BRPTests(TestCase):

    def create_app(self):
        app = application
        app.config['TESTING'] = True
        return app

    @patch('mks.operations.get_bsn_from_saml_token', lambda: '123456789')
    @patch('mks.service.mks_client_03_10._get_response', get_xml_response_fixture)
    def test_get_brp(self):
        data = get_brp()
        # data = json.loads(data_str)
        self.assertEqual(data['persoon']['bsn'], '123456789')
        self.assertEqual(data['verbintenis']['soortVerbintenisOmschrijving'], 'Huwelijk')
        self.assertEqual(len(data['kinderen']), 2)

    @patch('mks.operations.get_bsn_from_saml_token', lambda: '123456789')
    @patch('mks.service.mks_client_03_10._get_response', get_xml_response_fixture)
    def test_api_call(self):
        response = self.client.get('/brp/brp')

        json = response.json
        self.assertEqual(json['persoon']['bsn'], '123456789')
        self.assertEqual(json['adres']['huisletter'], None)
        self.assertEqual(json['adres']['postcode'], '1011 PN')


class StatusTest(TestCase):
    def create_app(self):
        app = application
        app.config['TESTING'] = True
        return app

    def test_status_call(self):
        response = self.client.get('/status/health')
        self.assert200(response)
