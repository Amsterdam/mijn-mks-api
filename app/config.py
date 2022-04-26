from datetime import date
from json import JSONEncoder
import logging
import os
import time

from jwcrypto import jwk

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_DIR, "..", "model", "static")
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# Sentry configuration.
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENV = os.getenv("SENTRY_ENVIRONMENT")

# Environment determination
IS_PRODUCTION = SENTRY_ENV == "production"
IS_ACCEPTANCE = SENTRY_ENV == "acceptance"
IS_AP = IS_PRODUCTION or IS_ACCEPTANCE
IS_DEV = os.getenv("FLASK_ENV") == "development" and not IS_AP

ENABLE_OPENAPI_VALIDATION = os.getenv("ENABLE_OPENAPI_VALIDATION", "1")

REQUEST_TIMEOUT = 20 if IS_PRODUCTION else 30  # seconds

BRP_APPLICATIE = os.getenv("BRP_APPLICATIE")
BRP_GEBRUIKER = os.getenv("BRP_GEBRUIKER")
MKS_CLIENT_CERT = os.getenv("MKS_CLIENT_CERT")
MKS_CLIENT_KEY = os.getenv("MKS_CLIENT_KEY")
MKS_ENDPOINT = os.getenv("MKS_BRP_ENDPOINT")

SENTRY_DSN = os.getenv("SENTRY_DSN", None)

# Set-up logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()

logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(pathname)s:%(lineno)d in function %(funcName)s] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=LOG_LEVEL,
)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.isoformat(timespec="minutes")
        if isinstance(obj, date):
            return obj.isoformat()

        return JSONEncoder.default(self, obj)


def get_jwt_key():
    key = os.getenv("MKS_JWT_KEY")
    return jwk.JWK.from_json('{"k":"%s","kty":"oct"}' % (key,))
