import logging
from builtins import print
from math import ceil

import connexion
import sentry_sdk
from flask import request
from flask_limiter import Limiter
from sentry_sdk.integrations.flask import FlaskIntegration

from mks import operation_resolver
from mks import operations
from mks.service.config import SENTRY_DSN

logging.basicConfig(level=logging.INFO)
webapp = connexion.App(__name__, options={"swagger_ui": False})

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FlaskIntegration()],
        with_locals=True
    )

mapping = {
    '/status/health': operations.get_status_health,
    '/brp/bsn': operations.get_bsn,
    '/brp/brp': operations.get_brp,
}

# using a custom resolver to determine operations
# instead of the operationId in the yaml file.
webapp.add_api('swagger.yaml',
               resolver=operation_resolver.CustomOperationResolver(mapping),
               validate_responses=False)

# set the WSGI application callable to allow using uWSGI:
application = webapp.app


def global_limiter():
    return "global_limiter"


def limiter_exempt():
    if request.path == "/status/health":
        return True  # skip
    return False


# Flask limiter works per server, per process. this needs to match whats defined in uwsgi.ini
max_reqs_per_min = ceil((30 / 2) / 2)


limiter = Limiter(
    application,
    key_func=global_limiter,
    default_limits=[f"{max_reqs_per_min} per minute"],
    default_limits_exempt_when=limiter_exempt
)

if __name__ == "__main__":
    webapp.run(port=9853)
