import os
from datetime import date
from unittest import TestCase
from unittest.mock import patch

from app.service import mks_client_hr

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_kvk_mac_response.xml")

# Response for alle andere rechtsvormen (geen eenmanszaak) (EHerkenning+kvk)
KVK_HR_MAC_RESPONSE = {
    "mokum": True,
    "nnpid": "123456789",
    "onderneming": {
        "datumAanvang": None,
        "datumEinde": None,
        "handelsnamen": [
            "Primaire Handelsnaam",
            "Handelsnaam 2e locatie",
            "Handelsnaam v.o.f.",
        ],
        "hoofdactiviteit": "Fastfoodrestaurants, cafetaria's, ijssalons, eetkramen e.d.",
        "overigeActiviteiten": [],
        "rechtsvorm": "VennootschapOnderFirma",
    },
    "eigenaar": None,
    "rechtspersonen": [
        {
            "kvkNummer": "1234567",
            "rsin": "123456789",
            "statutaireNaam": "Naam v.o.f.",
            "statutaireZetel": None,
        }
    ],
    "vestigingen": [
        {
            "activiteiten": [
                "Fastfoodrestaurants, cafetaria's, " "ijssalons, eetkramen e.d."
            ],
            "bezoekadres": {
                "huisletter": "A",
                "huisnummer": "1",
                "huisnummertoevoeging": None,
                "postcode": "1012 PN",
                "straatnaam": "Amstel",
                "woonplaatsNaam": "Amsterdam",
            },
            "datumAanvang": date(2000, 2, 1),
            "datumEinde": None,
            "emailadres": "email@example.com",
            "faxnummer": None,
            "handelsnamen": ["Primaire Handelsnaam"],
            "postadres": {
                "huisletter": None,
                "huisnummer": "2",
                "huisnummertoevoeging": None,
                "postcode": "1012 PN",
                "straatnaam": "Amstel",
                "woonplaatsNaam": "Amsterdam",
            },
            "telefoonnummer": "+310200000000",
            "typeringVestiging": "Hoofdvestiging",
            "vestigingsNummer": "000000000001",
            "websites": ["www.example.com"],
        },
        {
            "activiteiten": [
                "Fastfoodrestaurants, cafetaria's, ijssalons, eetkramen e.d."
            ],
            "bezoekadres": {
                "huisletter": None,
                "huisnummer": "2",
                "huisnummertoevoeging": None,
                "postcode": "1012 PN",
                "straatnaam": "Amstel",
                "woonplaatsNaam": "Amsterdam",
            },
            "datumAanvang": date(2015, 1, 1),
            "datumEinde": None,
            "emailadres": "mail@example.com",
            "faxnummer": None,
            "handelsnamen": ["Handelsnaam 2e locatie"],
            "postadres": {
                "huisletter": None,
                "huisnummer": "1",
                "huisnummertoevoeging": None,
                "postcode": "1012 PN",
                "straatnaam": "Amstel",
                "woonplaatsNaam": "Amsterdam",
            },
            "telefoonnummer": "+310000000000",
            "typeringVestiging": "Nevenvestiging",
            "vestigingsNummer": "000000000002",
            "websites": ["www.example.com"],
        },
        {
            "activiteiten": [
                "Fastfoodrestaurants, cafetaria's, ijssalons, eetkramen e.d."
            ],
            "bezoekadres": {
                "huisletter": None,
                "huisnummer": "1",
                "huisnummertoevoeging": None,
                "postcode": "1011 PN",
                "straatnaam": "Amstel",
                "woonplaatsNaam": "Amsterdam",
            },
            "datumAanvang": date(2002, 1, 1),
            "datumEinde": None,
            "emailadres": "mail@example.com",
            "faxnummer": None,
            "handelsnamen": ["Handelsnaam v.o.f."],
            "postadres": {
                "huisletter": "B",
                "huisnummer": "1",
                "huisnummertoevoeging": None,
                "postcode": "1012 PN",
                "straatnaam": "Amstel",
                "woonplaatsNaam": "Amsterdam",
            },
            "telefoonnummer": "+310200000000",
            "typeringVestiging": "Nevenvestiging",
            "vestigingsNummer": "000000000003",
            "websites": ["www.example.com"],
        },
    ],
}


def get_kvk_mac_xml_response_fixture(*args):
    with open(RESPONSE_PATH, "rb") as response_file:
        return response_file.read()


class KvkHrTest(TestCase):
    @patch("app.service.mks_client_hr._get_response", get_kvk_mac_xml_response_fixture)
    def test_get(self):
        result = mks_client_hr.get_from_kvk("123456789")

        self.assertEqual(result, KVK_HR_MAC_RESPONSE)
