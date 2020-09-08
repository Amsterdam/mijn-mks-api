from unittest.mock import patch

from tma_saml import FlaskServerTMATestCase
from tma_saml.for_tests.cert_and_key import server_crt

from mks.server import application


@patch("mks.service.saml.get_tma_certificate", lambda: server_crt)
class UserIdentifierTest(FlaskServerTMATestCase):

    def setUp(self) -> None:
        self.client = self.get_tma_test_app(application)

    def test_bsn(self):
        headers = self.add_digi_d_headers('999999990')
        response = self.client.get('/brp/bsn', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'burgerservicenummer': '999999990'})

    def test_kvk(self):
        headers = self.add_e_herkenning_headers('12345678')
        response = self.client.get('/brp/kvk', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'kvknummer': '12345678'})
