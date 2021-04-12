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

from mks.model.stuf_3_10_hr import extract_oefent_activiteiten_uit_in, extract_owners, \
    extract_basic_info, extract_owner_persoon
from mks.model.stuf_utils import is_nil
from mks.service.config import MKS_CLIENT_CERT, MKS_CLIENT_KEY, BRP_APPLICATIE, BRP_GEBRUIKER, PROJECT_DIR, \
    MKS_ENDPOINT, REQUEST_TIMEOUT
from mks.service.exceptions import ExtractionError, NoResultException

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
    response = _get_from_mks(bsn=bsn)
    return extract_for_bsn(response)


def get_from_kvk(kvk_number: str):
    response = _get_from_mks(kvk_number=kvk_number)
    return extract_for_kvk(response)


def extract_for_bsn(xml_data):
    try:
        tree = BeautifulSoup(xml_data, features='lxml-xml')

        if tree.find('Body') is None:
            raise NoResultException()

        object_data = tree.Body.find('rps.isEigenaarVan')
        activiteiten = tree.Body.find_all('oefentActiviteitUitIn')
        eigenaren = tree.Body.find('object')

        if is_nil(object_data):
            return {}

        object_data = extract_basic_info(object_data)
        eigenaren_data = [extract_owner_persoon(eigenaren)]
        activiteiten_data = extract_oefent_activiteiten_uit_in(activiteiten)

        handelsnamen = set()
        ondernemingsactiviteiten = set()
        vestigingen = []
        hoofdactiviteit = None

        for i in activiteiten_data:
            handelsnamen.update(i['handelsnamen'])
            for j in i['activiteiten']:
                if j['indicatieHoofdactiviteit']:
                    hoofdactiviteit = j['omschrijving']
                else:
                    ondernemingsactiviteiten.add(j['omschrijving'])

            vestiging = {
                'vestigingsNummer': i['vestigingsNummer'],
                'handelsnamen': i['handelsnamen'],
                'typeringVestiging': i['typeringVestiging'],
                'datumAanvang': i['datumAanvang'],
                'datumEinde': i['datumEinde'],
                'telefoonnummer': i['telefoonnummer'],
                'faxnummer': i['faxnummer'],
                'emailadres': i['emailadres'],
                'websites': i['url'],
                'activiteiten': [j['omschrijving'] for j in i['activiteiten']],
                'bezoekadres': i['bezoekadres'],
                'postadres': i['postadres'],
            }
            vestigingen.append(vestiging)

        handelsnamen = sorted(list(handelsnamen))

        rechtsvorm = eigenaren_data[0]['rechtsvorm']
        # if not rechtsvorm:
        #     rechtsvorm = "Eenmanszaak"

        onderneming = {
            'datumAanvang': object_data['datumAanvang'],
            'datumEinde': object_data['datumEinde'],
            'handelsnamen': handelsnamen,
            'rechtsvorm': rechtsvorm,
            'overigeActiviteiten': sorted(list(ondernemingsactiviteiten)),
            'hoofdactiviteit': hoofdactiviteit
        }

        rechtspersonen = []
        for i in eigenaren_data:
            persoon = {
                'kvkNummer': object_data['kvkNummer'],
                'rsin': i.get('nnpId', None),
                'bsn': eigenaren_data[0].get('bsn', None),
                'statutaireNaam': i.get('statutaireNaam', None),
                'statutaireZetel': i.get('statutaireZetel', None),
            }
            rechtspersonen.append(persoon)

        eigenaar = None

        is_amsterdammer = False
        for i in vestigingen:
            if i['typeringVestiging']:
                if ((i['bezoekadres'] and i['bezoekadres']['woonplaatsNaam'] == "Amsterdam") or
                        (i['postadres'] and i['postadres']['woonplaatsNaam'] == "Amsterdam")):
                    is_amsterdammer = True

        bestuurders = []
        gemachtigden = []
        functionarissen = []

        data = {
            'mokum': is_amsterdammer,
            'onderneming': onderneming,
            'eigenaar': eigenaar,
            'rechtspersonen': rechtspersonen,
            'vestigingen': vestigingen,
            'bestuurders': bestuurders,
            'gemachtigden': gemachtigden,
            'functionarissen': functionarissen,
        }

        return data

    except Exception as e:
        logging.error(f"Error: {type(e)} {e}")
        raise ExtractionError()


