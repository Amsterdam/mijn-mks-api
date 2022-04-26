import logging
import os
from datetime import datetime
from random import randint

import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from app.helpers import get_request_template
from app.model.stuf_02_04 import extract_data
from app.config import (
    MKS_CLIENT_CERT,
    MKS_CLIENT_KEY,
    BRP_APPLICATIE,
    BRP_GEBRUIKER,
    MKS_ENDPOINT,
    REQUEST_TIMEOUT,
)
from app.service.exceptions import ExtractionError, NoResultException

prs_stuf_0204_template = get_request_template("PRS_stuf02.04.xml")


def _get_soap_request_payload(bsn: str) -> str:
    ref = str(randint(100000, 999999))

    referentienummer = f"MijnAmsterdam||{ref}"
    context = {
        "bsn": bsn,
        "applicatie": BRP_APPLICATIE,
        "gebruiker": BRP_GEBRUIKER,
        "referentienummer": referentienummer,
        "timestamp": datetime.now().strftime("%Y%m%d%H%M%S") + "00",
    }
    return prs_stuf_0204_template.render(context)


def _get_response(mks_brp_url, soap_request_payload):
    session = requests.Session()
    session.headers.update(
        {
            "Content-Type": "text/xml;charset=UTF-8",
            "SOAPAction": "http://www.egem.nl/StUF/sector/bg/0204/beantwoordSynchroneVraagIntegraal",
        }
    )
    session.cert = (MKS_CLIENT_CERT, MKS_CLIENT_KEY)

    post_response = session.post(
        mks_brp_url, data=soap_request_payload, timeout=REQUEST_TIMEOUT
    )

    return post_response.content


def extract(xml_data):
    try:
        tree = BeautifulSoup(xml_data, features="lxml-xml")
        if tree.find("Body") is None:
            logging.error("No Body tag. no data for person")
            raise NoResultException()
        person = tree.Body.PRS
        data = extract_data(person)
        data["crossRefNummer"] = tree.find("crossRefNummer").text
        return data
    except Exception as e:
        logging.error(f"Error: {type(e)} {e}")
        raise ExtractionError()


def get_0204(bsn: str):
    response = get_0204_raw(bsn)

    return extract(response)


def get_0204_raw(bsn: str, as_xml: bool = False):
    soap_request_payload = _get_soap_request_payload(bsn)
    response = _get_response(
        f"{MKS_ENDPOINT}/CGS/StUF/services/BGSynchroon", soap_request_payload
    )

    return response
