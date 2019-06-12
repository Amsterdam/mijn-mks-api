import logging

# helpers #
import connexion
from flask import request

from mks.service import mks_client
from mks.service import saml
from mks.service.config import TMA_CERTIFICATE
from mks.service.exceptions import NoResultException, InvalidBSNException
from mks.service.exceptions import ServiceException, onbekende_fout
from mks.service.saml import SamlVerificationException


def log_and_generate_response(exception, response_type='json'):
    logging.error(exception)
    e_type = type(exception)
    if e_type == ServiceException and response_type == 'json':
        return exception.to_dict(), 500
    elif e_type == ServiceException and response_type == 'text':
        return str(exception), 500
    elif e_type == SamlVerificationException:
        return 'Access denied', 403
    elif e_type == NoResultException:
        return 'No results', 400
    elif e_type == InvalidBSNException:
        return 'Ongeldig BSN', 400
    else:
        return onbekende_fout().to_dict(), 500


def get_bsn_from_saml_token() -> int:
    """
    Check if the BSN retrieved from the token is actually valid and parse it
    to int format for further use
    :return: The bsn in int form or an error in case it's not 11proef safe.
    """
    # return 307741837
    # return 230012346
    saml_token = connexion.request.headers.get('x-saml-attribute-token1')
    raw_bsn = saml.verify_saml_token_and_retrieve_saml_attribute(
        saml_token=saml_token,
        attribute='uid',
        saml_cert=TMA_CERTIFICATE)

    # BSN of 8 character misses a 0 prefix which is required for elfproef
    if len(raw_bsn) == 8:
        raw_bsn = '0' + raw_bsn

    # BSN Should be 9 characters long.
    if len(raw_bsn) == 9:
        bsn_sum = 0
        for index, nr in enumerate(reversed(raw_bsn)):
            if index == 0:
                multiplier = -1
            else:
                multiplier = index + 1
            bsn_sum += int(nr) * multiplier

        # Elfproef
        if bsn_sum % 11 == 0:
            return int(raw_bsn)

    raise InvalidBSNException()


# operations #
def get_brp():
    try:
        log_request(request)
        response = mks_client.get_response(get_bsn_from_saml_token())
        return response
    except Exception as e:
        return log_and_generate_response(e)


def get_status_health():
    try:
        log_request(request)
        return 'OK'
    except Exception as e:
        return log_and_generate_response(e)


def get_bsn():
    try:
        log_request(request)
        return {
            "burgerservicenummer": get_bsn_from_saml_token()
        }
    except Exception as e:
        return log_and_generate_response(e)


def log_request(req):
    logging.info(req.url)
