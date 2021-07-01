import logging

import connexion
import sentry_sdk
from prometheus_client import make_wsgi_app
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from mks import operation_resolver, operations
from mks.service.config import SENTRY_DSN, IS_PRODUCTION, IS_ACCEPTANCE

logging.basicConfig(level=logging.INFO)
webapp = connexion.App(__name__, options={"swagger_ui": False})

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FlaskIntegration()],
        with_locals=False
    )

mapping = {
    '/status/health': operations.get_status_health,
    '/brp/bsn': operations.get_bsn,
    '/brp/kvk': operations.get_kvk_number,
    '/brp/brp': operations.get_brp,
    '/brp/hr': operations.get_hr,
    '/brp/aantal_bewoners': operations.get_resident_count,
    '/brp/brp/raw': operations.get_brp_raw,
    '/brp/hr/raw': operations.get_hr_raw,
}

# using a custom resolver to determine operations
# instead of the operationId in the yaml file.
webapp.add_api('swagger.yaml',
               resolver=operation_resolver.CustomOperationResolver(mapping),
               validate_responses=not IS_PRODUCTION and not IS_ACCEPTANCE)


# set the WSGI application callable to allow using uWSGI:
application = webapp.app

application.wsgi_app = DispatcherMiddleware(application.wsgi_app, {
    '/metrics': make_wsgi_app()
})


if __name__ == "__main__":
    webapp.run(port=9853)
