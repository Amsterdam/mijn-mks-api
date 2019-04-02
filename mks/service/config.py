from logging import config

import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

BRP_APPLICATIE = os.getenv('BRP_APPLICATIE')
BRP_GEBRUIKER = os.getenv('BRP_GEBRUIKER')
MKS_CLIENT_CERT = os.getenv('MKS_CLIENT_CERT')
MKS_CLIENT_KEY = os.getenv('MKS_CLIENT_KEY')
MKS_ENDPOINT = os.getenv('MKS_BRP_ENDPOINT')
TMA_CERTIFICATE = os.getenv('TMA_CERTIFICATE')

assert (TMA_CERTIFICATE is not None)
assert (BRP_APPLICATIE is not None)
assert (BRP_GEBRUIKER is not None)
assert (MKS_ENDPOINT is not None)

DEBUG = os.getenv("DEBUG", 'False') == 'True'


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
