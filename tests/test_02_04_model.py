import os
from datetime import datetime
from pprint import pprint
from unittest.case import TestCase

from bs4 import BeautifulSoup

# ignoring E402: module level import not at top of file
os.environ['TMA_CERTIFICATE'] = 'cert content'  # noqa: E402
os.environ['BRP_APPLICATIE'] = 'mijnAmsTestApp'  # noqa: E402
os.environ['BRP_GEBRUIKER'] = 'mijnAmsTestUser'  # noqa: E402
os.environ['MKS_BRP_ENDPOINT'] = 'https://example.com'  # noqa: E402

from mks.model.stuf_02_04 import extract_data

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response_0204.xml")


class Model0204Tests(TestCase):
    def get_result(self):
        return {
            'adres': {
                'adresInOnderzoek': False,
                'begindatumVerblijf': datetime(2009, 1, 1, 0, 0),
                'centroidXCoordinaat': None,
                'centroidYCoordinaat': None,
                'centroidZCoordinaat': None,
                'einddatumVerblijf': None,
                'huisletter': None,
                'huisnummer': '1',
                'huisnummertoevoeging': 'I',
                'postcode': '1001 PN',
                'straatnaam': 'Amstel',
                'woonplaatsNaam': 'Amsterdam'
            },
            'identiteitsbewijzen': [
                {
                    'datumAfloop': datetime(2019, 1, 1, 0, 0),
                    'datumUitgifte': datetime(2014, 1, 1, 0, 0),
                    'documentNummer': 'PP01XYZ34',
                    'documentType': 'paspoort'
                }
            ],
            'kinderen': [
                {
                    'adellijkeTitelPredikaat': None,
                    'bsn': '5678901234',
                    'geboorteLand': '6030',
                    'geboortedatum': datetime(2011, 1, 1, 0, 0),
                    'geboortelandnaam': 'Nederland',
                    'geboorteplaats': '947',
                    'geboorteplaatsnaam': 'Neer',
                    'geslachtsaanduiding': 'V',
                    'geslachtsnaam': 'Bakker',
                    'omschrijvingAdellijkeTitel': None,
                    'omschrijvingGeslachtsaanduiding': 'Vrouw',
                    'opgemaakteNaam': None,
                    'overlijdensdatum': None,
                    'voornamen': 'Anne',
                    'voorvoegselGeslachtsnaam': 'van'
                }
            ],
            'ouders': [
                {
                    'adellijkeTitelPredikaat': None,
                    'bsn': '345678901',
                    'geboorteLand': '5012',
                    'geboortedatum': datetime(1961, 1, 1, 0, 0),
                    'geboortelandnaam': 'Iran',
                    'geboorteplaats': 'Teheran',
                    'geboorteplaatsnaam': 'Teheran',
                    'geslachtsaanduiding': 'V',
                    'geslachtsnaam': 'Visser',
                    'omschrijvingAdellijkeTitel': None,
                    'omschrijvingGeslachtsaanduiding': 'Vrouw',
                    'opgemaakteNaam': None,
                    'overlijdensdatum': None,
                    'voornamen': 'Iep',
                    'voorvoegselGeslachtsnaam': None
                },
                {
                    'adellijkeTitelPredikaat': None,
                    'bsn': '4567890123',
                    'geboorteLand': '7035',
                    'geboortedatum': datetime(1951, 1, 1, 0, 0),
                    'geboortelandnaam': 'Japan',
                    'geboorteplaats': 'Tokio',
                    'geboorteplaatsnaam': 'Osaka',
                    'geslachtsaanduiding': 'M',
                    'geslachtsnaam': 'Jansen',
                    'omschrijvingAdellijkeTitel': None,
                    'omschrijvingGeslachtsaanduiding': 'Man',
                    'opgemaakteNaam': None,
                    'overlijdensdatum': None,
                    'voornamen': 'Thomas',
                    'voorvoegselGeslachtsnaam': None
                }
            ],
            'persoon': {
                'aanduidingNaamgebruikOmschrijving': 'Eigen geslachtsnaam',
                'bsn': '1',
                'codeGeboorteland': '6030',
                'codeLandEmigratie': None,
                'datumVertrekUitNederland': None,
                'geboortedatum': datetime(1968, 1, 1, 0, 0),
                'geboortelandnaam': 'Nederland',
                'geboorteplaats': '947',
                'geboorteplaatsnaam': 'Neer',
                'gemeentenaamInschrijving': 'Amsterdam',
                'geslachtsaanduiding': 'M',
                'geslachtsnaam': 'Boer',
                'mokum': True,
                'nationaliteiten': [
                    {
                        'code': 1, 'omschrijving': 'Nederlandse'
                    }
                ],
                'omschrijvingAdellijkeTitel': 'Ridder',
                'omschrijvingBurgerlijkeStaat': 'Gehuwd',
                'omschrijvingGeslachtsaanduiding': 'Man',
                'omschrijvingIndicatieGeheim': 'Geen beperking',
                'opgemaakteNaam': None,
                'vertrokkenOnbekendWaarheen': False,
                'voornamen': 'Johannes',
                'voorvoegselGeslachtsnaam': 'den'
            },
            'verbintenis': {
                'adellijkeTitelPredikaat': None,
                'bsn': '234567890',
                'datumOntbinding': None,
                'datumSluiting': datetime(2000, 1, 1, 0, 0),
                'geboortedatum': datetime(1970, 1, 1, 0, 0),
                'geboortelandnaam': 'Nederland',
                'geboorteplaatsnaam': 'Neer',
                'geslachtsaanduiding': 'V',
                'geslachtsnaam': 'Bakker',
                'landnaamSluiting': 'Nederland',
                'omschrijvingAdellijkeTitel': 'Jonkvrouw',
                'omschrijvingGeslachtsaanduiding': 'Vrouw',
                'opgemaakteNaam': None,
                'overlijdensdatum': None,
                'persoon': {},
                'plaatsnaamSluitingOmschrijving': 'Amsterdam',
                'soortVerbintenis': None,
                'soortVerbintenisOmschrijving': 'Huwelijk',
                'voornamen': 'Wilhelmina',
                'voorvoegselGeslachtsnaam': 'van'
            },
            'verbintenisHistorisch': []
        }

    def test_response(self):
        with open(RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        self.maxDiff = None
        self.assertEqual(result, self.get_result())

        # pprint(result)
