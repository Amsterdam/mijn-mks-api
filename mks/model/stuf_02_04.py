from datetime import datetime
import re

from bs4 import Tag

from mks.model.gba import lookup_prsidb_soort_code


def _set_value(tag, field, target):
    key = field.get('save_as', field['name'])

    if tag is None:
        # tag is not in the data
        if field.get('optional') != True:
            raise AttributeError(f"Tag not found in data: {field['name']}")
        else:
            # TODO: make me dry
            value = field['parser'](None)  # make sure it goes through the parser, bool's need this
            target[key] = value
            return

    # print("tag", tag)
    value = tag.string
    if value is None:
        if field.get('optional') != True:
            raise AttributeError(f"Tag has no value: {field['name']} {tag}")

    # put value through specified parser function
    value = field['parser'](value)
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
    result = []

    fields = [
        {'name': 'omschrijving', 'parser': to_string},
        {'name': 'code', 'parser': to_int},
    ]

    # For people not living in Amsterdam we dont get the omschrijving.
    # Quick fix for Nederlandse if code == 1
    for n in result:
        if not n['omschrijving']:
            if n['code'] == "1":
                n['omschrijving'] = "Nederlandse"

    nationaliteit = {}
    for nat in nationaliteiten:
        set_fields(nat, fields, nationaliteit)

    result.append(nationaliteit)

    return result


