import logging

import sentry_sdk
from flask import Flask, request
from requests import HTTPError
from sentry_sdk.integrations.flask import FlaskIntegration

from app import auth
from app.config import IS_DEV, SENTRY_DSN, CustomJSONEncoder
from app.helpers import (
    decrypt,
    error_response_json,
    success_response_json,
    validate_openapi,
)
from app.service import mks_client_02_04, mks_client_hr
from app.service.adr_mks_client_02_04 import get_resident_count

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[FlaskIntegration()], with_locals=False
    )


@app.route("/brp/brp", methods=["GET"])
@auth.login_required
@validate_openapi
def get_brp():
    user = auth.get_current_user()
    brp = mks_client_02_04.get_0204(user["id"])
    return success_response_json(brp)


@app.route("/brp/hr", methods=["GET"])
@auth.login_required
@validate_openapi
def get_hr():
    user = auth.get_current_user()

    if user["type"] == auth.PROFILE_TYPE_PRIVATE:
        hr = mks_client_hr.get_from_bsn(user["id"])
    else:
        hr = mks_client_hr.get_hr_for_kvk(user["id"])

    return success_response_json(hr)


@app.route("/brp/aantal_bewoners", methods=["POST"])
@auth.login_required
@validate_openapi
def get_aantal_bewonders():
    request_json = request.get_json()

    if request_json:
        try:
            address_key = request_json.get("addressKey")
            if address_key:
                aantal_bewoners = get_resident_count(decrypt(address_key))
                return success_response_json(aantal_bewoners)
        except Exception as error:
            logging.error(error)
            pass

    return error_response_json("bad request", 400)


@app.route("/status/health")
def health_check():
    return success_response_json("OK")


@app.errorhandler(Exception)
def handle_error(error):

    error_message_original = f"{type(error)}:{str(error)}"

    msg_auth_exception = "Auth error occurred"
    msg_request_http_error = "Request error occurred"
    msg_server_error = "Server error occurred"

    logging.exception(error, extra={"error_message_original": error_message_original})

    if IS_DEV:  # pragma: no cover
        msg_auth_exception = error_message_original
        msg_request_http_error = error_message_original
        msg_server_error = error_message_original

    if isinstance(error, HTTPError):
        return error_response_json(
            msg_request_http_error,
            error.response.status_code,
        )
    elif auth.is_auth_exception(error):
        return error_response_json(msg_auth_exception, 401)

    return error_response_json(msg_server_error, 500)


if __name__ == "__main__":  # pragma: no cover
    app.run()
