import os
from datetime import date
from unittest import TestCase
from unittest.mock import patch

from mks.service import mks_client_bsn_hr

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_kvk_prs_response.xml")
RESPONSE_EMPTY_PATH = os.path.join(FIXTURE_PATH, "hr_empty_response.xml")


def get_xml_response_fixture(*args):
    with open(RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


def get_xml_response_empty_fixture(*args):
    with open(RESPONSE_EMPTY_PATH, 'rb') as response_file:
        return response_file.read()


class KvkHrTest(TestCase):
    def _expected_result(self) -> dict:
        return {
            'aandeelhouders': [],
            'bestuurders': [],
            'mokum': True,
            'onderneming': {
                'datumAanvang': date(1992, 1, 1),
                'datumEinde': date(2020, 1, 1),
                'handelsnamen': ['Naam 1', 'Naam 2', 'Naam 3', 'Naam 4'],
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
                    'activiteiten': ['Overige administratiekantoren', 'Organisatie-adviesbureaus', 'Arbeidsbemiddeling'],
                    'bezoekadres': {
                        'huisletter': None,
                        'huisnummer': '1',
                        'huisnummertoevoeging': None,
                        'postcode': '1012 PN',
                        'straatnaam': 'Amstel',
                        'woonplaatsNaam': 'Amsterdam'
                    },
                    'datumAanvang': date(1992, 1, 1),
                    'datumEinde': date(2020, 1, 1),
                    'emailadres': None,
                    'faxnummer': None,
                    'handelsnamen': ['Naam 1', 'Naam 2', 'Naam 3', 'Naam 4'],
                    'postadres': {
                        'huisletter': None,
                        'huisnummer': '1',
                        'huisnummertoevoeging': None,
                        'postcode': '1012 PN',
                        'straatnaam': 'Amstel',
                        'woonplaatsNaam': 'Amsterdam'
                    },
                    'telefoonnummer': None,
                    'typeringVestiging': 'Hoofdvestiging',
                    'vestigingsNummer': '000000000001',
                    'websites': []
                }
            ]
        }

    @patch('mks.service.mks_client_bsn_hr._get_response', get_xml_response_fixture)
    def test_get(self):
        result = mks_client_bsn_hr.get_from_kvk('123456789')

        self.assertEqual(result, self._expected_result())

    @patch('mks.service.mks_client_bsn_hr._get_response', get_xml_response_empty_fixture)
    def test_get_empty(self):
        result = mks_client_bsn_hr.get_from_kvk('123456789')

        self.assertEqual(result, {})
