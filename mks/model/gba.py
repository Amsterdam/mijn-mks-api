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
lookup_prsidb_soort_code = {
    1: "Paspoort",
    2: "Europese identiteitskaart",
    3: "Toeristenkaart",
    4: "Gemeentelijke identiteitskaart",
    5: "Verblijfsdocument van de Vreemdelingendienst",
    6: "Vluchtelingenpaspoort",
    7: "Vreemdelingenpaspoort",
    8: "Paspoort met aantekening vergunning tot verblijf",
    9: "(electronisch) W-document",
}  # https://www.gemmaonline.nl/images/gemmaonline/c/cb/GFO_Basisgegevens.pdf


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
