import logging

import connexion

from mks import operation_resolver
from mks import operations

logging.basicConfig(level=logging.INFO)
webapp = connexion.App(__name__, swagger_url='todo')

mapping = {
    '/status/health': operations.get_status_health,
    '/brp/bsn': operations.get_bsn,
    '/brp/brp': operations.get_brp,
}

# using a custom resolver to determine operations
# instead of the operationId in the yaml file.
webapp.add_api('brp_swagger.json',
               resolver=operation_resolver.CustomOperationResolver(mapping),
               validate_responses=False)

# set the WSGI application callable to allow using uWSGI:
application = webapp.app

if __name__ == "__main__":
    webapp.run(port=9853)
