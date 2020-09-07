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

from mks.model.stuf_3_10_hr import extract_data_is_eigenaar_van, extract_oefent_activiteiten_uit_in, extract_owners, \
    extract_basic_info, extract_owner_persoon
from mks.service.config import MKS_CLIENT_CERT, MKS_CLIENT_KEY, BRP_APPLICATIE, BRP_GEBRUIKER, PROJECT_DIR, \
    MKS_ENDPOINT, REQUEST_TIMEOUT
from mks.service.exceptions import ExtractionError

BSN_HR_TEMPLATE_PATH = os.path.join(PROJECT_DIR, "HR.xml.jinja2")
with open(BSN_HR_TEMPLATE_PATH) as fp:
    bsn_hr_template = Template(fp.read())

log_response = False


def _get_soap_request(bsn: str = None, kvk_number: str = None):
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
    if kvk_number:
        context['kvk_nummer'] = kvk_number

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
    soap_request = _get_soap_request(bsn=bsn)
    response = _get_response(MKS_ENDPOINT, soap_request)

    if log_response:
        content_bytesio = BytesIO(response)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())

    return extract_for_bsn(response)


def extract_for_bsn(xml_data):
    try:
        tree = BeautifulSoup(xml_data, features='lxml-xml')

        is_amsterdammer = True  # TODO: fill me

        onderneming = tree.Body.find('rps.isEigenaarVan')
        activiteiten = tree.Body.find_all('oefentActiviteitUitIn')
        eigenaren = tree.Body.find('object')

        data = {
            'mokum': is_amsterdammer,
            'onderneming': extract_basic_info(onderneming),
            'rechtspersonen': [extract_owner_persoon(eigenaren)],
            'vestigingen': extract_oefent_activiteiten_uit_in(activiteiten),
            'aandeelhouders': [],
            'bestuurders': [],
        }

        return data

        # hr_data = tree.Body.find_all('rps.isEigenaarVan')
        # data = extract_data_is_eigenaar_van(hr_data)
        # return data
    except Exception as e:
        logging.error(f"Error: {type(e)} {e}")
        raise ExtractionError()


def get_from_kvk(kvk_number: str):
    soap_request = _get_soap_request(kvk_number=kvk_number)
    response = _get_response(MKS_ENDPOINT, soap_request)

    if log_response:
        content_bytesio = BytesIO(response)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())

    return extract_for_kvk(response)


def extract_for_kvk(xml_str):
    try:
        tree = BeautifulSoup(xml_str, features='lxml-xml')

        is_amsterdammer = True  # TODO: fill me

        onderneming = tree.Body.find('object')
        activiteiten = tree.Body.find_all('oefentActiviteitUitIn')
        eigenaren = tree.Body.find_all('heeftAlsEigenaar')

        data = {
            'mokum': is_amsterdammer,
            'onderneming': extract_basic_info(onderneming),
            'rechtspersonen': extract_owners(eigenaren),
            'vestigingen': extract_oefent_activiteiten_uit_in(activiteiten),
            'aandeelhouders': [],
            'bestuurders': [],
        }

        return data


    except Exception as e:
        logging.error(f"Error: {type(e)} {e}")
        raise ExtractionError()

# def extract_for_kvk(xml_data):
#     try:
#         tree = BeautifulSoup(xml_data, features='lxml-xml')
#         activiteiten = tree.Body.find_all('oefentActiviteitUitIn')
#         eigenaren = tree.Body.find_all('heeftAlsEigenaar')
#         return {
#             'activiteiten': extract_oefent_activiteiten_uit_in(activiteiten),
#             'eigenaren': extract_owners(eigenaren)
#         }
#     except Exception as e:
#         logging.error(f"Error: {type(e)} {e}")
#         raise ExtractionError()
#
