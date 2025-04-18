import logging
import os
import time
from datetime import datetime
from random import randint

import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from app.helpers import get_request_template
from app.model.adr_stuf_02_04 import extract_data
from app.config import (
    MKS_CLIENT_CERT,
    MKS_CLIENT_KEY,
    BRP_APPLICATIE,
    BRP_GEBRUIKER,
    PROJECT_DIR,
    MKS_ENDPOINT,
    REQUEST_TIMEOUT,
)


adr_stuf_0204_template = get_request_template("ADR_stuf02.04.xml")


def _get_soap_request_payload(adres_sleutel: str) -> str:
    ref = str(randint(100000, 999999))

    referentienummer = f"MijnAmsterdam||{ref}"
    context = {
        "adres_sleutel": adres_sleutel,
        "applicatie": BRP_APPLICATIE,
        "gebruiker": BRP_GEBRUIKER,
        "referentienummer": referentienummer,
        "timestamp": datetime.now().strftime("%Y%m%d%H%M%S") + "00",
    }
    return adr_stuf_0204_template.render(context)


def _get_response(mks_brp_url, soap_request_payload):
    session = requests.Session()
    session.headers.update(
        {
            "Content-Type": "text/xml;charset=UTF-8",
            "SOAPAction": "http://www.egem.nl/StUF/sector/bg/0204/beantwoordSynchroneVraag",
        }
    )

    session.cert = (MKS_CLIENT_CERT, MKS_CLIENT_KEY)
    request_start = time.time()
    try:
        post_response = session.post(
            mks_brp_url, data=soap_request_payload, timeout=REQUEST_TIMEOUT
        )
    finally:
        request_end = time.time()
        logging.info(f"request took: '{request_end - request_start}' seconds")

    return post_response.content


def extract(xml_data):
    tree = BeautifulSoup(xml_data, features="lxml-xml")
    adr = tree.Body.ADR

    if not adr:
        return None

    data = extract_data(adr)

    if data:
        data["crossRefNummer"] = tree.find("crossRefNummer").text

    return data


def get_resident_count(adres_sleutel: str):
    soap_request_payload = _get_soap_request_payload(adres_sleutel)

    response = _get_response(
        f"{MKS_ENDPOINT}/CGS/StUF/services/BGSynchroon", soap_request_payload
    )

    return extract(response)
