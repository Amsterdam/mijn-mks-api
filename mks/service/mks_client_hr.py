import logging
import os
import time
from datetime import datetime
from io import BytesIO
from random import randint

import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from lxml import etree
from mks.model.stuf_3_10_hr import (
    extract_aansprakelijken,
    extract_basic_info,
    extract_bestuurders,
    extract_gemachtigden,
    extract_oefent_activiteiten_uit_in,
    extract_overige_functionarissen,
    extract_owner_persoon,
    extract_owners,
)
from mks.model.stuf_utils import is_nil
from mks.service.config import (
    BRP_APPLICATIE,
    BRP_GEBRUIKER,
    MKS_CLIENT_CERT,
    MKS_CLIENT_KEY,
    MKS_ENDPOINT,
    PROJECT_DIR,
    REQUEST_TIMEOUT,
)
from mks.service.exceptions import ExtractionError, NoResultException

HR_TEMPLATE_PATH = os.path.join(PROJECT_DIR, "HR_stuf0310.xml.jinja2")
with open(HR_TEMPLATE_PATH) as fp:
    hr_template = Template(fp.read())

NNP_TEMPLATE_PATH = os.path.join(PROJECT_DIR, "NNP_stuf0310.xml.jinja2")
with open(NNP_TEMPLATE_PATH) as fp:
    nnp_template = Template(fp.read())

log_response = False

HR_URL = f"{MKS_ENDPOINT}/CGS/StUF/0301/BG/0310/services/BeantwoordVraag"


def _get_soap_request_payload(
    template: Template = None,
    bsn: str = None,
    kvk_number: str = None,
    nnpid: str = None,
):
    ref = str(randint(100000, 999999))

    referentienummer = f"MijnAmsterdam||{ref}"
    context = {
        "applicatie": BRP_APPLICATIE,
        "gebruiker": BRP_GEBRUIKER,
        "referentienummer": referentienummer,
        "timestamp": datetime.now().strftime("%Y%m%d%H%M%S") + "00",
    }
    if bsn:
        context["bsn"] = bsn
    if kvk_number:
        context["kvk_nummer"] = kvk_number
    if nnpid:
        context["nnpid"] = nnpid

    return template.render(context)


def _get_response(mks_url, soap_request_payload):
    session = requests.Session()
    session.headers.update(
        {
            "Content-Type": "text/xml;charset=UTF-8",
            # 'SOAPAction': 'http://www.egem.nl/StUF/sector/bg/0204/beantwoordSynchroneVraagIntegraal',
        }
    )
    session.cert = (MKS_CLIENT_CERT, MKS_CLIENT_KEY)
    request_start = time.time()
    try:
        post_response = session.post(
            mks_url, data=soap_request_payload, timeout=REQUEST_TIMEOUT
        )
    finally:
        request_end = time.time()
        logging.info(f"request took: '{request_end - request_start}' seconds")

    return post_response.content


def _get_from_mks(
    url: str = None,
    template: Template = None,
    bsn: str = None,
    kvk_number: str = None,
    nnpid: str = None,
):
    soap_request_payload = _get_soap_request_payload(template, bsn, kvk_number, nnpid)

    response = _get_response(url, soap_request_payload)

    if log_response:
        content_bytesio = BytesIO(response)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())

    return response


def _get_response_by_bsn(bsn: str = None):
    return _get_from_mks(url=HR_URL, template=hr_template, bsn=bsn)


def _get_response_by_kvk_number(kvk_number: str = None):
    return _get_from_mks(url=HR_URL, template=hr_template, kvk_number=kvk_number)


def _get_response_by_nnpid(nnpid: str = None):
    return _get_from_mks(url=HR_URL, template=nnp_template, nnpid=nnpid)


