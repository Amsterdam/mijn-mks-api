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
        return [
            {
                'activities': [
                    {
                        'activities': [
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
                        'datumAanvang': date(1992, 1, 1),
                        'datumEinde': date(2020, 1, 1),
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
                ],
                'datumAanvang': date(1992, 1, 1),
                'datumEinde': date(2020, 1, 1),
                'kvkNummer': '12345678'
            }
        ]

    @patch('mks.service.mks_client_bsn_hr._get_response', get_bsn_xml_response_fixture)
    def test_get(self):
        result = mks_client_bsn_hr.get_from_bsn('123456789')

        self.assertEqual(result, self._get_expected())
