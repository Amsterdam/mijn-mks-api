import os
from datetime import date
from unittest import TestCase
from unittest.mock import patch

from mks.service import mks_client_bsn_hr

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
BSN_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_bsn_response.xml")


def get_bsn_xml_response_fixture(*args):
    with open(BSN_RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


class BsnHrTest(TestCase):

    def _get_expected(self):
        return {
            'aandeelhouders': [],
            'bestuurders': [],
            'mokum': True,
            'onderneming': {
                'datumAanvang': date(1992, 1, 1),
                'datumEinde': date(2020, 1, 1),
                'kvkNummer': '12345678'
            },
            'rechtspersonen': [
                {
                    'adres': {
                        'huisletter': None,
                        'huisnummer': None,
                        'huisnummertoevoeging': None,
                        'straatnaam': None,
                        'postcode': None,
                        'woonplaatsNaam': None
                    },
                    'bsn': None,
                    'geboortedatum': date(1970, 1, 1),
                    'geslachtsnaam': 'Achternaam',
                    'voornamen': 'Voornaam',
                    'rechtsvorm': 'Eenmanszaak',
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
                    'bezoekadres': {
                        'huisletter': None,
                        'huisnummer': '1',
                        'huisnummertoevoeging': None,
                        'postcode': '1011PN',
                        'straatnaam': 'Amstel',
                        'woonplaatsNaam': 'Amsterdam'
                    },
                    'datumAanvang': date(1992, 1, 1),
                    'datumEinde': date(2020, 1, 1),
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
                    'url': None,
                    'vestigingsNummer': '000000000001'
                }
            ]
        }

    @patch('mks.service.mks_client_bsn_hr._get_response', get_bsn_xml_response_fixture)
    def test_get(self):
        result = mks_client_bsn_hr.get_from_bsn('123456789')

        self.assertEqual(result, self._get_expected())
