import base64
import json
import os

from flask.helpers import make_response
from jinja2 import Template
from jwcrypto import jwe
from jwcrypto.common import json_encode

from app.config import SERVICES_DIR, get_jwt_key


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


def remove_attr(input, attr):
    if isinstance(input, dict):
        for key in list(input.keys()):
            if key == attr:
                input.pop(key)
            else:
                remove_attr(input[key], attr)
    if isinstance(input, list):
        for list_item in input:
            remove_attr(list_item, attr)
