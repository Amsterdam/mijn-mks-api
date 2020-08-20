import logging
import os
from datetime import datetime
from io import BytesIO
from random import randint
import time

import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from lxml import etree

from mks.model.stuf_3_10_hr import extract_data_is_eigenaar_van
from mks.service.config import MKS_CLIENT_CERT, MKS_CLIENT_KEY, BRP_APPLICATIE, BRP_GEBRUIKER, PROJECT_DIR, \
    MKS_ENDPOINT, REQUEST_TIMEOUT
from mks.service.exceptions import ExtractionError

BSN_HR_TEMPLATE_PATH = os.path.join(PROJECT_DIR, "HR.xml.jinja2")
with open(BSN_HR_TEMPLATE_PATH) as fp:
    bsn_hr_template = Template(fp.read())

log_response = False


def _get_soap_request(bsn: str = None, kvk_nummer: str = None):
    ref = str(randint(100000, 999999))

    referentienummer = f'MijnAmsterdam||{ref}'
    context = {
        "applicatie": BRP_APPLICATIE,
        "gebruiker": BRP_GEBRUIKER,
        "referentienummer": referentienummer,
        "timestamp": datetime.now().strftime('%Y%m%d%H%M%S') + '00'
    }
    if bsn:
        context['bsn'] = bsn
    if kvk_nummer:
        context['kvk_nummer'] = kvk_nummer

    return bsn_hr_template.render(context)


def _get_response(mks_url, soap_request):
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'text/xml;charset=UTF-8',
        # 'SOAPAction': 'http://www.egem.nl/StUF/sector/bg/0204/beantwoordSynchroneVraagIntegraal',
    })
    session.cert = (MKS_CLIENT_CERT, MKS_CLIENT_KEY)
    request_start = time.time()
    try:
        post_response = session.post(mks_url, data=soap_request, timeout=REQUEST_TIMEOUT)
    finally:
        request_end = time.time()
        logging.info(f"request took: '{request_end - request_start}' seconds")

    return post_response.content


def get_from_bsn(bsn: str):
    soap_request = _get_soap_request(bsn)
    response = _get_response(MKS_ENDPOINT, soap_request)

    if log_response:
        content_bytesio = BytesIO(response)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())

    return extract(response)


def get_from_kvk(kvk_nummer: str):
    soap_request = _get_soap_request(kvk_nummer)
    response = _get_response(MKS_ENDPOINT, soap_request)

    if log_response:
        content_bytesio = BytesIO(response)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())

    return extract(response)



def extract(xml_data):
    try:
        tree = BeautifulSoup(xml_data, features='lxml-xml')
        hr_data = tree.Body.find_all('rps.isEigenaarVan')
        data = extract_data_is_eigenaar_van(hr_data)
        return data
    except Exception as e:
        logging.error(f"Error: {type(e)} {e}")
        raise ExtractionError()
