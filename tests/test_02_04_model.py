import os
from datetime import datetime
from unittest import TestCase

from bs4 import BeautifulSoup

# ignoring E402: module level import not at top of file
os.environ['TMA_CERTIFICATE'] = 'cert content'
os.environ['BRP_APPLICATIE'] = 'mijnAmsTestApp'
os.environ['BRP_GEBRUIKER'] = 'mijnAmsTestUser'
os.environ['MKS_BRP_ENDPOINT'] = 'https://example.com'
os.environ['MKS_JWT_KEY'] = "RsKzMu5cIx92FSzLZz1RmsdLg7wJQPTwsCrkOvNNlqg"

from mks.model.stuf_02_04 import extract_data, get_nationaliteiten, set_opgemaakte_naam  # noqa: E402

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response_0204.xml")
RESPONSE_NO_KIDS_PARENTS_ID_PARTNERS_ADR = os.path.join(FIXTURE_PATH, "response_0204_no_kids_parents_idb_partners_adr.xml")
RESPONSE_IDB = os.path.join(FIXTURE_PATH, "response_0204_idb_test.xml")
RESPONSE_PUNTADRES = os.path.join(FIXTURE_PATH, "response_0204_puntadres.xml")
VOW_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response_0204_vertrokkenonbekendwaarheen.xml")
VOW_NOT_FROM_AMSTERDAM_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response_0204_vertrokkenonbekendwaarheen_not_from_amsterdam.xml")
EMIGRATION_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response_0204_emigration.xml")


