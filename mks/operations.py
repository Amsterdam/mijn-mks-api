import logging

# helpers #
import connexion
from flask import request
from tma_saml import SamlVerificationException
from urllib3.exceptions import ConnectTimeoutError

from mks.model.stuf_utils import decrypt
from mks.service import mks_client_02_04, adr_mks_client_02_04
from mks.service.exceptions import NoResultException, InvalidBSNException, ExtractionError
from mks.service.exceptions import ServiceException, onbekende_fout
from mks.service.saml import get_bsn_from_request


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
    elif e_type == ConnectTimeoutError:
        logging.error("MKS Timeout")
        return 'Source connection timeout', 500
    elif e_type == ExtractionError:
        return 'Extraction error', 500
    elif e_type == UnicodeDecodeError:
        return 'Invalid encrypted value', 400
    else:
        return onbekende_fout().to_dict(), 500


def get_bsn_from_saml_token() -> str:
    """
    Check if the BSN retrieved from the token is actually valid and parse it
    to int format for further use
    :return: The bsn in int form or an error in case it's not 11proef safe.
    """
    return get_bsn_from_request(connexion.request)


# operations #
def get_brp():
    try:
        log_request(request)
        response = mks_client_02_04.get_0204(get_bsn_from_saml_token())
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


def get_resident_count():
    try:
        if request.data:
            adres_sleutel = decrypt(request.data)
            response = adr_mks_client_02_04.get(adres_sleutel)
            return response
        else:
            return "adressleutel required", 400
    except Exception as e:
        return log_and_generate_response(e)


def log_request(req):
    logging.info(req.url)
