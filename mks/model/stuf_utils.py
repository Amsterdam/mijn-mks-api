import base64
import json
from datetime import datetime
import re

from jwcrypto import jwe
from jwcrypto.common import json_encode

from mks.service.config import get_jwt_key


def encrypt(value: str) -> str:
    key = get_jwt_key()

    jwetoken = jwe.JWE(value.encode('utf-8'),
                       json_encode({"alg": "A256KW", "enc": "A256CBC-HS512"}))
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


def _set_value(tag, field, target):
    key = field.get('save_as', field['name'])

    if tag is None:
        value = None
    else:
        value = tag.string

    # put value through specified parser function
    value = field['parser'](value)
    # print(">> ", key, ":", value)
    target[key] = value


def set_extra_fields(source, fields, target):
    for field in fields:
        tag = source.find(attrs={"naam": field['name']})
        _set_value(tag, field, target)


def set_fields(source, fields, target):
    """ Iterate over the list of fields to be put on target dict from the source

        source: Beautifulsoup tree
        fields: A list of fields which data to include. Format:
                [
                  {
                    'name': source field name,
                    'parser': a function to put the value through. For example to parse a date or number,
                    'save_as': the key name the value is stored under in the result dict
                  },
                  ...
                ]
        target: a dict where the result will be put on
     """
    for field in fields:
        tag = source.find(field['name'])
        _set_value(tag, field, target)


def _set_value_on(target_dict, sourcefield, targetfield, lookup):
    # if omschrijving is set, do not attempt to overwrite it.
    if target_dict.get(targetfield):
        return

    if not target_dict[sourcefield]:
        target_dict[targetfield] = None
        return

    try:
        # int() fails when it is already filled with a name. Use that instead
        key = "%04d" % int(target_dict[sourcefield])
    except ValueError:
        target_dict[targetfield] = target_dict[sourcefield]
        return

    value = lookup.get(key, None)
    if value:
        target_dict[targetfield] = value


def to_datetime(value):
    """
    :param value:
    :return:
    """
    if not value:
        return None
    try:
        parsed_value = datetime.strptime(str(value), '%Y%m%d')
        return parsed_value
    except ValueError:
        pass
    return None


def to_date(value):
    """
    :param value:
    :return:
    """
    if not value:
        return None
    try:
        parsed_value = datetime.strptime(str(value), '%Y%m%d')
        return parsed_value.date()
    except ValueError:
        pass
    return None


def to_int(value):
    # our xml parser, automatically converts numbers. So this converter doesn't do much.
    if value == 0:
        return 0
    if not value:
        return None
    return int(value)


def to_string(value):
    if not value:
        return None
    return str(value).strip()


def to_bool(value):
    if not value:
        return False
    elif value.lower() in ["0", "n"]:
        return False
    elif value.lower() in ["1", "j"]:
        return True

    return False


def geheim_indicatie_to_bool(value):
    if not value:
        return False
    if value in ['1', '2', '3', '4', '5', '6', '7']:
        return True

    return False


def as_postcode(value):
    if not value:
        return None
    value = to_string(value)
    match = re.match(r'(?P<num>\d{4})(?P<let>[A-Za-z]{2})', value)
    if not match:
        return None

    return f"{match['num']} {match['let'].upper()}"


def to_is_amsterdam(value):
    if not value:
        return False

    value = to_int(value)

    if value == 363:
        return True
    else:
        return False
