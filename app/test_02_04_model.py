from datetime import date
import os
from unittest import TestCase

from bs4 import BeautifulSoup
from app.model.stuf_02_04 import (
    extract_data,
    extract_verbintenis_data,
    get_nationaliteiten,
    set_opgemaakte_naam,
)
from app.model.stuf_utils import to_date

os.environ["TMA_CERTIFICATE"] = "cert content"
os.environ["BRP_APPLICATIE"] = "mijnAmsTestApp"
os.environ["BRP_GEBRUIKER"] = "mijnAmsTestUser"
os.environ["MKS_BRP_ENDPOINT"] = "https://example.com"
os.environ["MKS_JWT_KEY"] = "RsKzMu5cIx92FSzLZz1RmsdLg7wJQPTwsCrkOvNNlqg"


FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response_0204.xml")
RESPONSE_NO_KIDS_PARENTS_ID_PARTNERS_ADR = os.path.join(
    FIXTURE_PATH, "response_0204_no_kids_parents_idb_partners_adr.xml"
)
RESPONSE_IDB = os.path.join(FIXTURE_PATH, "response_0204_idb_test.xml")
RESPONSE_ADRES_ONDERZOEK = os.path.join(
    FIXTURE_PATH, "response_0204_adres_in_onderzoek1.xml"
)
VOW_RESPONSE_PATH = os.path.join(
    FIXTURE_PATH, "response_0204_vertrokkenonbekendwaarheen.xml"
)
VOW_NOT_FROM_AMSTERDAM_RESPONSE_PATH = os.path.join(
    FIXTURE_PATH, "response_0204_vertrokkenonbekendwaarheen_not_from_amsterdam.xml"
)
EMIGRATION_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "response_0204_emigration.xml")

ONTBINDING_RESPOSNE_PATH = os.path.join(FIXTURE_PATH, "response_0204_ontbinding.xml")