def extract_for_bsn(xml_data):
    try:
        tree = BeautifulSoup(xml_data, features="lxml-xml")

        if tree.find("Body") is None:
            raise NoResultException()

        object_data = tree.Body.find("rps.isEigenaarVan")
        activiteiten = tree.Body.find_all("oefentActiviteitUitIn")
        eigenaren = tree.Body.find("object")

        if is_nil(object_data):
            return {}

        object_data = extract_basic_info(object_data)
        eigenaar_data = extract_owner_persoon(eigenaren)
        activiteiten_data = extract_oefent_activiteiten_uit_in(activiteiten)

        handelsnamen = set()
        primaire_handelsnamen = None
        ondernemingsactiviteiten = set()
        vestigingen = []
        hoofdactiviteit = None

        for i in activiteiten_data:

            for j in i["activiteiten"]:
                if j["indicatieHoofdactiviteit"]:
                    hoofdactiviteit = j["omschrijving"]
                else:
                    ondernemingsactiviteiten.add(j["omschrijving"])

            if i["typeringVestiging"] == "Hoofdvestiging":
                primaire_handelsnamen = i["handelsnamen"]
            else:
                handelsnamen.update(i["handelsnamen"])

            vestiging = {
                "vestigingsNummer": i["vestigingsNummer"],
                "handelsnamen": i["handelsnamen"],
                "typeringVestiging": i["typeringVestiging"],
                "datumAanvang": i["datumAanvang"],
                "datumEinde": i["datumEinde"],
                "telefoonnummer": i["telefoonnummer"],
                "faxnummer": i["faxnummer"],
                "emailadres": i["emailadres"],
                "websites": i["url"],
                "activiteiten": [j["omschrijving"] for j in i["activiteiten"]],
                "bezoekadres": i["bezoekadres"],
                "postadres": i["postadres"],
            }
            vestigingen.append(vestiging)

        handelsnamen = sorted(list(handelsnamen))

        if primaire_handelsnamen:
            handelsnamen = primaire_handelsnamen + handelsnamen

        rechtsvorm = eigenaar_data["rechtsvorm"]

        onderneming = {
            "kvkNummer": object_data["kvkNummer"],
            "datumAanvang": object_data["datumAanvang"],
            "datumEinde": object_data["datumEinde"],
            "handelsnamen": handelsnamen,
            "rechtsvorm": rechtsvorm,
            "overigeActiviteiten": sorted(list(ondernemingsactiviteiten)),
            "hoofdactiviteit": hoofdactiviteit,
        }

        eigenaar = {
            "naam": "%s %s"
            % (eigenaar_data["voornamen"], eigenaar_data["geslachtsnaam"]),
            "geboortedatum": eigenaar_data["geboortedatum"],
            "adres": eigenaar_data["adres"],
            "bsn": eigenaar_data.get("bsn", None),
        }

        is_amsterdammer = False
        for i in vestigingen:
            if i["typeringVestiging"]:
                if (
                    i["bezoekadres"]
                    and i["bezoekadres"]["woonplaatsNaam"] == "Amsterdam"
                ) or (
                    i["postadres"] and i["postadres"]["woonplaatsNaam"] == "Amsterdam"
                ):
                    is_amsterdammer = True

        data = {
            "mokum": is_amsterdammer,
            "nnpid": None,  # Eenmanszaken don't have NNPID
            "onderneming": onderneming,
            "eigenaar": eigenaar,
            "rechtspersonen": [],
            "vestigingen": vestigingen,
        }

        return data

    except Exception as e:
        logging.error(f"Error: {type(e)} {e}")
        raise ExtractionError()


def extract_nnp(nnpid: str, xml_str: str):
    tree = BeautifulSoup(xml_str, features="lxml-xml")
    nnps = tree.find_all("object")

    if is_nil(nnps):
        return {}

    nnp = None
    for nnp_item in nnps:
        if nnp_item.find("inn.nnpId", None).string == nnpid:
            nnp = nnp_item

    if is_nil(nnp):
        return {}

    bestuurders = extract_bestuurders(nnp)
    gemachtigden = extract_gemachtigden(nnp)
    overige_functionarissen = extract_overige_functionarissen(nnp)
    aansprakelijken = extract_aansprakelijken(nnp)

    return {
        "gemachtigden": gemachtigden,
        "overigeFunctionarissen": overige_functionarissen,
        "bestuurders": bestuurders,
        "aansprakelijken": aansprakelijken,
    }


