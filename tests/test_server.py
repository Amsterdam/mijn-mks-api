import os
from unittest.mock import patch

from tma_saml import FlaskServerTMATestCase
from tma_saml.for_tests.cert_and_key import server_crt

from mks.server import application

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
BSN_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_bsn_response.xml")
KVK_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_kvk_prs_response.xml")


def get_bsn_xml_response_fixture(*args):
    with open(BSN_RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


def get_kvk_xml_response_fixture(*args):
    with open(BSN_RESPONSE_PATH, 'rb') as response_file:
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
                    'kvkNummer': '12345678'},
                'rechtspersonen': [
                    {
                        'adres': {
                            'huisletter': None,
                            'huisnummer': None,
                            'huisnummertoevoeging': None,
                            'openbareRuimteNaam': None,
                            'postcode': None,
                            'woonplaatsNaam': None
                        },
                        'geboortedatum': '1970-01-01',
                        'geslachtsnaam': 'Achternaam',
                        'voornamen': 'Voornaam'
                    }
                ],
                'vestigingen': [
                    {
                        'activiteiten': [
                            {
                                'code': '000000000069209',
                                'indicatieHoofdactiviteit': True,
                                'omschrijving': 'Overige '
                                                'administratiekantoren'
                            },
                            {
                                'code': '000000000070221',
                                'indicatieHoofdactiviteit': False,
                                'omschrijving': 'Organisatie-adviesbureaus'
                            },
                            {
                                'code': '000000000007810',
                                'indicatieHoofdactiviteit': False,
                                'omschrijving': 'Arbeidsbemiddeling'
                            }
                        ],
                        'datumAanvang': '1992-01-01',
                        'datumEinde': '2020-01-01',
                        'emailadres': None,
                        'faxnummer': None,
                        'handelsnamen': ['Ding 1',
                                         'Ding 2',
                                         'Ding 3',
                                         'Ding 4'],
                        'rekeningnummerBankGiro': None,
                        'telefoonnummer': None,
                        'typeringVestiging': 'Hoofdvestiging',
                        'vestigingsNummer': '000000000001'
                    }
                ]
            },
            'status': 'OK'
        }

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
                    'kvkNummer': '12345678'
                },
                'rechtspersonen': [],
                'vestigingen': [
                    {
                        'activiteiten': [
                            {
                                'code': '000000000069209',
                                'indicatieHoofdactiviteit': True,
                                'omschrijving': 'Overige '
                                                'administratiekantoren'
                            },
                            {
                                'code': '000000000070221',
                                'indicatieHoofdactiviteit': False,
                                'omschrijving': 'Organisatie-adviesbureaus'
                            },
                            {
                                'code': '000000000007810',
                                'indicatieHoofdactiviteit': False,
                                'omschrijving': 'Arbeidsbemiddeling'
                            }
                        ],
                        'datumAanvang': '1992-01-01',
                        'datumEinde': '2020-01-01',
                        'emailadres': None,
                        'faxnummer': None,
                        'handelsnamen': [
                            'Ding 1',
                            'Ding 2',
                            'Ding 3',
                            'Ding 4'
                        ],
                        'rekeningnummerBankGiro': None,
                        'telefoonnummer': None,
                        'typeringVestiging': 'Hoofdvestiging',
                        'vestigingsNummer': '000000000001'
                    }
                ]
            },
            'status': 'OK'}

    @patch('mks.service.mks_client_bsn_hr._get_response', get_kvk_xml_response_fixture)
    def test_kvk(self):
        headers = self.add_e_herkenning_headers('999999990')
        response = self.client.get('/brp/hr', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self._get_expected())