def _get_from_mks(**kwargs):
    # kwargs are: kvk_number or bsn
    soap_request = _get_soap_request(**kwargs)

    response = _get_response(f'{MKS_ENDPOINT}/CGS/StUF/0301/BG/0310/services/BeantwoordVraag', soap_request)

    if log_response:
        content_bytesio = BytesIO(response)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())

    return response


def extract_for_kvk(xml_str):
    try:
        tree = BeautifulSoup(xml_str, features='lxml-xml')

        object_data = tree.Body.find('object')
        activiteiten_data = tree.Body.find_all('oefentActiviteitUitIn')
        eigenaren_data = tree.Body.find_all('heeftAlsEigenaar')

        if not object_data:
            return {}

        object_data = extract_basic_info(object_data)
        eigenaren_data = extract_owners(eigenaren_data)
        activiteiten_data = extract_oefent_activiteiten_uit_in(activiteiten_data)

        handelsnamen = set()
        ondernemingsactiviteiten = set()
        vestigingen = []
        hoofdactiviteit = None

        for i in activiteiten_data:
            handelsnamen.update(i['handelsnamen'])
            for j in i['activiteiten']:
                if j['indicatieHoofdactiviteit']:
                    hoofdactiviteit = j['omschrijving']
                else:
                    ondernemingsactiviteiten.add(j['omschrijving'])

            vestiging = {
                'vestigingsNummer': i['vestigingsNummer'],
                'handelsnamen': i['handelsnamen'],
                'typeringVestiging': i['typeringVestiging'],
                'datumAanvang': i['datumAanvang'],
                'datumEinde': i['datumEinde'],
                'telefoonnummer': i['telefoonnummer'],
                'faxnummer': i['faxnummer'],
                'emailadres': i['emailadres'],
                'websites': i['url'],
                'activiteiten': [j['omschrijving'] for j in i['activiteiten']],
                'bezoekadres': i['bezoekadres'],
                'postadres': i['postadres'],
            }
            vestigingen.append(vestiging)
        handelsnamen = sorted(list(handelsnamen))

        rechtsvorm = eigenaren_data[0]['rechtsvorm']

        onderneming = {
            'datumAanvang': object_data['datumAanvang'],
            'datumEinde': object_data['datumEinde'],
            'handelsnamen': handelsnamen,
            'rechtsvorm': rechtsvorm,
            'overigeActiviteiten': sorted(list(ondernemingsactiviteiten)),
            'hoofdactiviteit': hoofdactiviteit
        }

        rechtspersonen = []
        for i in eigenaren_data:
            persoon = {
                'kvkNummer': object_data['kvkNummer'],
                'rsin': i.get('nnpId', None),
                'bsn': i.get('bsn', None),
                'statutaireNaam': i.get('statutaireNaam', None),
                'statutaireZetel': i.get('statutaireZetel', None),
            }
            rechtspersonen.append(persoon)

        is_amsterdammer = False
        for i in vestigingen:
            if i['typeringVestiging']:
                if (i['bezoekadres']['woonplaatsNaam'] == "Amsterdam" or i['postadres']['woonplaatsNaam'] == "Amsterdam"):
                    is_amsterdammer = True

        data = {
            'mokum': is_amsterdammer,
            'onderneming': onderneming,
            'rechtspersonen': rechtspersonen,
            'vestigingen': vestigingen,
            'aandeelhouders': [],
            'bestuurders': [],
        }

        return data

    except Exception as e:
        logging.error(f"Error: {type(e)} {e}")
        raise ExtractionError()
