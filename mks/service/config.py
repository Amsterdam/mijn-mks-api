from logging import config

import os

from jwcrypto import jwk

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_DIR, '..', 'model', 'static')

REQUEST_TIMEOUT = 12

BRP_APPLICATIE = os.getenv('BRP_APPLICATIE')
BRP_GEBRUIKER = os.getenv('BRP_GEBRUIKER')
MKS_CLIENT_CERT = os.getenv('MKS_CLIENT_CERT')
MKS_CLIENT_KEY = os.getenv('MKS_CLIENT_KEY')
MKS_ENDPOINT = os.getenv('MKS_BRP_ENDPOINT')
TMA_CERTIFICATE = os.getenv('TMA_CERTIFICATE')

SENTRY_DSN = os.getenv('SENTRY_DSN', None)

assert (TMA_CERTIFICATE is not None)
assert (BRP_APPLICATIE is not None)
assert (BRP_GEBRUIKER is not None)
assert (MKS_ENDPOINT is not None)

DEBUG = os.getenv("DEBUG", 'False') == 'True'


def get_jwt_key():
    # key = jwk.JWK.generate(kty='oct', size=256)
    return jwk.JWK.from_json(os.getenv("MKS_JWT_KEY"))


def debug_logging():
    config.dictConfig({
        'version': 1,
        'formatters': {
            'verbose': {
                'format': '%(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'zeep.transports': {
                'level': 'DEBUG',
                'propagate': True,
                'handlers': ['console'],
            },
        }
    })


if DEBUG:
    debug_logging()
