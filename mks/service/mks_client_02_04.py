import logging
import os
from datetime import datetime
from io import BytesIO
from random import randint

import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from lxml import etree
from prometheus_client import Histogram

from mks.model.stuf_02_04 import extract_data
from mks.prometheus_definitions import mks_connection_state
from mks.service.config import MKS_CLIENT_CERT, MKS_CLIENT_KEY, BRP_APPLICATIE, BRP_GEBRUIKER, PROJECT_DIR, \
    MKS_ENDPOINT, REQUEST_TIMEOUT
from mks.service.exceptions import ExtractionError, NoResultException

PRS_STUF0204TEMPLATE_PATH = os.path.join(PROJECT_DIR, "PRS_stuf02.04.xml.jinja2")
with open(PRS_STUF0204TEMPLATE_PATH) as fp:
    prs_stuf_0204_template = Template(fp.read())

log_response = False


def _get_soap_request(bsn: str) -> str:
    ref = str(randint(100000, 999999))

    referentienummer = f'MijnAmsterdam||{ref}'
    context = {
        "bsn": bsn,
        "applicatie": BRP_APPLICATIE,
        "gebruiker": BRP_GEBRUIKER,
        "referentienummer": referentienummer,
        "timestamp": datetime.now().strftime('%Y%m%d%H%M%S') + '00'
    }
    return prs_stuf_0204_template.render(context)


mks_request_latency = Histogram('mks_request_latency_seconds', 'Mks request time')


def _get_response(mks_brp_url, soap_request):
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'text/xml;charset=UTF-8',
        'SOAPAction': 'http://www.egem.nl/StUF/sector/bg/0204/beantwoordSynchroneVraagIntegraal',
    })
    session.cert = (MKS_CLIENT_CERT, MKS_CLIENT_KEY)

    with mks_request_latency.time():
        post_response = session.post(mks_brp_url, data=soap_request, timeout=REQUEST_TIMEOUT)

    mks_connection_state.set(0)  # success, mark state as running
    return post_response.content


def extract(xml_data):
    try:
        tree = BeautifulSoup(xml_data, features='lxml-xml')
        if tree.find('Body') is None:
            logging.error("No Body tag. no data for person")
            raise NoResultException()
        person = tree.Body.PRS
        data = extract_data(person)
        data['crossRefNummer'] = tree.find('crossRefNummer').text
        return data
    except Exception as e:
        logging.error(f"Error: {type(e)} {e}")
        raise ExtractionError()


def get_0204(bsn: str):
    response = get_0204_raw(bsn)

    return extract(response)


def get_0204_raw(bsn: str):
    soap_request = _get_soap_request(bsn)
    response = _get_response(f'{MKS_ENDPOINT}/CGS/StUF/services/BGSynchroon', soap_request)

    if log_response:
        content_bytesio = BytesIO(response)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())

    return response
