import os
from datetime import date
from unittest import TestCase
from unittest.mock import patch

from mks.service import mks_client_bsn_hr

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_kvk_mac_response.xml")


def get_xml_response_fixture(*args):
    with open(RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


class KvkHrTest(TestCase):

    def _expected_result(self):
        return {
            'aandeelhouders': [],
            'bestuurders': [],
            'mokum': True,
            'onderneming': {
                'datumAanvang': None,
                'datumEinde': None,
                'kvkNummer': '1234567'
            },
            'rechtspersonen': [
                {
                    'datumAanvang': date(2009, 1, 1),
                    'datumEinde': None,
                    'datumVoortzetting': None,
                    'emailadres': None,
                    'faxnummer': None,
                    'rechtsvorm': 'VennootschapOnderFirma',
                    'statutaireNaam': 'Naam v.o.f.',
                    'statutaireZetel': None,
                    'telefoonnummer': None,
                    'type': 'nnp',
                    'url': None
                }
            ],
            'vestigingen': [
                {
                    'activiteiten': [
                        {
                            'code': '000000000056102',
                            'indicatieHoofdactiviteit': True,
                            'omschrijving': "Fastfoodrestaurants, cafetaria's, ijssalons, eetkramen e.d."
                        }
                    ],
                    'datumAanvang': date(2000, 2, 1),
                    'datumEinde': None,
                    'emailadres': 'email@example.com',
                    'faxnummer': None,
                    'handelsnamen': ['Handelsnaam'],
                    'rekeningnummerBankGiro': None,
                    'telefoonnummer': '+310200000000',
                    'typeringVestiging': 'Hoofdvestiging',
                    'vestigingsNummer': '000000000001'},
                {
                    'activiteiten': [
                        {
                            'code': '000000000056102',
                            'indicatieHoofdactiviteit': True,
                            'omschrijving': 'Fastfoodrestaurants, '
                                            "cafetaria's, ijssalons, "
                                            'eetkramen e.d.'
                        }
                    ],
                    'datumAanvang': date(2015, 1, 1),
                    'datumEinde': None,
                    'emailadres': 'mail@example.com',
                    'faxnummer': None,
                    'handelsnamen': ['Handelsnaam 2e locatie'],
                    'rekeningnummerBankGiro': None,
                    'telefoonnummer': '+310000000000',
                    'typeringVestiging': 'Nevenvestiging',
                    'vestigingsNummer': '000000000002'
                },
                {
                    'activiteiten': [
                        {
                            'code': '000000000056102',
                            'indicatieHoofdactiviteit': True,
                            'omschrijving': "Fastfoodrestaurants, cafetaria's, ijssalons, eetkramen e.d."
                        }
                    ],
                    'datumAanvang': date(2002, 1, 1),
                    'datumEinde': None,
                    'emailadres': 'mail@example.com',
                    'faxnummer': None,
                    'handelsnamen': ['Handelsnaam v.o.f.'],
                    'rekeningnummerBankGiro': None,
                    'telefoonnummer': '+310200000000',
                    'typeringVestiging': 'Nevenvestiging',
                    'vestigingsNummer': '000000000003'
                }
            ]
        }

    @patch('mks.service.mks_client_bsn_hr._get_response', get_xml_response_fixture)
    def test_get(self):
        result = mks_client_bsn_hr.get_from_kvk('123456789')

        self.assertEqual(result, self._expected_result())
