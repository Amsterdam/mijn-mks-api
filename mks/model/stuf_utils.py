from datetime import datetime
from typing import re


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


def to_date(value):
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
    elif value == "0":
        return False
    elif value == "1":
        return True

    return True


def as_postcode(value):
    if not value:
        return None
    value = to_string(value)
    match = re.match(r'(?P<num>\d{4})(?P<let>[A-Z]{2})', value)
    if not match:
        return None

    return f"{match['num']} {match['let']}"


def to_is_amsterdam(value):
    if not value:
        return False

    value = to_int(value)

    if value == 363:
        return True
    else:
        return False
