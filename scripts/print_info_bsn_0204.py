#!/usr/bin/env python3

import json
from sys import argv

import mks.service.mks_client_02_04 as mks_client

# Turn on dumping of raw soap xml
mks_client.log_response = True

bsn = argv[1]

if not bsn:
    exit("BSN not provided")

data = mks_client.get_0204(bsn)
print(json.dumps(data, indent=2, default=str))
