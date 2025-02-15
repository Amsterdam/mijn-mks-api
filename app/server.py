import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.trace import get_tracer_provider
from requests.exceptions import HTTPError

from app import auth
from app.config import (
    IS_DEV,
    IS_SHOW_BSN_ENABLED,
    UpdatedJSONProvider,
    get_application_insights_connection_string,
)
from app.helpers import decrypt, error_response_json, remove_attr, success_response_json
from app.service import mks_client_02_04, mks_client_hr
from app.service.adr_mks_client_02_04 import get_resident_count

# See also: https://medium.com/@tedisaacs/auto-instrumenting-python-fastapi-and-monitoring-with-azure-application-insights-768a59d2f4b9
if get_application_insights_connection_string():
    configure_azure_monitor()

tracer = trace.get_tracer(__name__, tracer_provider=get_tracer_provider())

app = Flask(__name__)
app.json = UpdatedJSONProvider(app)


FlaskInstrumentor.instrument_app(app)


@app.route("/brp/brp", methods=["GET"])
@auth.login_required
def get_brp():
    with tracer.start_as_current_span("/brp"):
        user = auth.get_current_user()
        brp = mks_client_02_04.get_0204(user["id"])

        if not IS_SHOW_BSN_ENABLED:
            remove_attr(brp, "bsn")

        return success_response_json(brp)


@app.route("/brp/hr", methods=["GET"])
@auth.login_required
def get_hr():
    with tracer.start_as_current_span("/hr"):
        user = auth.get_current_user()

        if user["type"] == auth.PROFILE_TYPE_PRIVATE:
            hr = mks_client_hr.get_from_bsn(user["id"])
            if not IS_SHOW_BSN_ENABLED and hasattr(hr, "eigenaar"):
                remove_attr(hr["eigenaar"], "bsn")
        else:
            hr = mks_client_hr.get_hr_for_kvk(user["id"])

        return success_response_json(hr)


@app.route("/brp/aantal_bewoners", methods=["POST"])
@auth.login_required
def get_aantal_bewoners():
    with tracer.start_as_current_span("/aantal_bewoners"):
        request_json = request.get_json()

        if request_json:
            try:
                address_key = request_json.get("addressKey")
                if address_key:
                    resident_count_payload = get_resident_count(decrypt(address_key))
                    return success_response_json(resident_count_payload)
            except Exception as error:
                logging.error(error)
                pass

        return error_response_json("bad request", 400)


@app.route("/")
@app.route("/status/health")
def health_check():
    return success_response_json(
        {
            "gitSha": os.getenv("MA_GIT_SHA", -1),
            "buildId": os.getenv("MA_BUILD_ID", -1),
            "otapEnv": os.getenv("MA_OTAP_ENV", None),
        }
    )


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

    return error_response_json(
        msg_server_error,
        error.code if hasattr(error, "code") else 500,
    )


if __name__ == "__main__":  # pragma: no cover
    app.run()
