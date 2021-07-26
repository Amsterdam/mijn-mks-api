from bs4 import Tag, ResultSet

from mks.model.stuf_utils import (
    to_string,
    to_date,
    set_fields,
    to_bool,
    as_postcode,
    set_extra_fields,
    is_nil,
)
from mks.model.stuf_02_04 import _format_achternaam


def extract_basic_info(eigendom: Tag):

    result = {}

    fields = [
        {"name": "kvkNummer", "parser": to_string},
        {"name": "datumAanvang", "parser": to_date},
        {"name": "datumEinde", "parser": to_date},
    ]

    set_fields(eigendom, fields, result)
    return result


def extract_activiteiten(activities: ResultSet):
    res_activities = []

    fields = [
        {"name": "code", "parser": to_string},
        {"name": "omschrijving", "parser": to_string},
        {"name": "indicatieHoofdactiviteit", "parser": to_bool},
    ]

    for act in activities:
        res_act = {}
        set_fields(act, fields, res_act)
        res_activities.append(res_act)

    return res_activities


def extract_owner_nnp(owner: Tag):
    """Extracts data from <nietNatuurlijkPersoon>"""
    result = {}

    fields = [
        {"name": "inn.nnpId", "parser": to_string, "save_as": "nnpId"},
        {"name": "statutaireNaam", "parser": to_string},
        {"name": "inn.rechtsvorm", "parser": to_string, "save_as": "rechtsvorm"},
        {
            "name": "inn.statutaireZetel",
            "parser": to_string,
            "save_as": "statutaireZetel",
        },
        {"name": "datumAanvang", "parser": to_date},
        {"name": "datumEinde", "parser": to_date},
        {
            "name": "inn.datumVoortzetting",
            "parser": to_date,
            "save_as": "datumVoortzetting",
        },
        {
            "name": "sub.telefoonnummer",
            "parser": to_string,
            "save_as": "telefoonnummer",
        },
        {"name": "sub.faxnummer", "parser": to_string, "save_as": "faxnummer"},
        {"name": "sub.emailadres", "parser": to_string, "save_as": "emailadres"},
        {"name": "sub.url", "parser": to_string, "save_as": "url"},
    ]

    set_fields(owner, fields, result)
    return result


def extract_address(address: Tag):
    result = {}

    fields = [
        {
            "name": "wpl.woonplaatsNaam",
            "parser": to_string,
            "save_as": "woonplaatsNaam",
        },
        {"name": "gor.straatnaam", "parser": to_string, "save_as": "straatnaam"},
        {
            "name": "gor.openbareRuimteNaam",
            "parser": to_string,
            "save_as": "_straatnaam",
        },
        {"name": "aoa.postcode", "parser": as_postcode, "save_as": "postcode"},
        {"name": "postcode", "parser": as_postcode, "save_as": "_postcode"},
        {"name": "aoa.huisnummer", "parser": to_string, "save_as": "huisnummer"},
        {"name": "aoa.huisletter", "parser": to_string, "save_as": "huisletter"},
        {
            "name": "aoa.huisnummertoevoeging",
            "parser": to_string,
            "save_as": "huisnummertoevoeging",
        },
    ]

    set_fields(address, fields, result)

    if not result["postcode"]:
        if result["_postcode"]:
            result["postcode"] = result["_postcode"]

    del result["_postcode"]

    if not result["straatnaam"]:
        if result["_straatnaam"]:
            result["straatnaam"] = result["_straatnaam"]

    del result["_straatnaam"]

    return result


def extract_owner_persoon(owner: Tag):
    """Extracts data from <natuurlijkPersoon> or <object StUF:entiteittype="NPS">"""
    result = {}

    fields = [
        {"name": "inp.bsn", "parser": to_string, "save_as": "bsn"},
        {"name": "geslachtsnaam", "parser": to_string},
        {"name": "voornamen", "parser": to_string},
        {"name": "geboortedatum", "parser": to_date},
    ]

    extra_fields = [
        {"name": "rechtsvorm", "parser": to_string},
    ]

    set_fields(owner, fields, result)
    set_extra_fields(owner, extra_fields, result)

    # TODO: make this work for zzp. different xml tag (inp.verblijftIn or verblijfsadres?)
    #       But there is no response for this?
    address = extract_address(owner.find("verblijfsadres"))
    result["adres"] = address

    return result


def extract_owners(owners: ResultSet):
    """Extracts data from <heeftAlsEigenaar>"""
    result = []

    for owner in owners:
        nnps = owner.find_all("nietNatuurlijkPersoon")
        for i in nnps:
            nnp_result = extract_owner_nnp(i)
            nnp_result["type"] = "nnp"
            result.append(nnp_result)

    for owner in owners:
        np = owner.find_all("natuurlijkPersoon")
        for i in np:
            np_result = extract_owner_persoon(i)
            np_result["type"] = "np"
            result.append(np_result)

    return result


