#!/usr/bin/env python3

import json

import mks.service.mks_client as mks_client

# Turn on dumping of raw soap xml
mks_client.log_response = True

# Change me to get the datas
bsn = 123456789

data = mks_client.get_response(bsn)
print(json.dumps(data, indent=2, default=str))
