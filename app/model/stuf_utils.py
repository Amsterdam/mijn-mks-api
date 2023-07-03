from datetime import datetime
import re
import calendar
from typing import Union

from bs4 import Tag, ResultSet

from app.model.gba import lookup_landen


def is_nil(element: Union[Tag, ResultSet]) -> bool:
    """Return true if the element is empty, empty ResultSet or attr xsi:nil"""
    if not element:
        return True

    if isinstance(element, Tag):
        if element.get("xsi:nil") == "true":
            return True

    if isinstance(element, ResultSet) and len(element) == 1:
        if element[0].get("xsi:nil") == "true":
            return True

    if len(element) == 0:
        return True

    return False


def _set_value(tag, field, target, withTag=False):
    key = field.get("save_as", field["name"])

    if tag is None:
        value = None
    else:
        value = tag.string

    # put value through specified parser function
    value = field["parser"](value, tag) if withTag else field["parser"](value)

    # print(">> ", key, ":", value)
    target[key] = value


def set_extra_fields(source, fields, target):
    for field in fields:
        tag = source.find(attrs={"naam": field["name"]})
        _set_value(tag, field, target)


def set_fields(source, fields, target):
    """Iterate over the list of fields to be put on target dict from the source

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
        tag = source.find(field["name"])
        _set_value(tag, field, target)


def set_fields_with_attributes(source, fields, target):
    for field in fields:
        tag = source.find(field["name"])
        _set_value(tag, field, target, True)


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
        parsed_value = datetime.strptime(str(value), "%Y%m%d")
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
        parsed_value = datetime.strptime(str(value), "%Y%m%d")
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


def to_string_4x0(value):
    """Return value as string padded with zeros at the front"""
    if not value:
        return None
    return str(value).strip().zfill(4)


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
    if value in ["1", "2", "3", "4", "5", "6", "7"]:
        return True

    return False


def as_postcode(value):
    if not value:
        return None
    value = to_string(value)
    match = re.match(r"(?P<num>\d{4})(?P<let>[A-Za-z]{2})", value)
    if not match:
        return None

    return f"{match['num']} {match['let'].upper()}"


def as_bsn(value: str) -> str:
    if not value:
        return None
    return value.zfill(9)


def to_is_amsterdam(value):
    if not value:
        return False

    value = to_int(value)

    if value == 363:
        return True
    else:
        return False


def landcode_to_name(value: str) -> str:
    if not value:
        return None

    return lookup_landen.get(value, None)


def to_adres_in_onderzoek(value: str):
    if not value:
        return None

    # Deze waardes corresponderen met 2 verschillende onderzoekstypen:
    # 080000: Er wordt onderzocht of persoon nog op dit huidig adres verblijft.
    # 089999: Er is vastgesteld dat persoon niet meer op adres verblijft, onderzoek naar huidige verblijfplaats loopt nog.
    if value in ["080000", "089999"]:
        return value

    return None

def geboortedatum_to_string(value, tag):
    if value is None:
        return None

    indicatie = tag.get("indOnvolledigeDatum")  # J, M, D, V of None
    valueAsDate = to_date(value)

    if indicatie == "J":
        return "00 00 0000"
    elif indicatie == "M":
        return f"00 00 {valueAsDate.year}"  # 00 00 1957
    elif indicatie == "D":
        return f"00 {calendar.month_name[valueAsDate.month]} {valueAsDate.year}"  # 00 juli 1957

    return f"{valueAsDate.day} {calendar.month_name[valueAsDate.month]} {valueAsDate.year}"
