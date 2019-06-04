import os
import unittest

from lxml import objectify

from mks.model.stuff import StuffReply


FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response.xml")
RESPONSE_2_PATH = os.path.join(FIXTURE_PATH, "response2.xml")
RESPONSE_3_PATH = os.path.join(FIXTURE_PATH, "response3.xml")
RESPONSE_4_PATH = os.path.join(FIXTURE_PATH, "response4.xml")
RESPONSE_4_PARTNER_ORDER_SWITCHED_PATH = os.path.join(FIXTURE_PATH, "response4_partner_order_switched.xml")


class ResponseTests(unittest.TestCase):
    # noinspection PyAttributeOutsideInit
    def setUp(self):
        with open(RESPONSE_PATH, 'rb') as responsefile:
            self.reply = StuffReply(
                objectify.fromstring(
                    responsefile.read()
                )
            )

    def test_funcs(self):
        reply = self.reply
        persoon = reply.get_persoon()
        partner = reply.get_partner()
        kinderen = reply.get_kinderen()

        from pprint import pprint
        print("----")
        pprint(persoon)
        pprint(partner)
        pprint(kinderen)
        print("----")


    def testParseAll(self):
        reply = self.reply

        self.assertCountEqual(
            [kind['gerelateerde'].voornamen for kind in reply.get_kinderen()],
            ['Yassine', 'Marwan'],
            msg='Niet alle items komen overeen')

        self.assertCountEqual(
            [n['gerelateerde'].omschrijving for n in reply.get_nationaliteiten()],
            ['Nederlandse', 'Marokkaanse'],
            msg='Niet alle items komen overeen')

        self.assertEqual(
            reply.get_persoon()['inp.bsn'].pyval,
            123456789,
            msg='Bsn niet gevonden')

        self.assertEqual(
            reply.get_persoon()['geslachtsnaam'].pyval,
            'Kosterijk',
            msg='Geslachtsnaam niet gevonden')

    def test_json(self):
        response = self.reply.as_dict()
        self.assertEqual(response['persoon']['bsn'], '123456789', "bsn niet gevonden")

    def test_content(self):
        response = self.reply.as_dict()
        persoon = response['persoon']

        self.assertEqual(persoon['geslachtsaanduiding'], 'M')
        self.assertEqual(persoon['omschrijvingGeslachtsaanduiding'], 'Man')

        self.assertEqual(persoon['geboorteLand'], '5022')
        self.assertEqual(persoon['geboorteLandNaam'], 'Marokko')

        self.assertEqual(persoon['aanduidingNaamgebruik'], 'E')
        self.assertEqual(persoon['aanduidingNaamgebruikOmschrijving'], 'Eigen geslachtsnaam')

        self.assertEqual(persoon['burgerlijkeStaat'], '2')
        self.assertEqual(persoon['omschrijvingBurgerlijkeStaat'], 'Gehuwd')

        self.assertEqual(persoon['gemeenteVanInschrijving'], '363')
        self.assertEqual(persoon['gemeentenaamInschrijving'], 'Amsterdam')

        self.assertEqual(persoon['heeftAlsEchtgenootPartner']['soortVerbintenis'], 'H')
        self.assertEqual(persoon['heeftAlsEchtgenootPartner']['soortVerbintenisOmschrijving'], 'Huwelijk')

        self.assertEqual(persoon['heeftAlsEchtgenootPartner']['landSluiting'], '5022')
        self.assertEqual(persoon['heeftAlsEchtgenootPartner']['landnaamSluiting'], 'Marokko')

        self.assertEqual(persoon['heeftAlsEchtgenootPartner']['plaatsnaamSluitingOmschrijving'], 'Asilah')
        self.assertEqual(persoon['heeftAlsEchtgenootPartner']['soortVerbintenisOmschrijving'], 'Huwelijk')

        self.assertEqual(persoon['gemeenteVanInschrijving'], '363'),
        self.assertEqual(persoon['gemeentenaamInschrijving'], 'Amsterdam'),

        self.assertEqual(persoon['immigratieLand'], '5022')
        self.assertEqual(persoon['landnaamImmigratie'], 'Marokko')

        self.assertEqual(persoon['opgemaakteNaam'], 'A. Kosterijk')


class MultiplePartnersTest(unittest.TestCase):
    """
        FIXME:
        This test is supposed to test the multiple partners case, but there is insufficient test data available.
        So this test only test that they show up, but not that the extra data gets merged.
    """

    def setUp(self):
        with open(RESPONSE_4_PATH, 'rb') as responsefile:
            self.reply = StuffReply(
                objectify.fromstring(
                    responsefile.read()
                )
            )

    def test_partners(self):
        response = self.reply.as_dict()
        persoon = response['persoon']

        # Test data needs to be improved to test the merging.
        self.assertEqual(persoon['heeftAlsEchtgenootPartner'][0]['gerelateerde']['bsn'], '456789013')
        self.assertEqual(persoon['heeftAlsEchtgenootPartner'][1]['gerelateerde']['bsn'], '456789014')

        self.assertEqual(persoon['heeftAlsEchtgenootPartner'][0]['datumSluiting'], '1974-01-01T00:00:00')
        self.assertFalse(persoon['heeftAlsEchtgenootPartner'][0].get('datumOntbinding', False))
        # test data does not have datumSluiting for ex-partner
        self.assertEqual(persoon['heeftAlsEchtgenootPartner'][1]['datumOntbinding'], '1973-01-01T00:00:00')


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
