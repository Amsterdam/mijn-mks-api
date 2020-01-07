import os
import unittest

from datetime import datetime
from lxml import objectify

# ignoring E402: module level import not at top of file
os.environ['TMA_CERTIFICATE'] = 'cert content'  # noqa: E402
os.environ['BRP_APPLICATIE'] = 'mijnAmsTestApp'  # noqa: E402
os.environ['BRP_GEBRUIKER'] = 'mijnAmsTestUser'  # noqa: E402
os.environ['MKS_BRP_ENDPOINT'] = 'https://example.com'  # noqa: E402

from mks.model.stuff import StuffReply


FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response.xml")
RESPONSE_2_PATH = os.path.join(FIXTURE_PATH, "response2.xml")
RESPONSE_3_PATH = os.path.join(FIXTURE_PATH, "response3.xml")
RESPONSE_4_PATH = os.path.join(FIXTURE_PATH, "response4.xml")
RESPONSE_NIET_AMSTERDAMMER = os.path.join(FIXTURE_PATH, "niet_amsterdammer.xml")
RESPONSE_VERTROKKEN_ONBEKEND_WAARHEEN = os.path.join(FIXTURE_PATH, "response-vertrokken-onbekend-waarheen.xml")


class ResponseTests(unittest.TestCase):

    # noinspection PyAttributeOutsideInit
    def setUp(self):
        self.maxDiff = None
        with open(RESPONSE_PATH, 'rb') as responsefile:
            self.reply = StuffReply(
                objectify.fromstring(
                    responsefile.read()
                )
            )

    def get_result(self):
        return {
            'persoon': {
                'aanduidingNaamgebruikOmschrijving': 'Eigen geslachtsnaam',
                'bsn': '123456789',
                'datumVertrekUitNederland': None,
                'emigratieLand': None,
                'geboorteLand': '5022',
                'geboortedatum': datetime(1988, 1, 1, 0, 0),
                'geboortelandnaam': 'Marokko',
                'geboorteplaatsnaam': 'Mijlaou',
                'geboorteplaats': 'Mijlaou',
                'gemeentenaamInschrijving': 'Amsterdam',
                'geslachtsaanduiding': 'M',
                'geslachtsnaam': 'Kosterijk',
                'mokum': True,
                'omschrijvingBurgerlijkeStaat': 'Gehuwd',
                'omschrijvingGeslachtsaanduiding': 'Man',
                'omschrijvingIndicatieGeheim': 'Geen beperking',
                'omschrijvingAdellijkeTitel': None,
                'opgemaakteNaam': 'A. Kosterijk',
                'vertrokkenOnbekendWaarheen': False,
                'voornamen': 'Abdelouahed',
                'voorvoegselGeslachtsnaam': None,
                'nationaliteiten': [
                    {'omschrijving': 'Nederlandse'},
                    {'omschrijving': 'Marokkaanse'}
                ],
            },
            'verbintenis': {
                'datumOntbinding': None,
                'datumSluiting': datetime(1999, 1, 1, 0, 0),
                'landnaamSluiting': 'Marokko',
                'persoon': {
                    'bsn': '123456780',
                    'geboortedatum': datetime(1985, 1, 1, 0, 0),
                    'adellijkeTitelPredikaat': None,
                    'geslachtsaanduiding': None,
                    'geslachtsnaam': 'Bakker',
                    'overlijdensdatum': None,
                    'voornamen': 'Souad',
                    'voorvoegselGeslachtsnaam': None,
                    'omschrijvingGeslachtsaanduiding': None,
                },
                'plaatsnaamSluitingOmschrijving': 'Asilah',
                'soortVerbintenis': 'H',
                'soortVerbintenisOmschrijving': 'Huwelijk',
            },
            'verbintenisHistorisch': [],
            'kinderen': [
                {
                    'bsn': None,
                    'geboortedatum': datetime(2004, 1, 1, 0, 0),
                    'geslachtsaanduiding': 'M',
                    'omschrijvingGeslachtsaanduiding': 'Man',
                    'geslachtsnaam': 'Kosterijk',
                    'geboorteLand': None,
                    'geboorteplaats': None,
                    'overlijdensdatum': None,
                    'adellijkeTitelPredikaat': None,
                    'voornamen': 'Yassine',
                    'voorvoegselGeslachtsnaam': None},
                {
                    'bsn': None,
                    'geboortedatum': datetime(2008, 1, 1, 0, 0),
                    'geslachtsaanduiding': 'M',
                    'omschrijvingGeslachtsaanduiding': 'Man',
                    'geboorteLand': None,
                    'geboorteplaats': None,
                    'geslachtsnaam': 'Kosterijk',
                    'overlijdensdatum': None,
                    'adellijkeTitelPredikaat': None,
                    'voornamen': 'Marwan',
                    'voorvoegselGeslachtsnaam': None
                }
            ],
            'ouders': [
                {
                    'adellijkeTitelPredikaat': None,
                    'bsn': None,
                    'geboorteLand': None,
                    'geboortedatum': datetime(1939, 1, 1, 0, 0),
                    'geboorteplaats': None,
                    'geslachtsaanduiding': 'M',
                    'geslachtsnaam': 'Kosterijk',
                    'omschrijvingGeslachtsaanduiding': 'Man',
                    'overlijdensdatum': None,
                    'voornamen': 'El Mokhtar',
                    'voorvoegselGeslachtsnaam': None},
                {
                    'adellijkeTitelPredikaat': None,
                    'bsn': None,
                    'geboorteLand': None,
                    'geboortedatum': datetime(1944, 1, 1, 0, 0),
                    'geboorteplaats': None,
                    'geslachtsaanduiding': 'V',
                    'geslachtsnaam': 'Visser',
                    'omschrijvingGeslachtsaanduiding': 'Vrouw',
                    'overlijdensdatum': None,
                    'voornamen': 'Rahma',
                    'voorvoegselGeslachtsnaam': None}
            ],
            'adres': {
                'adresInOnderzoek': False,
                'begindatumVerblijf': datetime(1995, 1, 1, 0, 0),
                'huisletter': None,
                'huisnummer': '1',
                'huisnummertoevoeging': '1',
                'postcode': '1011 PN',
                'straatnaam': 'Amstel',
                'woonplaatsNaam': 'Amsterdam'
            },
        }

    def test_content(self):
        reply = self.reply

        result = reply.as_dict()

        self.assertEqual(result, self.get_result())

    def test_data(self):
        data = self.reply.as_dict()
        self.assertEqual(data['persoon']['bsn'], '123456789', "bsn niet gevonden")


