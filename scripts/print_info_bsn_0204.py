#!/usr/bin/env python3

import json
from sys import argv

import app.service.mks_client_02_04 as mks_client

bsn = argv[1]

if not bsn:
    exit("BSN not provided")

data = mks_client.get_0204(bsn)
print(json.dumps(data, indent=2, default=str))
