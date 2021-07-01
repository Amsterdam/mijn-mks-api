#!/usr/bin/env python3

import json
from sys import argv

import mks.service.mks_client_hr as mks_client

# Turn on dumping of raw soap xml
mks_client.log_response = True

kvk = argv[1]

if not kvk:
    exit("KVK not provided")

data = mks_client.get_from_kvk(kvk)
print(json.dumps(data, indent=2, default=str))
