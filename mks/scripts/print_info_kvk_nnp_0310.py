#!/usr/bin/env python3

import json
from sys import argv

import mks.service.mks_client_hr as mks_client

# Turn on dumping of raw soap xml
mks_client.log_response = True

kvk = argv[1]

if not kvk:
    exit("KVK not provided")

printData = mks_client.get_from_kvk(kvk)

if not printData['nnpid']:
    print('!! NNPID not found, printing kvk data !!')
else:
    printData = mks_client.get_nnp_from_kvk(printData['nnpid'])

print(json.dumps(printData, indent=2, default=str))
