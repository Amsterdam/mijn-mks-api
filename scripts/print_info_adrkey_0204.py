#!/usr/bin/env python3

import json
from sys import argv

import app.service.adr_mks_client_02_04 as mks_client
from app.helpers import decrypt  # noqa: F401


adres_sleutel = argv[1]
# adres_sleutel = decrypt("")

if not adres_sleutel:
    exit("Adres sleutel not provided")

data = mks_client.get(adres_sleutel)
print(json.dumps(data, indent=2, default=str))
