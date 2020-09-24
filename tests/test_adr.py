import os
from unittest import TestCase
from unittest.mock import patch

from flask_testing.utils import TestCase as FlaskTestCase

from mks.model.stuf_utils import encrypt
from mks.server import application
from mks.service.adr_mks_client_02_04 import extract
from mks.service.config import get_jwt_key

jwk_string = "RsKzMu5cIx92FSzLZz1RmsdLg7wJQPTwsCrkOvNNlqg"


FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "adr_response.xml")


def get_xml_response_fixture(*args):
    with open(RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


@patch.dict(os.environ, {'MKS_JWT_KEY': jwk_string})
class AdrTest(TestCase):

    def get_result(self):
        return {
            'residentCount': 3,
            'crossRefNummer': 'MijnAmsterdam'
        }

    def test_config(self):

        key = get_jwt_key().export()

        self.assertIn(jwk_string, key)

    def test_extraction(self):
        xml_data = get_xml_response_fixture()

        result = extract(xml_data)

        self.maxDiff = None
        self.assertEqual(result, self.get_result())


class ResidentsTest(FlaskTestCase):

    def create_app(self):
        app = application
        app.config['TESTING'] = True
        return app

    @patch('mks.service.adr_mks_client_02_04._get_response', get_xml_response_fixture)
    def test_adr_call(self):
        post_body = {'addressKey': encrypt('1234')}

        response = self.client.post('/brp/aantal_bewoners', json=post_body)
        self.assertEqual(response.json, {'crossRefNummer': 'MijnAmsterdam', 'residentCount': 3})

    @patch('mks.service.adr_mks_client_02_04._get_response', get_xml_response_fixture)
    def test_adr_call_empty(self):
        response = self.client.post('/brp/aantal_bewoners', json=None)
        self.assert400(response)
        self.assertEqual(response.json, "adressleutel required")

    @patch('mks.service.adr_mks_client_02_04._get_response', get_xml_response_fixture)
    def test_adr_call_wrong_key(self):
        response = self.client.post('/brp/aantal_bewoners', json={'wrongKey': ''})
        self.assert400(response)
        self.assertEqual(response.json, "adressleutel required")

    @patch('mks.service.adr_mks_client_02_04._get_response', get_xml_response_fixture)
    def test_adr_call_not_encrypted(self):
        post_body = {'addressKey': '1234'}

        response = self.client.post('/brp/aantal_bewoners', json=post_body)
        self.assert400(response)
        self.assertEqual(response.json, "Invalid encrypted value")