def extract_for_kvk(xml_str):
    try:
        tree = BeautifulSoup(xml_str, features="lxml-xml")

        object_data = tree.Body.find("object")
        activiteiten_data = tree.Body.find_all("oefentActiviteitUitIn")
        eigenaren_data = tree.Body.find_all("heeftAlsEigenaar")

        if not object_data:
            return {}

        object_data = extract_basic_info(object_data)
        eigenaren_data = extract_owners(eigenaren_data)
        activiteiten_data = extract_oefent_activiteiten_uit_in(activiteiten_data)

        handelsnamen = set()
        primaire_handelsnamen = None
        ondernemingsactiviteiten = set()
        vestigingen = []
        hoofdactiviteit = None

        for i in activiteiten_data:

            for j in i["activiteiten"]:
                if j["indicatieHoofdactiviteit"]:
                    hoofdactiviteit = j["omschrijving"]
                else:
                    ondernemingsactiviteiten.add(j["omschrijving"])

            if i["typeringVestiging"] == "Hoofdvestiging":
                primaire_handelsnamen = i["handelsnamen"]
            else:
                handelsnamen.update(i["handelsnamen"])

            vestiging = {
                "vestigingsNummer": i["vestigingsNummer"],
                "handelsnamen": i["handelsnamen"],
                "typeringVestiging": i["typeringVestiging"],
                "datumAanvang": i["datumAanvang"],
                "datumEinde": i["datumEinde"],
                "telefoonnummer": i["telefoonnummer"],
                "faxnummer": i["faxnummer"],
                "emailadres": i["emailadres"],
                "websites": i["url"],
                "activiteiten": [j["omschrijving"] for j in i["activiteiten"]],
                "bezoekadres": i["bezoekadres"],
                "postadres": i["postadres"],
            }
            vestigingen.append(vestiging)

        handelsnamen = sorted(list(handelsnamen))

        if primaire_handelsnamen:
            handelsnamen = primaire_handelsnamen + handelsnamen

        rechtsvorm = eigenaren_data[0]["rechtsvorm"]

        onderneming = {
            "datumAanvang": object_data["datumAanvang"],
            "datumEinde": object_data["datumEinde"],
            "handelsnamen": handelsnamen,
            "rechtsvorm": rechtsvorm,
            "overigeActiviteiten": sorted(list(ondernemingsactiviteiten)),
            "hoofdactiviteit": hoofdactiviteit,
        }

        nnpid = None
        eigenaar = None
        rechtspersonen = []

        # Only show natuurlijk persoon as eigenaar for rechtsvorm=Eenmanszaak
        if rechtsvorm == "Eenmanszaak":

            onderneming["kvkNummer"] = object_data["kvkNummer"]

            if eigenaren_data:
                eigenaar_item = eigenaren_data[0]

                eigenaar = {
                    "naam": "%s %s"
                    % (eigenaar_item["voornamen"], eigenaar_item["geslachtsnaam"]),
                    "geboortedatum": eigenaar_item["geboortedatum"],
                    "adres": eigenaar_item["adres"],
                    "bsn": eigenaar_item.get("bsn", None),
                }
        else:

            for eigenaar_item in eigenaren_data:

                rsin = eigenaar_item.get("nnpId", None)

                # NOTE: If there are more than 1 nnp owner with a RSIN, which one should we take?
                if not nnpid and rsin and eigenaar_item["type"] == "nnp":
                    nnpid = rsin

                rechtspersoon = {
                    "kvkNummer": object_data["kvkNummer"],
                    "rsin": rsin,
                    "statutaireNaam": eigenaar_item.get("statutaireNaam", None),
                    "statutaireZetel": eigenaar_item.get("statutaireZetel", None),
                }
                rechtspersonen.append(rechtspersoon)

        is_amsterdammer = False
        for i in vestigingen:
            if i["typeringVestiging"]:
                if (
                    i["bezoekadres"] is not None
                    and i["bezoekadres"]["woonplaatsNaam"] == "Amsterdam"
                ) or (
                    i["postadres"] is not None
                    and i["postadres"]["woonplaatsNaam"] == "Amsterdam"
                ):
                    is_amsterdammer = True

        data = {
            "mokum": is_amsterdammer,
            "nnpid": nnpid,
            "onderneming": onderneming,
            "eigenaar": eigenaar,
            "rechtspersonen": rechtspersonen,
            "vestigingen": vestigingen,
        }

        return data

    except Exception as e:
        logging.error(f"Error: {type(e)} {e}")
        raise ExtractionError()


def get_from_bsn(bsn: str):
    response = _get_response_by_bsn(bsn)
    return extract_for_bsn(response)


def get_from_kvk(kvk_number: str):
    response = _get_response_by_kvk_number(kvk_number)
    return extract_for_kvk(response)


def get_nnp_from_kvk(nnpid: str):
    response = _get_response_by_nnpid(nnpid)
    return extract_nnp(nnpid, response)
