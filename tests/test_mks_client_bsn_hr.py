import os
from datetime import date
from unittest import TestCase
from unittest.mock import patch

from mks.service import mks_client_bsn_hr

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
BSN_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_bsn_response.xml")
BSN_NO_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_bsn_no_hr_response.xml")


def get_bsn_xml_response_fixture(*args):
    with open(BSN_RESPONSE_PATH, 'rb') as response_file:
        return response_file.read()


def get_bsn_no_hr_xml_response_fixture(*args):
    with open(BSN_NO_RESPONSE_PATH, 'rb') as response_file:
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
                    'activiteiten': ['Overige administratiekantoren', 'Organisatie-adviesbureaus', 'Arbeidsbemiddeling'],
                    'bezoekadres': {
                        'huisletter': None,
                        'huisnummer': '1',
                        'huisnummertoevoeging': None,
                        'postcode': '1011 PN',
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
                        'postcode': '1011 PN',
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

    @patch('mks.service.mks_client_bsn_hr._get_response', get_bsn_xml_response_fixture)
    def test_get(self):
        result = mks_client_bsn_hr.get_from_bsn('123456789')

        self.assertEqual(result, self._get_expected())

    @patch('mks.service.mks_client_bsn_hr._get_response', get_bsn_no_hr_xml_response_fixture)
    def test_no_hr_get(self):
        result = mks_client_bsn_hr.get_from_bsn('123456789')
        self.assertEqual(result, {})
