import logging

import connexion
import sentry_sdk
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
    '/brp/aantal_bewoners': operations.get_resident_count,
}

# using a custom resolver to determine operations
# instead of the operationId in the yaml file.
webapp.add_api('swagger.yaml',
               resolver=operation_resolver.CustomOperationResolver(mapping),
               validate_responses=False)

# set the WSGI application callable to allow using uWSGI:
application = webapp.app

if __name__ == "__main__":
    webapp.run(port=9853)