def extract_oefent_activiteiten_uit_in(activities: ResultSet):
    result = []

    if is_nil(activities):
        return {}

    fields = [
        {"name": "vestigingsNummer", "parser": to_string},
        {"name": "typeringVestiging", "parser": to_string},
        {"name": "datumAanvang", "parser": to_date},
        {"name": "datumEinde", "parser": to_date},
        {
            "name": "sub.telefoonnummer",
            "parser": to_string,
            "save_as": "telefoonnummer",
        },
        {"name": "sub.faxnummer", "parser": to_string, "save_as": "faxnummer"},
        {"name": "sub.emailadres", "parser": to_string, "save_as": "emailadres"},
    ]

    for act in activities:
        result_activity = {}
        set_fields(act, fields, result_activity)

        handelsnamen = act.find("gerelateerde", recursive=False).find_all("handelsnaam")
        namen = [naam.text for naam in handelsnamen]
        result_activity["handelsnamen"] = namen

        activiteiten_omschrijvingen = extract_activiteiten(act.find_all("activiteit"))
        result_activity["activiteiten"] = activiteiten_omschrijvingen

        result_activity["bezoekadres"] = extract_address(act.find("verblijfsadres"))
        result_activity["postadres"] = extract_address(
            act.find("sub.correspondentieAdres")
        )

        if _has_nones(result_activity["bezoekadres"]):
            result_activity["bezoekadres"] = None

        if _has_nones(result_activity["postadres"]):
            result_activity["postadres"] = None

        result_activity["url"] = [
            to_string(url.text) for url in act.find_all("sub.url") if url.text != ""
        ]

        result.append(result_activity)

    return result


def _has_nones(object):
    for i in ["woonplaatsNaam", "straatnaam", "postcode"]:
        if object[i] is None:
            return True


def extract_data_is_eigenaar_van(is_eigenaar_van: ResultSet):

    result = []

    for eigendom in is_eigenaar_van:
        res_eigendom = {}
        basic_info = extract_basic_info(eigendom)
        res_eigendom.update(basic_info)

        activities = extract_oefent_activiteiten_uit_in(
            eigendom.find_all("oefentActiviteitUitIn")
        )
        res_eigendom["activiteiten"] = activities

        result.append(res_eigendom)

    return result


def naam_en_achternaam(persoon: dict):
    voornamen = persoon["voornamen"]
    partner = {
        "geslachtsnaam": persoon.get("geslachtsnaamPartner", None),
        "voorvoegselGeslachtsnaam": persoon.get(
            "voorvoegselGeslachtsnaamPartner", None
        ),
    }
    achternaam = _format_achternaam(persoon, partner)
    return f"{voornamen} {achternaam}"


def find_extra_element_value_by_name(source: Tag, name: str):
    return source.find(attrs={"naam": name}).string


def naam_en_geboortedatum(source: Tag):
    source_fields = [
        {"name": "voornamen", "parser": to_string},
        {"name": "voorvoegselGeslachtsnaam", "parser": to_string},
        {"name": "geslachtsnaam", "parser": to_string},
        {"name": "aanduidingNaamgebruik", "parser": to_string},
        {"name": "geslachtsnaamPartner", "parser": to_string},
        {"name": "voorvoegselGeslachtsnaamPartner", "parser": to_string},
        {"name": "geboortedatum", "parser": to_date},
    ]
    target_item = {}
    set_fields(source, source_fields, target_item)

    return {
        "naam": naam_en_achternaam(target_item),
        "geboortedatum": target_item["geboortedatum"],
    }


def extract_functionaris_by_type(source: Tag, typeFunctionaris: str):
    return [
        functionaris
        for functionaris in source.find_all("inn.heeftAlsFunctionaris")
        if functionaris.find("functionarisType").string == typeFunctionaris
    ]


def extract_bestuurders(nnp_data: Tag):
    bestuurders = []
    bestuurders_data = extract_functionaris_by_type(
        nnp_data, "heeftBestuursfunctionaris"
    )

    for bestuurder_item in bestuurders_data:
        bestuurder = {
            "functie": find_extra_element_value_by_name(bestuurder_item, "functie"),
            "soortBevoegdheid": find_extra_element_value_by_name(
                bestuurder_item, "soortBevoegdheid"
            ),
        }
        bestuurder.update(naam_en_geboortedatum(bestuurder_item))
        bestuurders.append(bestuurder)

    return bestuurders


def extract_gemachtigden(nnp_data: Tag):
    gemachtigden = []
    gemachtigden_data = extract_functionaris_by_type(nnp_data, "heeftGemachtigde")

    for gemachtigde_item in gemachtigden_data:
        gemachtigde = {
            "functie": find_extra_element_value_by_name(gemachtigde_item, "functie"),
            "datumIngangMachtiging": None,
        }
        gemachtigde.update(naam_en_geboortedatum(gemachtigde_item))
        gemachtigden.append(gemachtigde)

    return gemachtigden


def extract_overige_functionarissen(nnp_data: Tag):
    overige_functionarissen = []
    overige_functionarissen_data = extract_functionaris_by_type(
        nnp_data, "heeftOverigeFunctionaris"
    )

    for functionaris_item in overige_functionarissen_data:
        functionaris = {
            "functie": find_extra_element_value_by_name(functionaris_item, "functie"),
        }
        functionaris.update(naam_en_geboortedatum(functionaris_item))
        overige_functionarissen.append(functionaris)

    return overige_functionarissen


def extract_aansprakelijken(nnp_data: Tag):
    aansprakelijken = []
    aansprakelijken_data = extract_functionaris_by_type(nnp_data, "heeftAansprakelijke")

    for aansprakelijke_item in aansprakelijken_data:
        aansprakelijke = {
            "functie": find_extra_element_value_by_name(aansprakelijke_item, "functie"),
            "soortBevoegdheid": find_extra_element_value_by_name(
                aansprakelijke_item, "soortBevoegdheid"
            ),
        }
        aansprakelijke.update(naam_en_geboortedatum(aansprakelijke_item))
        aansprakelijken.append(aansprakelijke)

    return aansprakelijken