class Model0204Tests(TestCase):
    def get_result(self):
        return {
            'adres': {
                'adresBuitenland1': None,
                'adresBuitenland2': None,
                'adresBuitenland3': None,
                # '_adresSleutel':  # changes each time!
                'inOnderzoek': True,
                'begindatumVerblijf': datetime(2012, 1, 1, 0, 0),
                'einddatumVerblijf': None,
                'huisletter': None,
                'huisnummer': '1',
                'huisnummertoevoeging': 'I',
                'postcode': '1011 PN',
                'landnaam': 'Nederland',
                'straatnaam': 'Amstel',
                'woonplaatsNaam': 'Amsterdam',
                'landcode': '6030'
            },
            'adresHistorisch': [
                {
                    'adresBuitenland1': None,
                    'adresBuitenland2': None,
                    'adresBuitenland3': None,
                    'begindatumVerblijf': datetime(2005, 1, 1, 0, 0),
                    'einddatumVerblijf': datetime(2012, 1, 1, 0, 0),
                    'huisletter': None,
                    'huisnummer': '2',
                    'huisnummertoevoeging': 'H',
                    'inOnderzoek': False,
                    'postcode': '1011 PN',
                    'straatnaam': 'Amstel',
                    'woonplaatsNaam': 'Amsterdam',
                    'landcode': '6030',
                    'landnaam': 'Nederland',
                },
                {
                    'adresBuitenland1': None,
                    'adresBuitenland2': None,
                    'adresBuitenland3': None,
                    'begindatumVerblijf': datetime(1990, 1, 1, 0, 0),
                    'einddatumVerblijf': datetime(2005, 1, 1, 0, 0),
                    'huisletter': None,
                    'huisnummer': '3',
                    'huisnummertoevoeging': '3',
                    'inOnderzoek': False,
                    'postcode': '1011 PB',
                    'straatnaam': 'Amstel',
                    'woonplaatsNaam': 'Amsterdam',
                    'landcode': '6030',
                    'landnaam': 'Nederland',
                }
            ],
            'identiteitsbewijzen': [
                {
                    'datumAfloop': datetime(2025, 1, 1, 0, 0),
                    'datumUitgifte': datetime(2014, 1, 1, 0, 0),
                    'documentNummer': 'PP01XYZ35',
                    'documentType': 'paspoort',
                    'id': '25ee19ff7a9ecb909e2bf5ca044f1f05d2998c98888893c2075240c25a2ff0f7'
                },
                {
                    'datumAfloop': datetime(2025, 1, 1, 0, 0),
                    'datumUitgifte': datetime(2014, 1, 1, 0, 0),
                    'documentNummer': 'PP12XYZ456',
                    'documentType': 'paspoort',
                    'id': '52882470c67c063666cedc1e01779db71d186c2cffd818af2dd5d8ec021677f0'
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
                'aanduidingNaamgebruik': 'E',
                'aanduidingNaamgebruikOmschrijving': 'Eigen geslachtsnaam',
                'bsn': '000000001',
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
                'indicatieGeheim': False,
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
                'redenOntbindingOmschrijving': 'Overlijden',
            },
            'verbintenisHistorisch': []
        }

    def test_response(self):
        with open(RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        self.maxDiff = None
        self.assertEqual(type(result['adres']['_adresSleutel']), str)
        del result['adres']['_adresSleutel']  # changes each time
        self.assertEqual(result, self.get_result())

    def test_prs_indicatiegeheim(self):
        with open(RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        # test_response tests 0 value

        # test 1
        tree.find('indicatieGeheim').string = '1'
        result = extract_data(tree)
        self.assertEqual(result['persoon']['indicatieGeheim'], True)

    def test_reden_ontbinding(self):
        with open(RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        tree.find('redenOntbinding').string = 'S'
        result = extract_data(tree)

        self.assertEqual(result['verbintenis']['redenOntbindingOmschrijving'], 'Echtscheiding')

        tree.find('redenOntbinding').string = 'X'
        result = extract_data(tree)

        self.assertEqual(result['verbintenis']['redenOntbindingOmschrijving'], None)

    # TODO: geslachtsomschrijving being set, geboorteplaatsNaam, geboorteLandnaam

    def test_get_multi_nationaliteiten(self):
        # Cleaned up, does not contain stuff we do not use.
        nationaliteiten_xml = """
        <BG:PRS>
          <BG:PRSNAT soortEntiteit="R" StUF:sleutelVerzendend="1" StUF:sleutelGegevensbeheer="1">
            <BG:datumVerkrijging>19700101</BG:datumVerkrijging>
            <BG:datumVerlies xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:NAT soortEntiteit="T">
              <BG:code>54</BG:code>
              <BG:omschrijving>Deense</BG:omschrijving>
            </BG:NAT>
          </BG:PRSNAT>

          <BG:PRSNAT soortEntiteit="R" StUF:sleutelVerzendend="1" StUF:sleutelGegevensbeheer="1">
            <BG:datumVerkrijging xsi:nil="true" StUF:noValue="waardeOnbekend"/>
            <BG:datumVerlies>19650101</BG:datumVerlies>
            <BG:NAT soortEntiteit="T">
              <BG:code>1</BG:code>
              <BG:omschrijving>Nederlandse</BG:omschrijving>
            </BG:NAT>
          </BG:PRSNAT>

          <BG:PRSNAT soortEntiteit="R" StUF:sleutelVerzendend="1" StUF:sleutelGegevensbeheer="1">
            <BG:datumVerkrijging xsi:nil="true" StUF:noValue="waardeOnbekend"/>
            <BG:datumVerlies xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:NAT soortEntiteit="T">
              <BG:code>52</BG:code>
              <BG:omschrijving>Belgische</BG:omschrijving>
            </BG:NAT>
          </BG:PRSNAT>

          <!-- one where nationaliteit is not set so it has to be taken from the translation table -->
          <BG:PRSNAT soortEntiteit="R" StUF:sleutelVerzendend="1" StUF:sleutelGegevensbeheer="1">
            <BG:datumVerkrijging xsi:nil="true" StUF:noValue="waardeOnbekend"/>
            <BG:datumVerlies xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:NAT soortEntiteit="T">
              <BG:code>336</BG:code>
              <BG:omschrijving></BG:omschrijving>
            </BG:NAT>
          </BG:PRSNAT>
        </BG:PRS>
        """

        tree = BeautifulSoup(nationaliteiten_xml, features='lxml-xml')
        result = get_nationaliteiten(tree.find_all("PRSNAT"))

        expected = [{'omschrijving': 'Deense', 'code': 54}, {'omschrijving': 'Belgische', 'code': 52}, {'code': 336, 'omschrijving': 'Syrische'}]
        self.assertEqual(result, expected)

    def test_vertrokken_onbekend_waarheen(self):
        """ Test if the person has status vertrokken onbekend waarheen. """

        with open(VOW_RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        self.assertEqual(result['persoon']['vertrokkenOnbekendWaarheen'], True)

    def test_vertrokken_onbekend_waarheen_not_from_amsterdam(self):
        """ Test if the person has status vertrokken onbekend waarheen. """

        with open(VOW_NOT_FROM_AMSTERDAM_RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        self.assertEqual(result['persoon']['vertrokkenOnbekendWaarheen'], False)

    def test_extraction_no_kids_parents_id_partners(self):
        """ Test if the person has status vertrokken onbekend waarheen. """

        with open(RESPONSE_NO_KIDS_PARENTS_ID_PARTNERS_ADR) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        self.assertEqual(result['kinderen'], [])
        self.assertEqual(result['ouders'], [])
        self.assertEqual(result['verbintenis'], {})
        self.assertEqual(result['verbintenisHistorisch'], [])
        self.assertEqual(result['identiteitsbewijzen'], [])
        self.assertEqual(result['adres'], {})
        self.assertEqual(result['adresHistorisch'], [])
        self.assertEqual(result['persoon']['nationaliteiten'], [])

        self.assertFalse(result['persoon']['vertrokkenOnbekendWaarheen'])

    def test_punt_adres(self):
        """ Test if the person has status adres in onderzoek. """

        with open(RESPONSE_PUNTADRES) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        self.assertEqual(result['adres']['inOnderzoek'], True)
        # check that the previous adres is used
        self.assertEqual(result['adres']['postcode'], '1011 PN')
        self.assertEqual(result['adresHistorisch'], [])

    def test_emigration(self):
        """ Test the address with a adres outside of NL. """
        with open(EMIGRATION_RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        self.assertEqual(result['adres']['adresBuitenland1'], '89 Woodcote Road')
        self.assertEqual(result['adres']['adresBuitenland2'], 'Caversham Heights')
        self.assertEqual(result['adres']['adresBuitenland3'], 'RG4 7EZ')
        self.assertEqual(result['adres']['landnaam'], 'Groot-Brittannië')

        self.assertEqual(result['persoon']['vertrokkenOnbekendWaarheen'], False)

        self.assertEqual(result['adresHistorisch'][0]['straatnaam'], 'Amstel')

    def test_set_opgemaakte_naam(self):
        """ Test set_opgemaakte_naam() """
        def get_persoon():
            return {
                'opgemaakteNaam': None,
                'voornamen': 'Voornaam Voornaam2',
                'geslachtsnaam': 'eigengeslachtsnaam',
                'aanduidingNaamgebruik': 'E',
                'voorvoegselGeslachtsnaam': 'ter'
            }

        verbintenissen = []
        persoon = get_persoon()
        persoon['voorvoegselGeslachtsnaam'] = ''
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(persoon['opgemaakteNaam'], 'V.V. eigengeslachtsnaam')

        persoon = get_persoon()
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(persoon['opgemaakteNaam'], 'V.V. ter eigengeslachtsnaam')

        verbintenissen = [
            {
                'geslachtsnaam': 'partnergeslachtsnaam',
                'voorvoegselGeslachtsnaam': 'van'
            }, {
                'geslachtsnaam': 'foute partnergeslachtsnaam',
                'voorvoegselGeslachtsnaam': 'van'
            }
        ]

        persoon = get_persoon()
        persoon['aanduidingNaamgebruik'] = 'N'
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(persoon['opgemaakteNaam'], 'V.V. ter eigengeslachtsnaam - van partnergeslachtsnaam')

        persoon = get_persoon()
        persoon['aanduidingNaamgebruik'] = 'V'
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(persoon['opgemaakteNaam'], 'V.V. van partnergeslachtsnaam - ter eigengeslachtsnaam')

        persoon = get_persoon()
        persoon['aanduidingNaamgebruik'] = 'P'
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(persoon['opgemaakteNaam'], 'V.V. van partnergeslachtsnaam')

    def test_idb_allow_list(self):
        with open(RESPONSE_IDB) as fp:
            tree = BeautifulSoup(fp.read(), features='lxml-xml')

        result = extract_data(tree)

        # one extra (5), because type 2 becomes type 10
        self.assertEqual(len(result['identiteitsbewijzen']), 5)

        doc_types = [d['documentType'] for d in result['identiteitsbewijzen']]
        expected = ['paspoort', 'nederlandse identiteitskaart', 'nederlandse identiteitskaart', 'vluchtelingenpaspoort', 'vreemdelingenpaspoort']
        self.assertEqual(doc_types, expected)