class MultiplePartnersTest(unittest.TestCase):

    def get_result(self):
        return {
            'datumOntbinding': None,
            'datumSluiting': datetime(1974, 1, 1, 0, 0),
            'landnaamSluiting': None,
            'persoon': {
                'bsn': '345678901',
                'geboortedatum': datetime(1940, 1, 1, 0, 0),
                'geslachtsaanduiding': None,
                'omschrijvingGeslachtsaanduiding': None,
                'geslachtsnaam': 'Dijk',
                'adellijkeTitelPredikaat': None,
                'overlijdensdatum': None,
                'voornamen': 'Henk',
                'voorvoegselGeslachtsnaam': None
            },
            'plaatsnaamSluitingOmschrijving': None,
            'soortVerbintenis': None,
            'soortVerbintenisOmschrijving': None
        }

    def get_result_history(self):
        # lots of None's because example test data isn't great
        return [
            {
                'datumOntbinding': datetime(1973, 1, 1, 0, 0),
                'datumSluiting': None,
                'landnaamSluiting': None,
                'persoon': {
                    'adellijkeTitelPredikaat': None,
                    'bsn': '234567890',
                    'geboortedatum': datetime(1921, 1, 1, 0, 0),
                    'geslachtsaanduiding': None,
                    'geslachtsnaam': 'Oever',
                    'omschrijvingGeslachtsaanduiding': None,
                    'overlijdensdatum': None,
                    'voornamen': 'Erik',
                    'voorvoegselGeslachtsnaam': 'van den'
                },
                'plaatsnaamSluitingOmschrijving': None,
                'soortVerbintenis': None,
                'soortVerbintenisOmschrijving': None
            }
        ]

    def setUp(self):
        self.maxDiff = None
        with open(RESPONSE_4_PATH, 'rb') as responsefile:
            self.reply = StuffReply(
                objectify.fromstring(
                    responsefile.read()
                )
            )

    def test_partners(self):
        data = self.reply.as_dict()

        # deep equal test
        self.assertEqual(data['verbintenis'], self.get_result())
        self.assertEqual(data['verbintenisHistorisch'], self.get_result_history())


class NonAmsterdamTest(unittest.TestCase):
    def setUp(self) -> None:
        with open(RESPONSE_NIET_AMSTERDAMMER, 'rb') as responsefile:
            self.reply = StuffReply(
                objectify.fromstring(
                    responsefile.read()
                )
            )

    def test_nationaliteit(self):
        data = self.reply.as_dict()
        self.assertEqual(data['persoon']['nationaliteiten'][0]['omschrijving'], "Nederlandse")
        self.assertEqual(len(data['persoon']['nationaliteiten']), 1)


class VertrokkenOnbekendWaarheenTest(unittest.TestCase):
    def setUp(self) -> None:
        with open(RESPONSE_VERTROKKEN_ONBEKEND_WAARHEEN, 'rb') as responsefile:
            self.reply = StuffReply(
                objectify.fromstring(
                    responsefile.read()
                )
            )

    def test_vow(self):
        data = self.reply.as_dict()
        self.assertEqual(data['persoon']['vertrokkenOnbekendWaarheen'], True)
        self.assertEqual(data['persoon']['datumVertrekUitNederland'], datetime(2019, 1, 1, 0, 0))


class ResponsesTest(unittest.TestCase):
    def test_json(self):
        for response_path in [RESPONSE_2_PATH, RESPONSE_3_PATH, RESPONSE_4_PATH]:
            with open(response_path, 'rb') as responsefile:
                reply = StuffReply(
                    objectify.fromstring(
                        responsefile.read()
                    )
                )

                response = reply.as_dict()
                self.assertTrue(response['persoon']['bsn'], "bsn niet gevonden")
