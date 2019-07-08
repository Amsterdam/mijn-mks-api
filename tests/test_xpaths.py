import json
import os
import unittest

from datetime import datetime
from lxml import objectify

from mks.model.stuff import StuffReply


FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response.xml")
RESPONSE_2_PATH = os.path.join(FIXTURE_PATH, "response2.xml")
RESPONSE_3_PATH = os.path.join(FIXTURE_PATH, "response3.xml")
RESPONSE_4_PATH = os.path.join(FIXTURE_PATH, "response4.xml")


class ResponseTests(unittest.TestCase):

    # noinspection PyAttributeOutsideInit
    def setUp(self):
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
                'geboortedatum': datetime(1988, 1, 1, 0, 0),
                'geboortelandnaam': 'Marokko',
                'geboorteplaatsnaam': 'Mijlaou',
                'gemeentenaamInschrijving': 'Amsterdam',
                'geslachtsnaam': 'Kosterijk',
                'omschrijvingBurgerlijkeStaat': 'Gehuwd',
                'omschrijvingGeslachtsaanduiding': 'Man',
                'opgemaakteNaam': 'A. Kosterijk',
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
                    'geslachtsaanduiding': None,
                    'geslachtsnaam': 'Bakker',
                    'overlijdensdatum': None,
                    'voornamen': 'Souad',
                    'voorvoegselGeslachtsnaam': None
                },
                'plaatsnaamSluitingOmschrijving': 'Asilah',
                'soortVerbintenis': 'H',
                'soortVerbintenisOmschrijving': 'Huwelijk'
            },
            'kinderen': [
                {
                    'bsn': None,
                    'geboortedatum': datetime(2004, 1, 1, 0, 0),
                    'geslachtsaanduiding': 'M',
                    'geslachtsnaam': 'Kosterijk',
                    'overlijdensdatum': None,
                    'voornamen': 'Yassine',
                    'voorvoegselGeslachtsnaam': None},
                {
                    'bsn': None,
                    'geboortedatum': datetime(2008, 1, 1, 0, 0),
                    'geslachtsaanduiding': 'M',
                    'geslachtsnaam': 'Kosterijk',
                    'overlijdensdatum': None,
                    'voornamen': 'Marwan',
                    'voorvoegselGeslachtsnaam': None
                }
            ],
            'adres': {
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

        self.maxDiff = None
        self.assertEqual(result, self.get_result())

    def test_json(self):
        response = self.reply.as_json()
        data = json.loads(response)
        self.assertEqual(data['persoon']['bsn'], '123456789', "bsn niet gevonden")


class MultiplePartnersTest(unittest.TestCase):

    def get_result(self):
        return {
            'datumOntbinding': None,
            'datumSluiting': '1974-01-01T00:00:00',
            'landnaamSluiting': None,
            'persoon': {
                'bsn': '345678901',
                'geboortedatum': '1940-01-01T00:00:00',
                'geslachtsaanduiding': None,
                'geslachtsnaam': 'Dijk',
                'overlijdensdatum': None,
                'voornamen': 'Henk',
                'voorvoegselGeslachtsnaam': None
            },
            'plaatsnaamSluitingOmschrijving': None,
            'soortVerbintenis': None,
            'soortVerbintenisOmschrijving': None
        }

    def setUp(self):
        with open(RESPONSE_4_PATH, 'rb') as responsefile:
            self.reply = StuffReply(
                objectify.fromstring(
                    responsefile.read()
                )
            )

    def test_partners(self):
        response = self.reply.as_json()
        data = json.loads(response)

        # deep equal test
        self.assertEqual(data['verbintenis'], self.get_result())


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
