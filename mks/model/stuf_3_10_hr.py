from bs4 import Tag, ResultSet

from mks.model.stuf_utils import to_string, to_date, set_fields, to_bool, as_postcode, set_extra_fields, is_nil


def extract_basic_info(eigendom: Tag):

    result = {}

    fields = [
        {'name': 'kvkNummer', 'parser': to_string},
        {'name': 'datumAanvang', 'parser': to_date},
        {'name': 'datumEinde', 'parser': to_date},
    ]

    set_fields(eigendom, fields, result)
    return result


def extract_activiteiten(activities: ResultSet):
    res_activities = []

    fields = [
        {'name': 'code', 'parser': to_string},
        {'name': 'omschrijving', 'parser': to_string},
        {'name': 'indicatieHoofdactiviteit', 'parser': to_bool},
    ]

    for act in activities:
        res_act = {}
        set_fields(act, fields, res_act)
        res_activities.append(res_act)

    return res_activities


def extract_owner_nnp(owner: Tag):
    """ Extracts data from <nietNatuurlijkPersoon> """
    result = {}

    fields = [
        {'name': 'inn.nnpId', 'parser': to_string, 'save_as': 'nnpId'},
        {'name': 'statutaireNaam', 'parser': to_string},
        {'name': 'inn.rechtsvorm', 'parser': to_string, 'save_as': 'rechtsvorm'},
        {'name': 'inn.statutaireZetel', 'parser': to_string, 'save_as': 'statutaireZetel'},
        {'name': 'datumAanvang', 'parser': to_date},
        {'name': 'datumEinde', 'parser': to_date},
        {'name': 'inn.datumVoortzetting', 'parser': to_date, 'save_as': 'datumVoortzetting'},
        {'name': 'sub.telefoonnummer', 'parser': to_string, 'save_as': 'telefoonnummer'},
        {'name': 'sub.faxnummer', 'parser': to_string, 'save_as': 'faxnummer'},
        {'name': 'sub.emailadres', 'parser': to_string, 'save_as': 'emailadres'},
        {'name': 'sub.url', 'parser': to_string, 'save_as': 'url'},
    ]

    set_fields(owner, fields, result)
    return result


def extract_address(address: Tag):
    result = {}

    fields = [
        {'name': 'wpl.woonplaatsNaam', 'parser': to_string, 'save_as': 'woonplaatsNaam'},
        {'name': 'gor.straatnaam', 'parser': to_string, 'save_as': 'straatnaam'},
        {'name': 'aoa.postcode', 'parser': as_postcode, 'save_as': 'postcode'},
        {'name': 'postcode', 'parser': as_postcode, 'save_as': '_postcode'},
        {'name': 'aoa.huisnummer', 'parser': to_string, 'save_as': 'huisnummer'},
        {'name': 'aoa.huisletter', 'parser': to_string, 'save_as': 'huisletter'},
        {'name': 'aoa.huisnummertoevoeging', 'parser': to_string, 'save_as': 'huisnummertoevoeging'},
    ]

    set_fields(address, fields, result)

    if not result['postcode']:
        if result['_postcode']:
            result['postcode'] = result['_postcode']

    del result['_postcode']

    return result


def extract_owner_persoon(owner: Tag):
    """ Extracts data from <natuurlijkPersoon> or <object StUF:entiteittype="NPS"> """
    result = {}

    fields = [
        {'name': 'inp.bsn', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
    ]

    extra_fields = [
        {'name': 'rechtsvorm', 'parser': to_string},
    ]

    set_fields(owner, fields, result)
    set_extra_fields(owner, extra_fields, result)

    # TODO: make this work for zzp. different xml tag (inp.verblijftIn or verblijfsadres?)
    #       But there is no response for this?
    address = extract_address(owner.find('verblijfsadres'))
    result['adres'] = address

    return result


def extract_owners(owners: ResultSet):
    """ Extracts data from <heeftAlsEigenaar> """
    result = []

    for owner in owners:
        nnps = owner.find_all('nietNatuurlijkPersoon')
        for i in nnps:
            nnp_result = extract_owner_nnp(i)
            nnp_result['type'] = 'nnp'
            result.append(nnp_result)

    for owner in owners:
        np = owner.find_all('natuurlijkPersoon')
        for i in np:
            np_result = extract_owner_persoon(i)
            np_result['type'] = 'np'
            result.append(np_result)

    return result


def extract_oefent_activiteiten_uit_in(activities: ResultSet):
    result = []

    if is_nil(activities):
        return {}

    fields = [
        {'name': 'vestigingsNummer', 'parser': to_string},
        {'name': 'typeringVestiging', 'parser': to_string},
        {'name': 'datumAanvang', 'parser': to_date},
        {'name': 'datumEinde', 'parser': to_date},
        {'name': 'sub.telefoonnummer', 'parser': to_string, 'save_as': 'telefoonnummer'},
        {'name': 'sub.faxnummer', 'parser': to_string, 'save_as': 'faxnummer'},
        {'name': 'sub.emailadres', 'parser': to_string, 'save_as': 'emailadres'},
    ]

    for act in activities:
        result_activity = {}
        set_fields(act, fields, result_activity)

        handelsnamen = act.find('gerelateerde', recursive=False).find_all('handelsnaam')
        namen = [naam.text for naam in handelsnamen]
        result_activity['handelsnamen'] = namen

        activiteiten_omschrijvingen = extract_activiteiten(act.find_all('activiteit'))
        result_activity['activiteiten'] = activiteiten_omschrijvingen

        result_activity['bezoekadres'] = extract_address(act.find('verblijfsadres'))
        result_activity['postadres'] = extract_address(act.find('sub.correspondentieAdres'))

        if _has_nones(result_activity['bezoekadres']):
            result_activity['bezoekadres'] = None

        if _has_nones(result_activity['postadres']):
            result_activity['postadres'] = None

        result_activity['url'] = [to_string(url.text) for url in act.find_all('sub.url') if url.text != '']

        result.append(result_activity)

    return result


def _has_nones(object):
    for i in ['woonplaatsNaam', 'straatnaam', 'postcode']:
        if object[i] is None:
            return True


def extract_data_is_eigenaar_van(is_eigenaar_van: ResultSet):

    result = []

    for eigendom in is_eigenaar_van:
        res_eigendom = {}
        basic_info = extract_basic_info(eigendom)
        res_eigendom.update(basic_info)

        activities = extract_oefent_activiteiten_uit_in(eigendom.find_all('oefentActiviteitUitIn'))
        res_eigendom['activiteiten'] = activities

        result.append(res_eigendom)

    return result
