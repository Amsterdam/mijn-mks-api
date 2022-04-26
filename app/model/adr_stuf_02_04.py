from datetime import date
import logging

from bs4 import Tag

from app.model.stuf_utils import to_date, is_nil


def extract_data(adr_tree: Tag):
    resident_count = 0

    residents_data = adr_tree.find_all("ADRPRSVBL", recursive=False)

    now = date.today()

    if is_nil(residents_data):
        logging.error("No data for address")
        return None

    for res in residents_data:
        tijdvak = res.find("tijdvakRelatie", recursive=False)
        endDate = to_date(tijdvak.find("einddatumRelatie", recursive=False))

        if endDate and endDate > now:
            continue

        resident_count += 1

    return {
        "residentCount": resident_count,
    }
