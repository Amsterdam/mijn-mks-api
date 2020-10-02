import os
from unittest.mock import patch

from tma_saml import FlaskServerTMATestCase
from tma_saml.for_tests.cert_and_key import server_crt

from mks.server import application

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
BSN_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_bsn_response.xml")
KVK_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_kvk_prs_response.xml")
RESPONSE_EMPTY_PATH = os.path.join(FIXTURE_PATH, "hr_empty_response.xml")


def get_bsn_xml_response_fixture(*args):
    with open(BSN_RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


def get_kvk_xml_response_fixture(*args):
    with open(KVK_RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


def get_xml_response_empty_fixture(*args):
    with open(RESPONSE_EMPTY_PATH, 'rb') as response_file:
        return response_file.read()


@patch("mks.service.saml.get_tma_certificate", lambda: server_crt)
class HrBsnTest(FlaskServerTMATestCase):

    def setUp(self) -> None:
        self.client = self.get_tma_test_app(application)

    def _get_expected(self):
        return {
            'content': {
                'aandeelhouders': [],
                'bestuurders': [],
                'mokum': True,
                'onderneming': {
                    'datumAanvang': '1992-01-01',
                    'datumEinde': '2020-01-01',
                    'handelsnamen': ['Ding 1', 'Ding 2', 'Ding 3', 'Ding 4'],
                    'hoofdactiviteit': 'Overige administratiekantoren',
                    'overigeActiviteiten': ['Arbeidsbemiddeling', 'Organisatie-adviesbureaus'],
                    'rechtsvorm': 'Eenmanszaak'
                },
                'rechtspersonen': [
                    {
                        'bsn': '999999999',
                        'kvkNummer': '12345678',
                        'rsin': None,
                        'statutaireNaam': None,
                        'statutaireZetel': None
                    }
                ],
                'vestigingen': [
                    {
                        'activiteiten': ['Overige administratiekantoren', 'Organisatie-adviesbureaus',
                                         'Arbeidsbemiddeling'],
                        'bezoekadres': {
                            'huisletter': None,
                            'huisnummer': '1',
                            'huisnummertoevoeging': None,
                            'postcode': '1011 PN',
                            'straatnaam': 'Amstel',
                            'woonplaatsNaam': 'Amsterdam'
                        },
                        'datumAanvang': '1992-01-01',
                        'datumEinde': '2020-01-01',
                        'emailadres': None,
                        'faxnummer': None,
                        'handelsnamen': ['Ding 1', 'Ding 2', 'Ding 3', 'Ding 4'],
                        'postadres': {
                            'huisletter': None,
                            'huisnummer': '1',
                            'huisnummertoevoeging': None,
                            'postcode': None,
                            'straatnaam': 'Amstel',
                            'woonplaatsNaam': 'Amsterdam'
                        },
                        'telefoonnummer': None,
                        'typeringVestiging': 'Hoofdvestiging',
                        'vestigingsNummer': '000000000001',
                        'websites': []
                    }
                ]
            },
            'status': 'OK'}

    @patch('mks.service.mks_client_bsn_hr._get_response', get_bsn_xml_response_fixture)
    def test_bsn(self):
        headers = self.add_digi_d_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected())


@patch("mks.service.saml.get_tma_certificate", lambda: server_crt)
class HrKvkTest(FlaskServerTMATestCase):

    def setUp(self) -> None:
        self.client = self.get_tma_test_app(application)

    def _get_expected(self):
        return {
            'content': {
                'aandeelhouders': [],
                'bestuurders': [],
                'mokum': True,
                'onderneming': {
                    'datumAanvang': '1992-01-01',
                    'datumEinde': '2020-01-01',
                    'handelsnamen': ['Naam 1',
                                     'Naam 2',
                                     'Naam 3',
                                     'Naam 4'],
                    'hoofdactiviteit': 'Overige administratiekantoren',
                    'overigeActiviteiten': ['Arbeidsbemiddeling', 'Organisatie-adviesbureaus'],
                    'rechtsvorm': 'Eenmanszaak'
                },
                'rechtspersonen': [
                    {
                        'bsn': '999999999',
                        'kvkNummer': '012345678',
                        'rsin': None,
                        'statutaireNaam': None,
                        'statutaireZetel': None
                    }
                ],
                'vestigingen': [
                    {
                        'activiteiten': ['Overige administratiekantoren', 'Organisatie-adviesbureaus',
                                         'Arbeidsbemiddeling'],
                        'bezoekadres': {
                            'huisletter': None,
                            'huisnummer': '1',
                            'huisnummertoevoeging': None,
                            'postcode': '1012 PN',
                            'straatnaam': 'Amstel',
                            'woonplaatsNaam': 'Amsterdam'
                        },
                        'datumAanvang': '1992-01-01',
                        'datumEinde': '2020-01-01',
                        'emailadres': None,
                        'faxnummer': None,
                        'handelsnamen': ['Naam 1', 'Naam 2', 'Naam 3', 'Naam 4'],
                        'postadres': {
                            'huisletter': None,
                            'huisnummer': '1',
                            'huisnummertoevoeging': None,
                            'postcode': None,
                            'straatnaam': 'Amstel',
                            'woonplaatsNaam': 'Amsterdam'
                        },
                        'telefoonnummer': None,
                        'typeringVestiging': 'Hoofdvestiging',
                        'vestigingsNummer': '000000000001',
                        'websites': []
                    }
                ]
            },
            'status': 'OK'
        }

    @patch('mks.service.mks_client_bsn_hr._get_response', get_kvk_xml_response_fixture)
    def test_kvk(self):
        headers = self.add_e_herkenning_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected())

    @patch('mks.service.mks_client_bsn_hr._get_response', get_xml_response_empty_fixture)
    def test_empty(self):
        headers = self.add_e_herkenning_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        self.assertEqual(response.status_code, 204)
