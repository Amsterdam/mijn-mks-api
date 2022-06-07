import base64
import json
import os
from functools import wraps
from jinja2 import Template

import yaml
from flask import request
from flask.helpers import make_response
from jwcrypto import jwe
from jwcrypto.common import json_encode
from openapi_core import create_spec
from openapi_core.contrib.flask import FlaskOpenAPIRequest, FlaskOpenAPIResponse
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.validators import ResponseValidator
from yaml import load

from app.config import BASE_PATH, ENABLE_OPENAPI_VALIDATION, SERVICES_DIR, get_jwt_key

openapi_spec = None


def get_openapi_spec():
    global openapi_spec
    if not openapi_spec:
        with open(os.path.join(BASE_PATH, "openapi.yml"), "r") as spec_file:
            spec_dict = load(spec_file, Loader=yaml.Loader)

        openapi_spec = create_spec(spec_dict)

    return openapi_spec


def validate_openapi(function):
    @wraps(function)
    def validate(*args, **kwargs):

        if ENABLE_OPENAPI_VALIDATION:
            spec = get_openapi_spec()
            openapi_request = FlaskOpenAPIRequest(request)
            validator = RequestValidator(spec)
            result = validator.validate(openapi_request)
            result.raise_for_errors()

        response = function(*args, **kwargs)

        if ENABLE_OPENAPI_VALIDATION:
            openapi_response = FlaskOpenAPIResponse(response)
            validator = ResponseValidator(spec)
            result = validator.validate(openapi_request, openapi_response)
            result.raise_for_errors()

        return response

    return validate


def success_response_json(response_content):
    return make_response({"status": "OK", "content": response_content}, 200)


def error_response_json(message: str, code: int = 500):
    return make_response({"status": "ERROR", "message": message}, code)


def encrypt(value: str) -> str:
    key = get_jwt_key()
    jwetoken = jwe.JWE(
        value.encode("utf-8"), json_encode({"alg": "A256KW", "enc": "A256CBC-HS512"})
    )
    jwetoken.add_recipient(key)
    enc = json.dumps(jwetoken.serialize()).encode()
    enc = base64.b64encode(enc)
    return enc.decode()


def decrypt(encrypted_value: str):
    key = get_jwt_key()
    encrypted_value = base64.b64decode(encrypted_value)
    payload = json.loads(encrypted_value)

    jwetoken = jwe.JWE()
    jwetoken.deserialize(payload)
    jwetoken.decrypt(key)
    return jwetoken.payload.decode()


def get_request_template(name):
    filename = os.path.join(SERVICES_DIR, f"{name}.jinja2")
    with open(filename) as fp:
        return Template(fp.read())
