#!/usr/bin/env python3

import json

import mks.service.adr_mks_client_02_04 as mks_client
from mks.model.stuf_utils import decrypt  # noqa: F401

# Turn on dumping of raw soap xml
mks_client.log_response = True

# Change me to get the datas
adres_sleutel = "123456789"
# adres_sleutel = decrypt("")

data = mks_client.get(adres_sleutel)
print(json.dumps(data, indent=2, default=str))