def extract_persoon_data(persoon_tree: Tag):
    result = {}

    prs_fields = [
        {'name': 'bsn-nummer', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string, 'optional': True},
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

    set_fields(persoon_tree, prs_fields, result)
    set_extra_fields(persoon_tree.extraElementen, prs_extra_fields, result)

    # vertrokken onbekend waarheen
    if result['codeLandEmigratie'] == 0:
        result['vertrokkenOnbekendWaarheen'] = True
    else:
        result['vertrokkenOnbekendWaarheen'] = False

    result['nationaliteiten'] = get_nationaliteiten(persoon_tree.PRS.find_all('NAT'))

    return result


def extract_kinderen_data(persoon_tree: Tag):
    result = []

    knd_fields = [
        {'name': 'bsn-nummer', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string, 'optional': True},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
        {'name': 'geboorteplaats', 'parser': to_string},
        {'name': 'codeGeboorteland', 'parser': to_string, 'save_as': 'geboorteLand'},
        {'name': 'datumOverlijden', 'parser': to_date, 'optional': True, 'save_as': 'overlijdensdatum'},  # Save as name to match 3.10
        {'name': 'adellijkeTitelPredikaat', 'parser': to_string, 'optional': True},
    ]

    knd_extra_fields = [
        {'name': 'omschrijvingAdellijkeTitel', 'parser': to_string, 'optional': True},
        {'name': 'geboortelandnaam', 'parser': to_string},
        {'name': 'geboorteplaatsnaam', 'parser': to_string},
        {'name': 'omschrijvingGeslachtsaanduiding', 'parser': to_string},
        {'name': 'opgemaakteNaam', 'parser': to_string, 'optional': True},  # TODO Niet optional: niet geauthoriserd
    ]

    kinderen = persoon_tree.find_all('PRSPRSKND')
    if kinderen[0].get("xsi:nil") == 'true':
        return []

    for kind in kinderen:
        result_kind = {}
        set_fields(kind.PRS, knd_fields, result_kind)
        set_extra_fields(kind.PRS, knd_extra_fields, result_kind)

        result.append(result_kind)

    return result


def extract_parents_data(persoon_tree: Tag):
    result = []

    parent_fields = [
        {'name': 'bsn-nummer', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string, 'optional': True},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
        {'name': 'geboorteplaats', 'parser': to_string},
        {'name': 'codeGeboorteland', 'parser': to_string, 'save_as': 'geboorteLand'},  # save as to match 3.10
        {'name': 'datumOverlijden', 'parser': to_date, 'optional': True, 'save_as': 'overlijdensdatum'},  # save as to match 3.10'
        {'name': 'adellijkeTitelPredikaat', 'parser': to_string, 'optional': True},
    ]

    parent_extra_fields = [
        {'name': 'omschrijvingAdellijkeTitel', 'parser': to_string, 'optional': True},
        {'name': 'geboortelandnaam', 'parser': to_string},
        {'name': 'geboorteplaatsnaam', 'parser': to_string},
        {'name': 'omschrijvingGeslachtsaanduiding', 'parser': to_string},
        {'name': 'opgemaakteNaam', 'parser': to_string, 'optional': True},  # TODO Niet optional: niet geauthoriserd
    ]

    parents = persoon_tree.find_all('PRSPRSOUD')
    if parents[0].get("xsi:nil") == 'true':
        return []

    for ouder in parents:
        result_parent = {}
        set_fields(ouder.PRS, parent_fields, result_parent)
        set_extra_fields(ouder.PRS, parent_extra_fields, result_parent)

        result.append(result_parent)

    return result


def extract_verbintenis_data(persoon_tree: Tag):
    result = []

    verbintenis_fields = [
        {'name': 'datumSluiting', 'parser': to_date},
        {'name': 'datumOntbinding', 'parser': to_date, 'optional': True},
        {'name': 'soortVerbintenis', 'parser': to_string, 'optional': True},
    ]

    verbintenis_extra_fields = [
        {'name': 'soortVerbintenisOmschrijving', 'parser': to_string},
        {'name': 'landnaamSluiting', 'parser': to_string},
        {'name': 'plaatsnaamSluitingOmschrijving', 'parser': to_string},
    ]

    partner_fields = [
        {'name': 'bsn-nummer', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string, 'optional': True},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
        {'name': 'datumOverlijden', 'parser': to_date, 'optional': True, 'save_as': 'overlijdensdatum'},  # to match 3.10 field name
        {'name': 'adellijkeTitelPredikaat', 'parser': to_string, 'optional': True},
    ]

    partner_extra_fields = [
        {'name': 'omschrijvingAdellijkeTitel', 'parser': to_string, 'optional': True},
        {'name': 'geboortelandnaam', 'parser': to_string},
        {'name': 'geboorteplaatsnaam', 'parser': to_string},
        {'name': 'omschrijvingGeslachtsaanduiding', 'parser': to_string},
        {'name': 'opgemaakteNaam', 'parser': to_string, 'optional': True},  # TODO Niet optional: niet geauthoriserd
    ]

    verbintenissen = persoon_tree.find_all('PRSPRSHUW')

    for verb in verbintenissen:
        result_verbintenis = {'persoon': {}}

        set_fields(verb, verbintenis_fields, result_verbintenis)
        set_extra_fields(verb, verbintenis_extra_fields, result_verbintenis)

        set_fields(verb.PRS, partner_fields, result_verbintenis)
        set_extra_fields(verb.PRS, partner_extra_fields, result_verbintenis)

        result.append(result_verbintenis)


    # if there is no datumSluiting, sort using the minimum datetime
    # sort to be sure that the most current partner is on top
    result.sort(key=lambda x: x['datumSluiting'] or datetime.datetime.min)

    current_results = [p for p in result if not p['datumOntbinding']]

    if current_results:
        current_result = current_results[0]
    else:
        current_result = {}

    past_result = [p for p in result if p['datumOntbinding']]

    return {
        'verbintenis': current_result,
        'verbintenisHistorisch': past_result,
    }


def extract_address(persoon_tree: Tag):
    result = {}
    fiels_tijdvak = [
        {'name': 'begindatumRelatie', 'parser': to_date, 'save_as': 'begindatumVerblijf'},
        {'name': 'einddatumRelatie', 'parser': to_date, 'save_as': 'einddatumVerblijf', 'optional': True},

    ]
    extra_fields = [
        {'name': 'aanduidingGegevensInOnderzoek', 'parser': to_bool, 'save_as': 'adresInOnderzoek', 'optional': True},
    ]

    address_fields = [
        {'name': 'woonplaatsnaam', 'parser': to_string, 'save_as': 'woonplaatsNaam'},
        {'name': 'postcode', 'parser': as_postcode},
        {'name': 'huisnummer', 'parser': to_string},
        {'name': 'huisletter', 'parser': to_string, 'optional': True},
        {'name': 'huisnummertoevoeging', 'parser': to_string, 'optional': True},
        {'name': 'straatnaam', 'parser': to_string},

        {'name': 'centroidXCoordinaat', 'parser': to_string, 'optional': True},
        {'name': 'centroidYCoordinaat', 'parser': to_string, 'optional': True},
        {'name': 'centroidZCoordinaat', 'parser': to_string, 'optional': True},
    ]
    address_extra_fields = [
        {'name': 'authentiekeWoonplaatsnaam', 'parser': to_string, 'optional': True},
        {'name': 'officieleStraatnaam', 'parser': to_string, 'optional': True},
    ]

    address = persoon_tree.find('PRSADRINS')
    set_fields(address.tijdvakRelatie, fiels_tijdvak, result)
    set_extra_fields(address, extra_fields, result)

    address_adr = address.ADR
    set_fields(address_adr, address_fields, result)
    set_extra_fields(address_adr, address_extra_fields, result)

    if result['authentiekeWoonplaatsnaam']:
        result['woonplaatsNaam'] = result['authentiekeWoonplaatsnaam']
    del result['authentiekeWoonplaatsnaam']

    if result['officieleStraatnaam']:
        result['straatnaam'] = result['officieleStraatnaam']
    del result['officieleStraatnaam']

    return result


def extract_identiteitsbewijzen(persoon_tree: Tag):
    result = []
    fields = [
        {'name': 'nummerIdentiteitsbewijs', 'parser': to_string, 'save_as': 'documentNummer'},
    ]
    extra_fields = [
        {'name': 'datumAfgifte', 'parser': to_date, 'save_as': 'datumUitgifte'},
        {'name': 'datumEindeGeldigheid', 'parser': to_date, 'save_as': 'datumAfloop'},
    ]
    SIB_fields = [
        {'name': 'soort', 'parser': to_int, 'save_as': 'documentType'},
    ]

    identiteitsbewijzen = persoon_tree.find_all('PRSIDB')
    for id in identiteitsbewijzen:
        result_id = {}
        set_fields(id, fields, result_id)
        set_extra_fields(id, extra_fields, result_id)
        set_fields(id.SIB, SIB_fields, result_id)

        result_id['documentType'] = lookup_prsidb_soort_code[result_id['documentType']]

        result.append(result_id)

    return result


def extract_data(persoon_tree: Tag):
    verbintenissen = extract_verbintenis_data(persoon_tree)

    return {
        "persoon": extract_persoon_data(persoon_tree),
        "kinderen": extract_kinderen_data(persoon_tree),
        "ouders": extract_parents_data(persoon_tree),
        'verbintenis': verbintenissen['verbintenis'],
        'verbintenisHistorisch': verbintenissen['verbintenisHistorisch'],
        'adres': extract_address(persoon_tree),
        'identiteitsbewijzen': extract_identiteitsbewijzen(persoon_tree),
    }


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
