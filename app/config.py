import logging
import os
from datetime import date, time

from flask.json.provider import DefaultJSONProvider
from jwcrypto import jwk

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_DIR, "model", "static")
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
SERVICES_DIR = os.path.join(BASE_PATH, "service")

# Sentry configuration.
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENV = os.getenv("SENTRY_ENVIRONMENT")

# Environment determination
IS_PRODUCTION = SENTRY_ENV == "production"
IS_ACCEPTANCE = SENTRY_ENV == "acceptance"
IS_DEV = SENTRY_ENV == "development"
IS_TEST = SENTRY_ENV == "test"

IS_TAP = IS_PRODUCTION or IS_ACCEPTANCE or IS_TEST
IS_AP = IS_ACCEPTANCE or IS_PRODUCTION
IS_OT = IS_DEV or IS_TEST

# App constants
ENABLE_OPENAPI_VALIDATION = os.getenv("ENABLE_OPENAPI_VALIDATION", not IS_TAP)
REQUEST_TIMEOUT = 20 if IS_PRODUCTION else 30  # seconds

BRP_APPLICATIE = os.getenv("BRP_APPLICATIE")
BRP_GEBRUIKER = os.getenv("BRP_GEBRUIKER")
MKS_CLIENT_CERT = os.getenv("MIJN_DATA_CLIENT_CERT")
MKS_CLIENT_KEY = os.getenv("MIJN_DATA_CLIENT_KEY")
MKS_ENDPOINT = os.getenv("MKS_BRP_ENDPOINT")

SENTRY_DSN = os.getenv("SENTRY_DSN", None)

# Set-up logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()

logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d in function %(funcName)s] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=LOG_LEVEL,
)


class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.isoformat(timespec="minutes")

        if isinstance(obj, date):
            return obj.isoformat()

        return super().default(obj)


def get_jwt_key():
    key = os.getenv("MKS_JWT_KEY")
    jwk_json = '{"k":"%s","kty":"oct", "kid":"test"}' % (key,)
    return jwk.JWK.from_json(jwk_json)
