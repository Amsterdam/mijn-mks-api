import base64
import logging
import os
from datetime import date, time
import tempfile

from flask.json.provider import DefaultJSONProvider
from jwcrypto import jwk

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_DIR, "model", "static")
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
SERVICES_DIR = os.path.join(BASE_PATH, "service")

OTAP_ENV = os.getenv("MA_OTAP_ENV")

# Environment determination
IS_PRODUCTION = OTAP_ENV == "production"
IS_ACCEPTANCE = OTAP_ENV == "acceptance"
IS_DEV = OTAP_ENV == "development"
IS_TEST = OTAP_ENV == "test"

IS_TAP = IS_PRODUCTION or IS_ACCEPTANCE or IS_TEST
IS_AP = IS_ACCEPTANCE or IS_PRODUCTION
IS_OT = IS_DEV or IS_TEST
IS_AZ = os.getenv("IS_AZ", False)

IS_SHOW_BSN_ENABLED = (
    os.getenv("MKS_IS_SHOW_BSN_ENABLED", "false" if IS_PRODUCTION else "true") == "true"
)

# App constants
VERIFY_JWT_SIGNATURE = os.getenv("VERIFY_JWT_SIGNATURE", IS_AP)
REQUEST_TIMEOUT = 20 if IS_PRODUCTION else 30  # seconds

BRP_APPLICATIE = os.getenv("BRP_APPLICATIE")
BRP_GEBRUIKER = os.getenv("BRP_GEBRUIKER")

MIJN_DATA_CLIENT_CERT = os.getenv("MIJN_DATA_CLIENT_CERT")
MKS_CLIENT_CERT = os.getenv("MIJN_DATA_CLIENT_CERT", os.getenv("MKS_CLIENT_CERT"))
MKS_CLIENT_KEY = os.getenv("MIJN_DATA_CLIENT_KEY", os.getenv("MKS_CLIENT_KEY"))

# TODO: Add other AZ env conditions after migration.
if IS_AZ and IS_TAP and MIJN_DATA_CLIENT_CERT is not None:
    # https://stackoverflow.com/a/46570364/756075
    # Server security / certificates
    cert = tempfile.NamedTemporaryFile(delete=False)
    cert.write(base64.b64decode(MKS_CLIENT_CERT))
    cert.close()

    key = tempfile.NamedTemporaryFile(delete=False)
    key.write(base64.b64decode(MKS_CLIENT_KEY))
    key.close()

    MKS_CLIENT_CERT = cert.name
    MKS_CLIENT_KEY = key.name

MKS_ENDPOINT = os.getenv("MKS_BRP_ENDPOINT")

# Set-up logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

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


def get_application_insights_connection_string():
    return os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
