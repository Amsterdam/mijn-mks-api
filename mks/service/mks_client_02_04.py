
import asyncio
import os
from datetime import datetime
from io import BytesIO

import httpx
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
    context = {
        "bsn": bsn,
        "applicatie": BRP_APPLICATIE,
        "gebruiker": BRP_GEBRUIKER,
        "referentienummer": "test2",
        "timestamp": datetime.now().strftime('%Y%m%d%H%M%S') + '00'
    }
    return stuf_0204_template.render(context)


async def _get_response(mks_brp_url, soap_request):
    headers = {
        'Content-Type': 'text/xml;charset=UTF-8',
        'SOAPAction': 'http://www.egem.nl/StUF/sector/bg/0310/npsLv01Integraal',
    }
    cert = (MKS_CLIENT_CERT, MKS_CLIENT_KEY)
    async with httpx.AsyncClient(cert=cert, timeout=20) as client:
        post_response = await client.post(
            "https://mks01.acc.amsterdam.nl:8443/CGS/StUF/services/BGSynchroon",
            data=soap_request,
            headers=headers)
        return post_response


def extract(xml_data):
    tree = BeautifulSoup(xml_data, features='lxml-xml')
    person = tree.Body.PRS
    data = extract_data(person)
    return data


def get_0204(bsn: str):
    # print("start 204")
    soap_request = _get_soap_request(bsn)
    response = await _get_response(MKS_ENDPOINT, soap_request)

    # print("end 204")
    if log_response:
        content_bytesio = BytesIO(response.content)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())
    # return post_response.content

    return extract(response.content)


# async def a():
#     await asyncio.gather(get_0204("307741837"))
# await a()
