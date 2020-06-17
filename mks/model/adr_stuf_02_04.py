import logging
from collections import defaultdict
from datetime import datetime
import re
from hashlib import sha256

from bs4 import Tag

from mks.model.gba import lookup_prsidb_soort_code, lookup_geslacht, lookup_gemeenten, lookup_landen


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


def extract_data(persoon_tree: Tag):
    return {
        'identiteitsbewijzen': identiteitsbewijzen,
    }