class Model0204Tests(TestCase):
    def get_result(self):
        self.maxDiff = None
        return {
            "adres": {
                # '_adresSleutel':  # changes each time!
                "begindatumVerblijf": date(2012, 1, 1),
                "einddatumVerblijf": None,
                "huisletter": None,
                "huisnummer": "1",
                "huisnummertoevoeging": "I",
                "postcode": "1011 PN",
                "landnaam": "Nederland",
                "straatnaam": "Amstel",
                "woonplaatsNaam": "Amsterdam",
                "landcode": "6030",
            },
            "adresHistorisch": [
                {
                    "begindatumVerblijf": date(2005, 1, 1),
                    "einddatumVerblijf": date(2012, 1, 1),
                    "huisletter": None,
                    "huisnummer": "2",
                    "huisnummertoevoeging": "H",
                    "postcode": "1011 PN",
                    "straatnaam": "Amstel",
                    "woonplaatsNaam": "Amsterdam",
                    "landcode": "6030",
                    "landnaam": "Nederland",
                },
                {
                    "begindatumVerblijf": date(1990, 1, 1),
                    "einddatumVerblijf": date(2005, 1, 1),
                    "huisletter": None,
                    "huisnummer": "3",
                    "huisnummertoevoeging": "3",
                    "postcode": "1011 PB",
                    "straatnaam": "Amstel",
                    "woonplaatsNaam": "Amsterdam",
                    "landcode": "6030",
                    "landnaam": "Nederland",
                },
                {
                    "begindatumVerblijf": date(1970, 1, 1),
                    "einddatumVerblijf": None,
                    "huisletter": None,
                    "huisnummer": "3333",
                    "huisnummertoevoeging": "3",
                    "postcode": "1011 PB",
                    "straatnaam": "Amstel",
                    "woonplaatsNaam": "Amsterdam",
                    "landcode": "6030",
                    "landnaam": "Nederland",
                },
            ],
            "identiteitsbewijzen": [
                {
                    "datumAfloop": date(2025, 1, 1),
                    "datumUitgifte": date(2014, 1, 1),
                    "documentNummer": "PP01XYZ35",
                    "documentType": "paspoort",
                    "id": "25ee19ff7a9ecb909e2bf5ca044f1f05d2998c98888893c2075240c25a2ff0f7",
                },
                {
                    "datumAfloop": date(2025, 1, 1),
                    "datumUitgifte": date(2014, 1, 1),
                    "documentNummer": "PP12XYZ456",
                    "documentType": "paspoort",
                    "id": "52882470c67c063666cedc1e01779db71d186c2cffd818af2dd5d8ec021677f0",
                },
            ],
            "kinderen": [
                {
                    "adellijkeTitelPredikaat": None,
                    "bsn": "567890123",
                    "geboorteLand": "6030",
                    "geboortedatum": date(2011, 1, 1),
                    "geregistreerdeGeboortedatum": '1 January 2011',
                    "geboortelandnaam": "Nederland",
                    "geboorteplaats": "947",
                    "geboorteplaatsnaam": "Neer",
                    "geslachtsaanduiding": "V",
                    "geslachtsnaam": "Bakker",
                    "omschrijvingAdellijkeTitel": None,
                    "omschrijvingGeslachtsaanduiding": "Vrouw",
                    "opgemaakteNaam": None,
                    "overlijdensdatum": None,
                    "voornamen": "Anne",
                    "voorvoegselGeslachtsnaam": "van",
                }
            ],
            "ouders": [
                {
                    "adellijkeTitelPredikaat": None,
                    "bsn": "456789012",
                    "geboorteLand": "7035",
                    "geboortedatum": date(1951, 1, 1),
                    "geregistreerdeGeboortedatum": '1 January 1951',
                    "geboortelandnaam": "Japan",
                    "geboorteplaats": "Tokio",
                    "geboorteplaatsnaam": "Osaka",
                    "geslachtsaanduiding": "M",
                    "geslachtsnaam": "Jansen",
                    "omschrijvingAdellijkeTitel": None,
                    "omschrijvingGeslachtsaanduiding": "Man",
                    "opgemaakteNaam": None,
                    "overlijdensdatum": None,
                    "voornamen": "Thomas",
                    "voorvoegselGeslachtsnaam": None,
                },
                {
                    "adellijkeTitelPredikaat": None,
                    "bsn": "345678901",
                    "geboorteLand": "5012",
                    "geboortedatum": date(1961, 1, 1),
                    "geregistreerdeGeboortedatum": '1 January 1961',
                    "geboortelandnaam": "Iran",
                    "geboorteplaats": "Teheran",
                    "geboorteplaatsnaam": "Teheran",
                    "geslachtsaanduiding": "V",
                    "geslachtsnaam": "Visser",
                    "omschrijvingAdellijkeTitel": None,
                    "omschrijvingGeslachtsaanduiding": "Vrouw",
                    "opgemaakteNaam": None,
                    "overlijdensdatum": None,
                    "voornamen": "Iep",
                    "voorvoegselGeslachtsnaam": None,
                },
            ],
            "persoon": {
                "aanduidingNaamgebruik": "E",
                "aanduidingNaamgebruikOmschrijving": "Eigen geslachtsnaam",
                "bsn": "000000001",
                "codeGemeenteVanInschrijving": 363,
                "codeLandEmigratie": None,
                "datumVertrekUitNederland": None,
                "geboortedatum": date(1968, 1, 1),
                "geregistreerdeGeboortedatum": '1 January 1968',
                "geboortelandnaam": "Nederland",
                "geboorteLand": "6030",
                "geboorteplaats": "947",
                "geboorteplaatsnaam": "Neer",
                "gemeentenaamInschrijving": "Amsterdam",
                "geslachtsaanduiding": "M",
                "geslachtsnaam": "Boer",
                "mokum": True,
                "nationaliteiten": [{"code": 1, "omschrijving": "Nederlandse"}],
                "omschrijvingAdellijkeTitel": "Ridder",
                "omschrijvingBurgerlijkeStaat": "Gehuwd",
                "omschrijvingGeslachtsaanduiding": "Man",
                "omschrijvingIndicatieGeheim": "Geen beperking",
                "indicatieGeheim": False,
                "opgemaakteNaam": "J. den Boer",
                "vertrokkenOnbekendWaarheen": False,
                "voornamen": "Johannes",
                "voorvoegselGeslachtsnaam": "den",
                "adresInOnderzoek": "080000",  # Value provided by adrins.extraelement.aanduidingGegevensInOnderzoek
            },
            "verbintenis": {},
            "verbintenisHistorisch": [
                {
                    "datumOntbinding": None,
                    "datumSluiting": date(2000, 1, 1),
                    "landnaamSluiting": "Nederland",
                    "persoon": {
                        "adellijkeTitelPredikaat": None,
                        "bsn": "234567890",
                        "geboortedatum": date(1970, 1, 1),
                        "geregistreerdeGeboortedatum": '1 January 1970',
                        "geboortelandnaam": "Nederland",
                        "geboorteplaatsnaam": "Neer",
                        "geslachtsaanduiding": "V",
                        "geslachtsnaam": "Bakker",
                        "omschrijvingAdellijkeTitel": "Jonkvrouw",
                        "omschrijvingGeslachtsaanduiding": "Vrouw",
                        "opgemaakteNaam": None,
                        "overlijdensdatum": None,
                        "voornamen": "Wilhelmina",
                        "voorvoegselGeslachtsnaam": "van",
                    },
                    "plaatsnaamSluitingOmschrijving": "Amsterdam",
                    "soortVerbintenis": None,
                    "soortVerbintenisOmschrijving": "Huwelijk",
                    "redenOntbindingOmschrijving": "Overlijden",
                }
            ],
        }

    def test_response(self):
        with open(RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        result = extract_data(tree)

        self.assertEqual(type(result["adres"]["_adresSleutel"]), str)
        del result["adres"]["_adresSleutel"]  # changes each time
        self.assertEqual(result, self.get_result())

    def test_prs_indicatiegeheim(self):
        with open(RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        # test_response tests 0 value

        # test 1
        tree.find("indicatieGeheim").string = "1"
        result = extract_data(tree)
        self.assertEqual(result["persoon"]["indicatieGeheim"], True)

    def test_reden_ontbinding(self):
        with open(RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        tree.find("redenOntbinding").string = "S"
        result = extract_data(tree)

        self.assertEqual(
            result["verbintenisHistorisch"][0]["redenOntbindingOmschrijving"],
            "Echtscheiding",
        )

        tree.find("redenOntbinding").string = "X"
        result = extract_data(tree)

        self.assertEqual(result["verbintenis"]["redenOntbindingOmschrijving"], None)

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

        tree = BeautifulSoup(nationaliteiten_xml, features="lxml-xml")
        result = get_nationaliteiten(tree.find_all("PRSNAT"))

        expected = [
            {"omschrijving": "Deense", "code": 54},
            {"omschrijving": "Belgische", "code": 52},
            {"code": 336, "omschrijving": "Syrische"},
        ]
        self.assertEqual(result, expected)

    def test_verbintenissen(self):
        response_xml = """
        <BG:PRS>
        <BG:PRSPRSHUW soortEntiteit="R" StUF:sleutelVerzendend="10" StUF:sleutelGegevensbeheer="10">
            <BG:datumSluiting>20000101</BG:datumSluiting>
            <BG:plaatsSluiting>363</BG:plaatsSluiting>
            <BG:landSluiting>6030</BG:landSluiting>
            <BG:datumOntbinding xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:redenOntbinding xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:extraElementen>
              <StUF:extraElement naam="aanduidingGegevensInOnderzoek" xsi:nil="true" StUF:noValue="nietGeautoriseerd"/>
              <StUF:extraElement naam="landnaamOntbinding" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="landnaamSluiting">Nederland</StUF:extraElement>
              <StUF:extraElement naam="plaatsnaamOntbindingOmschrijving" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="plaatsnaamSluitingOmschrijving">Amsterdam</StUF:extraElement>
              <StUF:extraElement naam="redenOntbindingOmschrijving" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="soortVerbintenisOmschrijving">Huwelijk</StUF:extraElement>
            </BG:extraElementen>
            <BG:PRS soortEntiteit="F" StUF:sleutelVerzendend="10" StUF:sleutelGegevensbeheer="10">
              <BG:bsn-nummer>234567890</BG:bsn-nummer>
              <BG:voornamen>Wilhelmina</BG:voornamen>
              <BG:voorletters>W</BG:voorletters>
              <BG:voorvoegselGeslachtsnaam>van</BG:voorvoegselGeslachtsnaam>
              <BG:geslachtsnaam>Bakker</BG:geslachtsnaam>
              <BG:geboortedatum>19700101</BG:geboortedatum>
              <BG:geslachtsaanduiding>V</BG:geslachtsaanduiding>
              <BG:datumOverlijden xsi:nil="true" StUF:noValue="geenWaarde"/>
              <BG:aanduidingNaamgebruik xsi:nil="true" StUF:noValue="nietGeautoriseerd"/>
              <BG:extraElementen>
                <StUF:extraElement naam="geboortelandnaam">Nederland</StUF:extraElement>
                <StUF:extraElement naam="geboorteplaatsnaam">Neer</StUF:extraElement>
                <StUF:extraElement naam="omschrijvingAdellijkeTitel">Jonkvrouw</StUF:extraElement>
                <StUF:extraElement naam="omschrijvingGeslachtsaanduiding">Vrouw</StUF:extraElement>
                <StUF:extraElement naam="opgemaakteNaam" xsi:nil="true" StUF:noValue="nietGeautoriseerd"/>
              </BG:extraElementen>
            </BG:PRS>
          </BG:PRSPRSHUW>
          <BG:PRSPRSHUW soortEntiteit="R" StUF:sleutelVerzendend="10" StUF:sleutelGegevensbeheer="10">
            <BG:datumSluiting>20000101</BG:datumSluiting>
            <BG:plaatsSluiting>363</BG:plaatsSluiting>
            <BG:landSluiting>6030</BG:landSluiting>
            <BG:datumOntbinding xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:redenOntbinding>S</BG:redenOntbinding>
            <BG:extraElementen>
              <StUF:extraElement naam="aanduidingGegevensInOnderzoek" xsi:nil="true" StUF:noValue="nietGeautoriseerd"/>
              <StUF:extraElement naam="landnaamOntbinding" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="landnaamSluiting">Nederland</StUF:extraElement>
              <StUF:extraElement naam="plaatsnaamOntbindingOmschrijving" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="plaatsnaamSluitingOmschrijving">Amsterdam</StUF:extraElement>
              <StUF:extraElement naam="redenOntbindingOmschrijving" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="soortVerbintenisOmschrijving">Huwelijk</StUF:extraElement>
            </BG:extraElementen>
            <BG:PRS soortEntiteit="F" StUF:sleutelVerzendend="10" StUF:sleutelGegevensbeheer="10">
              <BG:bsn-nummer>234567890</BG:bsn-nummer>
              <BG:voornamen>Wilhelmina</BG:voornamen>
              <BG:voorletters>W</BG:voorletters>
              <BG:voorvoegselGeslachtsnaam>van</BG:voorvoegselGeslachtsnaam>
              <BG:geslachtsnaam>Bakker</BG:geslachtsnaam>
              <BG:geboortedatum>19700101</BG:geboortedatum>
              <BG:geslachtsaanduiding>V</BG:geslachtsaanduiding>
              <BG:datumOverlijden xsi:nil="true" StUF:noValue="geenWaarde"/>
              <BG:aanduidingNaamgebruik xsi:nil="true" StUF:noValue="nietGeautoriseerd"/>
              <BG:extraElementen>
                <StUF:extraElement naam="geboortelandnaam">Nederland</StUF:extraElement>
                <StUF:extraElement naam="geboorteplaatsnaam">Neer</StUF:extraElement>
                <StUF:extraElement naam="omschrijvingAdellijkeTitel">Jonkvrouw</StUF:extraElement>
                <StUF:extraElement naam="omschrijvingGeslachtsaanduiding">Vrouw</StUF:extraElement>
                <StUF:extraElement naam="opgemaakteNaam" xsi:nil="true" StUF:noValue="nietGeautoriseerd"/>
              </BG:extraElementen>
            </BG:PRS>
          </BG:PRSPRSHUW>
          <BG:PRSPRSHUW soortEntiteit="R" StUF:sleutelVerzendend="10" StUF:sleutelGegevensbeheer="10">
            <BG:datumSluiting xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:plaatsSluiting xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:landSluiting xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:datumOntbinding xsi:nil="true" StUF:noValue="geenWaarde"/>
            <BG:redenOntbinding>O</BG:redenOntbinding>
            <BG:extraElementen>
              <StUF:extraElement naam="aanduidingGegevensInOnderzoek" xsi:nil="true" StUF:noValue="nietGeautoriseerd"/>
              <StUF:extraElement naam="landnaamOntbinding" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="landnaamSluiting">Nederland</StUF:extraElement>
              <StUF:extraElement naam="plaatsnaamOntbindingOmschrijving" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="plaatsnaamSluitingOmschrijving" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="redenOntbindingOmschrijving" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
              <StUF:extraElement naam="soortVerbintenisOmschrijving">Huwelijk</StUF:extraElement>
            </BG:extraElementen>
            <BG:PRS soortEntiteit="F" StUF:sleutelVerzendend="10" StUF:sleutelGegevensbeheer="10">
              <BG:bsn-nummer xsi:nil="true" StUF:noValue="geenWaarde"/>
              <BG:voornamen>Iemand</BG:voornamen>
              <BG:voorletters>I</BG:voorletters>
              <BG:voorvoegselGeslachtsnaam xsi:nil="true" StUF:noValue="geenWaarde"/>
              <BG:geslachtsnaam>Achternaam</BG:geslachtsnaam>
              <BG:geboortedatum xsi:nil="true" StUF:noValue="geenWaarde"/>
              <BG:geslachtsaanduiding xsi:nil="true" StUF:noValue="geenWaarde"/>
              <BG:datumOverlijden xsi:nil="true" StUF:noValue="geenWaarde"/>
              <BG:aanduidingNaamgebruik xsi:nil="true" StUF:noValue="nietGeautoriseerd"/>
              <BG:extraElementen>
                <StUF:extraElement naam="geboortelandnaam" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
                <StUF:extraElement naam="geboorteplaatsnaam" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
                <StUF:extraElement naam="omschrijvingAdellijkeTitel" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
                <StUF:extraElement naam="omschrijvingGeslachtsaanduiding" xsi:nil="true" StUF:noValue="waardeOnbekend"/>
                <StUF:extraElement naam="opgemaakteNaam" xsi:nil="true" StUF:noValue="nietGeautoriseerd"/>
              </BG:extraElementen>
            </BG:PRS>
          </BG:PRSPRSHUW>
          </BG:PRS>
        """

        tree = BeautifulSoup(response_xml, features="lxml-xml")
        verbintenissen = extract_verbintenis_data(tree)
        self.maxDiff = None
        self.assertEqual(
            verbintenissen,
            {
                "verbintenis": {
                    "persoon": {
                        "bsn": "234567890",
                        "voornamen": "Wilhelmina",
                        "voorvoegselGeslachtsnaam": "van",
                        "geslachtsnaam": "Bakker",
                        "geslachtsaanduiding": "V",
                        "geboortedatum": to_date("19700101"),
                        "geregistreerdeGeboortedatum": '1 January 1970',
                        "overlijdensdatum": None,
                        "adellijkeTitelPredikaat": None,
                        "omschrijvingAdellijkeTitel": "Jonkvrouw",
                        "geboortelandnaam": "Nederland",
                        "geboorteplaatsnaam": "Neer",
                        "omschrijvingGeslachtsaanduiding": "Vrouw",
                        "opgemaakteNaam": None,
                    },
                    "datumSluiting": to_date("20000101"),
                    "datumOntbinding": None,
                    "soortVerbintenis": None,
                    "soortVerbintenisOmschrijving": "Huwelijk",
                    "landnaamSluiting": "Nederland",
                    "plaatsnaamSluitingOmschrijving": "Amsterdam",
                    "redenOntbindingOmschrijving": None,
                },
                "verbintenisHistorisch": [
                    {
                        "persoon": {
                            "bsn": "234567890",
                            "voornamen": "Wilhelmina",
                            "voorvoegselGeslachtsnaam": "van",
                            "geslachtsnaam": "Bakker",
                            "geslachtsaanduiding": "V",
                            "geboortedatum": to_date("19700101"),
                            "geregistreerdeGeboortedatum": '1 January 1970',
                            "overlijdensdatum": None,
                            "adellijkeTitelPredikaat": None,
                            "omschrijvingAdellijkeTitel": "Jonkvrouw",
                            "geboortelandnaam": "Nederland",
                            "geboorteplaatsnaam": "Neer",
                            "omschrijvingGeslachtsaanduiding": "Vrouw",
                            "opgemaakteNaam": None,
                        },
                        "datumSluiting": to_date("20000101"),
                        "datumOntbinding": None,
                        "soortVerbintenis": None,
                        "soortVerbintenisOmschrijving": "Huwelijk",
                        "landnaamSluiting": "Nederland",
                        "plaatsnaamSluitingOmschrijving": "Amsterdam",
                        "redenOntbindingOmschrijving": "Echtscheiding",
                    },
                    {
                        "persoon": {
                            "bsn": None,
                            "voornamen": "Iemand",
                            "voorvoegselGeslachtsnaam": None,
                            "geslachtsnaam": "Achternaam",
                            "geslachtsaanduiding": None,
                            "geboortedatum": None,
                            "geregistreerdeGeboortedatum": None,
                            "overlijdensdatum": None,
                            "adellijkeTitelPredikaat": None,
                            "omschrijvingAdellijkeTitel": None,
                            "geboortelandnaam": None,
                            "geboorteplaatsnaam": None,
                            "omschrijvingGeslachtsaanduiding": None,
                            "opgemaakteNaam": None,
                        },
                        "datumSluiting": None,
                        "datumOntbinding": None,
                        "soortVerbintenis": None,
                        "soortVerbintenisOmschrijving": "Huwelijk",
                        "landnaamSluiting": "Nederland",
                        "plaatsnaamSluitingOmschrijving": None,
                        "redenOntbindingOmschrijving": "Overlijden",
                    },
                ],
            },
        )

    def test_vertrokken_onbekend_waarheen(self):
        """Test if the person has status vertrokken onbekend waarheen."""

        with open(VOW_RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        result = extract_data(tree)

        self.assertEqual(result["persoon"]["vertrokkenOnbekendWaarheen"], True)

    def test_vertrokken_onbekend_waarheen_not_from_amsterdam(self):
        """Test if the person has status vertrokken onbekend waarheen."""

        with open(VOW_NOT_FROM_AMSTERDAM_RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        result = extract_data(tree)

        self.assertEqual(result["persoon"]["vertrokkenOnbekendWaarheen"], False)

    def test_extraction_no_kids_parents_id_partners(self):
        """Test if the person has status vertrokken onbekend waarheen."""

        with open(RESPONSE_NO_KIDS_PARENTS_ID_PARTNERS_ADR) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        result = extract_data(tree)

        self.assertEqual(result["kinderen"], [])
        self.assertEqual(result["ouders"], [])
        self.assertEqual(result["verbintenis"], {})
        self.assertEqual(result["verbintenisHistorisch"], [])
        self.assertEqual(result["identiteitsbewijzen"], [])
        self.assertEqual(result["adres"], {})
        self.assertEqual(result["adresHistorisch"], [])
        self.assertEqual(result["persoon"]["nationaliteiten"], [])

        self.assertFalse(result["persoon"]["vertrokkenOnbekendWaarheen"])

    def test_adres_in_onderzoek(self):
        """Test if the person has status adres in onderzoek."""

        with open(RESPONSE_ADRES_ONDERZOEK) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        result = extract_data(tree)
        self.assertEqual(result["persoon"]["adresInOnderzoek"], "080000")

        # Wrong value for Aanduidingonderzoekadres
        tree.Body.find("PRSADRINS").find("StUF:extraElement").string = "N"
        tree.Body.find("StUF:extraElement").string = "090000"

        result = extract_data(tree)
        self.assertEqual(result["persoon"]["adresInOnderzoek"], None)

        # Punt adres value for Aanduidingonderzoekadres
        tree.Body.find("StUF:extraElement").string = "089999"
        result = extract_data(tree)
        self.assertEqual(result["persoon"]["adresInOnderzoek"], "089999")

        # No value for Aanduidingonderzoekadres, value is provided by ADR.extraElement.aanduidingGegevensInOnderzoek
        tree.Body.find("StUF:extraElement").string = ""
        tree.Body.find("PRSADRINS").find("StUF:extraElement").string = "J"
        result = extract_data(tree)
        self.assertEqual(result["persoon"]["adresInOnderzoek"], "080000")

    def test_emigration(self):
        """Test the address with a adres outside of NL."""
        with open(EMIGRATION_RESPONSE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        result = extract_data(tree)

        self.assertEqual(result["adres"]["landnaam"], "Groot-Brittannië")

        self.assertEqual(result["persoon"]["vertrokkenOnbekendWaarheen"], False)

        self.assertEqual(result["adresHistorisch"][0]["straatnaam"], "Amstel")

    def test_opgemaakte_naam_ontbinding(self):
        """Test the opgemaakte naam with multiple past verbindingen."""
        with open(ONTBINDING_RESPOSNE_PATH) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        result = extract_data(tree)

        self.assertEqual(result["persoon"]["opgemaakteNaam"], "J. van goed")

    def test_set_opgemaakte_naam(self):
        """Test set_opgemaakte_naam()"""

        def get_persoon():
            return {
                "opgemaakteNaam": None,
                "voornamen": "Voornaam Voornaam2",
                "geslachtsnaam": "eigengeslachtsnaam",
                "aanduidingNaamgebruik": "E",
                "voorvoegselGeslachtsnaam": "ter",
            }

        verbintenissen = []
        persoon = get_persoon()
        persoon["voorvoegselGeslachtsnaam"] = ""
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(persoon["opgemaakteNaam"], "V.V. eigengeslachtsnaam")

        persoon = get_persoon()
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(persoon["opgemaakteNaam"], "V.V. ter eigengeslachtsnaam")

        verbintenissen = [
            {
                "geslachtsnaam": "partnergeslachtsnaam",
                "voorvoegselGeslachtsnaam": "van",
            },
            {
                "geslachtsnaam": "foute partnergeslachtsnaam",
                "voorvoegselGeslachtsnaam": "van",
            },
        ]

        persoon = get_persoon()
        persoon["aanduidingNaamgebruik"] = "N"
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(
            persoon["opgemaakteNaam"],
            "V.V. ter eigengeslachtsnaam - van partnergeslachtsnaam",
        )

        persoon = get_persoon()
        persoon["aanduidingNaamgebruik"] = "V"
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(
            persoon["opgemaakteNaam"],
            "V.V. van partnergeslachtsnaam - ter eigengeslachtsnaam",
        )

        persoon = get_persoon()
        persoon["aanduidingNaamgebruik"] = "P"
        set_opgemaakte_naam(persoon, verbintenissen)
        self.assertEqual(persoon["opgemaakteNaam"], "V.V. van partnergeslachtsnaam")

    def test_idb_allow_list(self):
        with open(RESPONSE_IDB) as fp:
            tree = BeautifulSoup(fp.read(), features="lxml-xml")

        result = extract_data(tree)

        # one extra (5), because type 2 becomes type 10
        self.assertEqual(len(result["identiteitsbewijzen"]), 5)

        doc_types = [d["documentType"] for d in result["identiteitsbewijzen"]]
        expected = [
            "paspoort",
            "nederlandse identiteitskaart",
            "nederlandse identiteitskaart",
            "vluchtelingenpaspoort",
            "vreemdelingenpaspoort",
        ]
        self.assertEqual(doc_types, expected)
