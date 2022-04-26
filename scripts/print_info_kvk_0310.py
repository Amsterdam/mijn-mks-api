#!/usr/bin/env python3

import json
from sys import argv

import app.service.mks_client_hr as mks_client

kvk = argv[1]

if not kvk:
    exit("KVK not provided")

data = mks_client.get_from_kvk(kvk)
print(json.dumps(data, indent=2, default=str))
