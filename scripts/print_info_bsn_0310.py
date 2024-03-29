#!/usr/bin/env python3

import json
from sys import argv

import app.service.mks_client_hr as mks_client

# Change me to get the datas
bsn = argv[1]

if not bsn:
    exit("BSN not provided")

data = mks_client.get_from_bsn(bsn)
print(json.dumps(data, indent=2, default=str))
