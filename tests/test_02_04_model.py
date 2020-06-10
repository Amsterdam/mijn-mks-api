import os
from datetime import datetime
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
                'inOnderzoek': False,
                'begindatumVerblijf': datetime(2009, 1, 1, 0, 0),
                'centroidXCoordinaat': None,
                'centroidYCoordinaat': None,
                'centroidZCoordinaat': None,
                'einddatumVerblijf': None,
                'huisletter': None,
                'huisnummer': '1',
                'huisnummertoevoeging': 'I',
                'postcode': '1011 PN',
                'straatnaam': 'Amstel',
                'woonplaatsNaam': 'Amsterdam'
            },
            'identiteitsbewijzen': [
                {
                    'datumAfloop': datetime(2025, 1, 1, 0, 0),
                    'datumUitgifte': datetime(2014, 1, 1, 0, 0),
                    'documentNummer': 'PP01XYZ35',
                    'documentType': 'paspoort',
                    'id': '25ee19ff7a9ecb909e2bf5ca044f1f05d2998c98888893c2075240c25a2ff0f7'
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
                },
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
            ],
            'persoon': {
                'aanduidingNaamgebruikOmschrijving': 'Eigen geslachtsnaam',
                'bsn': '1',
                'codeGemeenteVanInschrijving': 363,
                'codeLandEmigratie': None,
                'datumVertrekUitNederland': None,
                'geboortedatum': datetime(1968, 1, 1, 0, 0),
                'geboortelandnaam': 'Nederland',
                'geboorteLand': '6030',
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
                'opgemaakteNaam': "J. den Boer",
                'vertrokkenOnbekendWaarheen': False,
                'voornamen': 'Johannes',
                'voorvoegselGeslachtsnaam': 'den'
            },
            'verbintenis': {
                'datumOntbinding': None,
                'datumSluiting': datetime(2000, 1, 1, 0, 0),
                'landnaamSluiting': 'Nederland',
                'persoon': {
                    'adellijkeTitelPredikaat': None,
                    'bsn': '234567890',
                    'geboortedatum': datetime(1970, 1, 1, 0, 0),
                    'geboortelandnaam': 'Nederland',
                    'geboorteplaatsnaam': 'Neer',
                    'geslachtsaanduiding': 'V',
                    'geslachtsnaam': 'Bakker',
                    'omschrijvingAdellijkeTitel': 'Jonkvrouw',
                    'omschrijvingGeslachtsaanduiding': 'Vrouw',
                    'opgemaakteNaam': None,
                    'overlijdensdatum': None,
                    'voornamen': 'Wilhelmina',
                    'voorvoegselGeslachtsnaam': 'van'
                },
                'plaatsnaamSluitingOmschrijving': 'Amsterdam',
                'soortVerbintenis': None,
                'soortVerbintenisOmschrijving': 'Huwelijk',
            },
            'verbintenisHistorisch': []
        }

    def test_response(self):
        with open(RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        self.maxDiff = None
        self.assertEqual(result, self.get_result())

    # TODO: geslachtsomschrijving being set, geboorteplaatsNaam, geboorteLandnaam
