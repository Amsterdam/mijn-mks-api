import os
from datetime import date
from unittest import TestCase
from unittest.mock import patch

from app.service import mks_client_hr

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_kvk_prs_response.xml")
RESPONSE_EMPTY_PATH = os.path.join(FIXTURE_PATH, "hr_empty_response.xml")

# Response for eenmanszaak (Digid+BSN or Eherkenning+KVK)
KVK_HR_EENMANSZAAK_RESPONSE = {
    "mokum": True,
    "nnpid": None,
    "onderneming": {
        "kvkNummer": "012345678",
        "datumAanvang": date(1992, 1, 1),
        "datumEinde": date(2020, 1, 1),
        "handelsnamen": ["Primaire Handelsnaam", "Naam 2", "Naam 3", "Naam 4"],
        "hoofdactiviteit": "Overige administratiekantoren",
        "overigeActiviteiten": ["Arbeidsbemiddeling", "Organisatie-adviesbureaus"],
        "rechtsvorm": "Eenmanszaak",
    },
    "eigenaar": {
        "bsn": "999999999",
        "naam": "Voornaam van Achternaam",
        "geboortedatum": date(1970, 1, 1),
        "adres": {
            "huisletter": None,
            "huisnummer": "1",
            "huisnummertoevoeging": None,
            "postcode": "1012 NP",
            "straatnaam": "Amstel",
            "woonplaatsNaam": "Amsterdam",
        },
    },
    "rechtspersonen": [],
    "vestigingen": [
        {
            "activiteiten": [
                "Overige administratiekantoren",
                "Organisatie-adviesbureaus",
                "Arbeidsbemiddeling",
            ],
            "bezoekadres": {
                "huisletter": None,
                "huisnummer": "1",
                "huisnummertoevoeging": None,
                "postcode": "1012 PN",
                "straatnaam": "Amstel",
                "woonplaatsNaam": "Amsterdam",
            },
            "datumAanvang": date(1992, 1, 1),
            "datumEinde": date(2020, 1, 1),
            "emailadres": None,
            "faxnummer": None,
            "handelsnamen": ["Primaire Handelsnaam", "Naam 2", "Naam 3", "Naam 4"],
            "postadres": {
                "huisletter": None,
                "huisnummer": "1",
                "huisnummertoevoeging": None,
                "postcode": "1012 PN",
                "straatnaam": "Amstel",
                "woonplaatsNaam": "Amsterdam",
            },
            "telefoonnummer": None,
            "typeringVestiging": "Hoofdvestiging",
            "vestigingsNummer": "000000000001",
            "websites": [],
        }
    ],
}


def get_kvk_prs_xml_response_fixture(*args):
    with open(RESPONSE_PATH, "rb") as response_file:
        return response_file.read().decode("utf-8")


def get_xml_response_empty_fixture(*args):
    with open(RESPONSE_EMPTY_PATH, "rb") as response_file:
        return response_file.read().decode("utf-8")


class KvkHrTest(TestCase):
    @patch("app.service.mks_client_hr._get_response", get_kvk_prs_xml_response_fixture)
    def test_get(self):
        result = mks_client_hr.get_from_kvk("123456789")

        self.assertEqual(result, KVK_HR_EENMANSZAAK_RESPONSE)

    @patch("app.service.mks_client_hr._get_response", get_xml_response_empty_fixture)
    def test_get_empty(self):
        result = mks_client_hr.get_from_kvk("123456789")

        self.assertEqual(result, None)
