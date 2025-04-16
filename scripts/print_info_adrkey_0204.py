#!/usr/bin/env python3

import json
from sys import argv

import app.service.adr_mks_client_02_04 as mks_client

adres_sleutel = argv[1]

if not adres_sleutel:
    exit("Adres sleutel not provided")

data = mks_client.get_resident_count(adres_sleutel)
print(json.dumps(data, indent=2, default=str))
