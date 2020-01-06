import csv
import os.path

from mks.service.config import STATIC_DIR

GBA_STATIC_DIR = os.path.join(STATIC_DIR, 'gba')

lookup_landen = {}
lookup_gemeenten = {}
lookup_geslacht = {
    'M': 'Man',
    'V': 'Vrouw',
}

# source: wsdl/bg0310_msg_vraagAntwoord.xsd
lookup_geheimhouding = {
    "0": "geen beperking",
    "1": "niet zonder toestemming aan derden ter uitvoering van een algemeen verbindend voorschrift",
    "2": "niet aan kerken",
    "3": "niet aan vrije derden",
    "4": "niet zonder toestemming aan derden ter uitvoering van een algemeen verbindend voorschrift en niet aan kerken",
    "5": "niet zonder toestemming aan derden ter uitvoering van een algemeen verbindend voorschrift en niet aan vrije derden",
    "6": "niet aan kerken en niet aan vrije derden",
    "7": "niet zonder toestemming aan derden ter uitvoering van een algemeen verbindend voorschrift en niet aan vrije derden en niet aan kerken",
}


# Source:
# https://publicaties.rvig.nl/Landelijke_tabellen/Landelijke_tabellen_32_t_m_60_excl_tabel_35/Landelijke_Tabellen_32_t_m_60_in_csv_formaat


def load_landen_lookup():
    with open(os.path.join(GBA_STATIC_DIR, 'Tabel34 Landentabel (gesorteerd op code).csv'), encoding='utf16') as fh:
        fh.readline()  # Skip first line
        reader = csv.reader(fh)
        for row in reader:
            lookup_landen[row[0]] = row[1]


def load_gemeenten_lookup():
    with open(os.path.join(GBA_STATIC_DIR, 'Tabel33 Gemeententabel (gesorteerd op code).csv'), encoding='utf16') as fh:
        fh.readline()  # Skip first line
        reader = csv.reader(fh)
        for row in reader:
            lookup_gemeenten[row[0]] = row[1]


load_landen_lookup()
load_gemeenten_lookup()
