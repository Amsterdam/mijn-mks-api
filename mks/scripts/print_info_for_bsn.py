#!/usr/bin/env python3
import mks.service.mks_client as mks_client

# Turn on dumping of raw soap xml
mks_client.log_response = True

bsn = 123456789
print( mks_client.get_response(bsn))