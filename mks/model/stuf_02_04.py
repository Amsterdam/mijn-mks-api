from datetime import datetime
import re

from bs4 import Tag


def _set_value(tag, field, target):
    if tag is None:
        # tag is not in the data
        if field.get('optional') != True:
            raise AttributeError(f"Tag not found in data: {field['name']}")

    value = tag.string
    if value is None:
        if field.get('optional') != True:
            raise AttributeError(f"Tag has no value: {field['name']} {tag}")

    # put value through specified parser function
    value = field['parser'](value)
    key = field.get('save_as', field['name'])
    print(">> ", key, ":", value)
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


def get_nationaliteiten(nationaliteiten: Tag):
    print("ttt", type(nationaliteiten))
    result = []

    fields = [
        {'name': 'omschrijving', 'parser': to_string},
        {'name': 'code', 'parser': to_string}
    ]

    nationaliteit = {}
    for nat in nationaliteiten:
        print("nat", nat)
        set_fields(nat, fields, nationaliteit)

    result.append(nationaliteit)

    return result


def extract_data(person_tree: Tag):
    result = {}

    prs_fields = [
        {'name': 'bsn-nummer', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string},
        {'name': 'codeGemeenteVanInschrijving', 'parser': to_is_amsterdam, 'save_as': 'mokum'},
        {'name': 'geboorteplaats', 'parser': to_string},
        {'name': 'codeGeboorteland', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'codeLandEmigratie', 'parser': to_int, 'optional': True},
        {'name': 'datumVertrekUitNederland', 'parser': to_date, 'optional': True},
    ]

    prs_extra_fields = [
        {'name': 'aanduidingNaamgebruikOmschrijving', 'parser': to_string, 'optional': True},  # TODO Niet optional: niet geauthoriserd
        {'name': 'geboortelandnaam', 'parser': to_string},
        {'name': 'geboorteplaatsnaam', 'parser': to_string},
        {'name': 'gemeentenaamInschrijving', 'parser': to_string},
        {'name': 'omschrijvingBurgerlijkeStaat', 'parser': to_string, 'optional': True},  # TODO Niet optional: niet geauthoriserd
        {'name': 'omschrijvingGeslachtsaanduiding', 'parser': to_string},
        {'name': 'omschrijvingIndicatieGeheim', 'parser': to_string},
        {'name': 'opgemaakteNaam', 'parser': to_string, 'optional': True},   # TODO Niet optional: niet geauthoriserd
        {'name': 'omschrijvingAdellijkeTitel', 'parser': to_string},
    ]

    set_fields(person_tree, prs_fields, result)
    set_extra_fields(person_tree.extraElementen, prs_extra_fields, result)

    # vertrokken onbekend waarheen
    if result['codeLandEmigratie'] == 0:
        result['vertrokkenOnbekendWaarheen'] = True
    else:
        result['vertrokkenOnbekendWaarheen'] = False

    result['nationaliteiten'] = get_nationaliteiten(person_tree.PRS.find_all('NAT'))

    return result



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


