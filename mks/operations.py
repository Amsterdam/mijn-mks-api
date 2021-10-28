import logging

# helpers #
import connexion
from flask import request, make_response
from tma_saml import SamlVerificationException, UserType
from urllib3.exceptions import ConnectTimeoutError

from mks.model.stuf_utils import decrypt, is_nil
from mks.prometheus_definitions import mks_connection_state
from mks.service import adr_mks_client_02_04, mks_client_02_04
from mks.service.config import NNPID_EXTENSION1_ENABLED, get_raw_key
from mks.service.exceptions import (
    ExtractionError,
    InvalidBSNException,
    NoResultException,
    ServiceException,
    onbekende_fout,
)
from mks.service.mks_client_hr import (
    _get_response_by_bsn,
    _get_response_by_kvk_number,
    get_from_bsn,
    get_from_kvk,
    get_nnp_from_kvk,
)
from mks.service.saml import get_bsn_from_request, get_kvk_number_from_request, get_type


def log_and_generate_response(exception, response_type="json"):
    logging.error(f"exception type {type(exception)}")
    logging.exception(exception)
    e_type = type(exception)
    if e_type == ServiceException and response_type == "json":
        return exception.to_dict(), 500
    elif e_type == ServiceException and response_type == "text":
        return str(exception), 500
    elif e_type == SamlVerificationException:
        return "Access denied", 403
    elif e_type == NoResultException:
        return "No results", 400
    elif e_type == InvalidBSNException:
        return "Ongeldig BSN", 400
    elif e_type == ConnectTimeoutError:
        mks_connection_state.set(1)
        logging.error("MKS Timeout")
        return "Source connection timeout", 500
    elif e_type == ExtractionError:
        return "Extraction error", 500
    else:
        return onbekende_fout().to_dict(), 500


def get_bsn_from_saml_token() -> str:
    """
    Check if the BSN retrieved from the token is actually valid and parse it
    to int format for further use
    :return: The bsn in str form or an error in case it's not 11proef safe.
    """
    return get_bsn_from_request(connexion.request)


# operations #
def get_brp():
    try:
        usertype = get_type(request)
        if usertype != UserType.BURGER:
            return {
                "status": "error",
                "message": "Only requests via BSN is supported",
            }, 400
        log_request(request)
        response = mks_client_02_04.get_0204(get_bsn_from_saml_token())
        return response
    except Exception as e:
        return log_and_generate_response(e)


def get_brp_raw():
    cookie_value = request.cookies.get("access_token")
    if cookie_value is not None and cookie_value == get_raw_key():
        log_request(request)
        response = mks_client_02_04.get_0204_raw(get_bsn_from_saml_token(), True)
        return response

    return "no access without access token", 401


def get_status_health():
    try:
        log_request(request)
        return "OK"
    except Exception as e:
        return log_and_generate_response(e)


def get_bsn():
    try:
        log_request(request)
        return {"burgerservicenummer": get_bsn_from_saml_token()}
    except Exception as e:
        return log_and_generate_response(e)


def get_hr_raw():
    cookie_value = request.cookies.get("access_token")
    if cookie_value is None or cookie_value != get_raw_key():
        return "no access without access token", 401

    usertype = get_type(request)
    if usertype == UserType.BEDRIJF:
        kvk = get_kvk_number_from_request(request)
        return _get_response_by_kvk_number(kvk_number=kvk)

    if usertype == UserType.BURGER:
        bsn = get_bsn_from_saml_token()
        return _get_response_by_bsn(bsn=bsn)


def get_kvk_number():
    try:
        log_request(request)
        return {"kvknummer": get_kvk_number_from_request(request)}
    except Exception as e:
        return log_and_generate_response(e)


def get_hr_for_bsn():
    try:
        log_request(request)
        return get_from_bsn(get_bsn_from_saml_token())
    except Exception as e:
        return log_and_generate_response(e)


def get_hr_for_kvk():
    try:
        log_request(request)
        kvk_number = get_kvk_number_from_request(request)
        hr_kvk = get_from_kvk(kvk_number)

        if (
            (not NNPID_EXTENSION1_ENABLED)
            or ("nnpid" not in hr_kvk)
            or is_nil(hr_kvk["nnpid"])
        ):
            return hr_kvk

        hr_kvk_nnp = get_nnp_from_kvk(hr_kvk["nnpid"])

        return {**hr_kvk, **hr_kvk_nnp}
    except Exception as e:
        return log_and_generate_response(e)


def get_hr():
    usertype = get_type(request)
    data = None

    if usertype == UserType.BEDRIJF:
        data = get_hr_for_kvk()

    if usertype == UserType.BURGER:
        data = get_hr_for_bsn()

    if not data:
        return {}, 204

    return {"content": data, "status": "OK"}


def get_resident_count():
    request_json = request.get_json()

    if request_json:
        address_key = request_json.get("addressKey")

        if address_key:
            try:
                address_key_decrypted = decrypt(address_key)
            except Exception:
                return "Invalid encrypted value", 400

            response = adr_mks_client_02_04.get(address_key_decrypted)

            if not response:
                return None, 204

            return response

    return "adressleutel required", 400


def log_request(req):
    logging.info(req.url)
