from bs4 import Tag, ResultSet

from mks.model.stuf_utils import to_string, to_date, set_fields, to_bool


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


def extract_oefent_activiteiten_uit_in(activities: ResultSet):
    result = []

    fields = [
        {'name': 'vestigingsNummer', 'parser': to_string},
        {'name': 'typeringVestiging', 'parser': to_string},
        {'name': 'datumAanvang', 'parser': to_date},
        {'name': 'datumEinde', 'parser': to_date},
        {'name': 'sub.telefoonnummer', 'parser': to_string, 'save_as': 'telefoonnummer'},
        {'name': 'sub.faxnummer', 'parser': to_string, 'save_as': 'faxnummer'},
        {'name': 'sub.emailadres', 'parser': to_string, 'save_as': 'emailadres'},
        {'name': 'sub.rekeningnummerBankGiro', 'parser': to_string, 'save_as': 'rekeningnummerBankGiro'},
    ]

    for act in activities:
        result_activity = {}
        set_fields(act, fields, result_activity)

        handelsnamen = act.find('gerelateerde', recursive=False).find_all('handelsnaam')
        namen = [naam.text for naam in handelsnamen]
        result_activity['handelsnamen'] = namen

        activiteiten_omschrijvingen = extract_activiteiten(act.find_all('activiteit'))
        result_activity['activities'] = activiteiten_omschrijvingen

        result.append(result_activity)

    return result





def extract_data(is_eigenaar_van: ResultSet):

    result = []

    for eigendom in is_eigenaar_van:
        res_eigendom = {}
        basic_info = extract_basic_info(eigendom)
        res_eigendom.update(basic_info)

        activities = extract_oefent_activiteiten_uit_in(eigendom.find_all('oefentActiviteitUitIn'))
        res_eigendom['activities'] = activities

        result.append(res_eigendom)

    from pprint import pprint
    pprint(result)