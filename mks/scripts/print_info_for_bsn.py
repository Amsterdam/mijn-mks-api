#!/usr/bin/env python3

import json

import mks.service.mks_client_02_04 as mks_client

# Turn on dumping of raw soap xml
mks_client.log_response = True

# Change me to get the datas
bsn = "123456789"

data = mks_client.get_0204(bsn)
print(json.dumps(data, indent=2, default=str))
