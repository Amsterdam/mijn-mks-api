from datetime import datetime

from bs4 import Tag

from mks.model.stuf_utils import to_string, to_int, set_fields, to_date


def get_nationaliteiten(nationaliteiten: Tag):
    result = []

    fields = [
        {'name': 'omschrijving', 'parser': to_string},
        {'name': 'code', 'parser': to_int},
    ]

    for nat in nationaliteiten:
        nationaliteit = {}
        set_fields(nat, fields, nationaliteit)
        result.append(nationaliteit)

    # For people not living in Amsterdam we dont get the omschrijving.
    # Quick fix for Nederlandse if code == 1
    for n in result:
        if not n['omschrijving']:
            if n['code'] == 1:
                n['omschrijving'] = "Nederlandse"

    return result


def extract_data(adr_tree: Tag):
    resident_count = 0

    residents_data = adr_tree.find_all("ADRPRSVBL", recursive=False)

    now = datetime.now()
    for res in residents_data:
        tijdvak = res.find('tijdvakRelatie', recursive=False)
        endDate = to_date(tijdvak.find('einddatumRelatie', recursive=False))

        if endDate and endDate > now:
            continue

        resident_count += 1

    return {
        'residentCount': resident_count,
    }
