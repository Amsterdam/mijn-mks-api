from datetime import datetime

from bs4 import Tag

from mks.model.stuf_utils import to_datetime


def extract_data(adr_tree: Tag):
    resident_count = 0

    residents_data = adr_tree.find_all("ADRPRSVBL", recursive=False)

    now = datetime.now()

    if residents_data is None or residents_data.get("xsi:nil") == 'true':
        pass

    for res in residents_data:
        tijdvak = res.find('tijdvakRelatie', recursive=False)
        endDate = to_datetime(tijdvak.find('einddatumRelatie', recursive=False))

        if endDate and endDate > now:
            continue

        resident_count += 1

    return {
        'residentCount': resident_count,
    }
