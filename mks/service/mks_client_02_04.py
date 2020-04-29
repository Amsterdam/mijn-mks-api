
import asyncio
import os
from datetime import datetime
from io import BytesIO
from random import randint

import httpx
import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from lxml import etree

from mks.model.stuf_02_04 import extract_data
from mks.service.config import MKS_CLIENT_CERT, MKS_CLIENT_KEY, BRP_APPLICATIE, BRP_GEBRUIKER, PROJECT_DIR, MKS_ENDPOINT

STUF0204TEMPLATE_PATH = os.path.join(PROJECT_DIR, "stuf02.04.xml.jinja2")
with open(STUF0204TEMPLATE_PATH) as fp:
    stuf_0204_template = Template(fp.read())


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
    return stuf_0204_template.render(context)


def _get_response(mks_brp_url, soap_request):
    print("get response!!!!!!!!!!!!!!!!!!!")
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'text/xml;charset=UTF-8',
    })
    session.cert = (MKS_CLIENT_CERT, MKS_CLIENT_KEY)
    post_response = session.post(mks_brp_url, data=soap_request)
    return post_response.content


def extract(xml_data):
    tree = BeautifulSoup(xml_data, features='lxml-xml')
    person = tree.Body.PRS
    data = extract_data(person)
    return data


def get_0204(bsn: str):
    soap_request = _get_soap_request(bsn)
    response = _get_response(MKS_ENDPOINT, soap_request)

    if log_response:
        content_bytesio = BytesIO(response)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())

    return extract(response)
