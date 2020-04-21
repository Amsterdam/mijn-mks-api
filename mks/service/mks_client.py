from datetime import datetime
from random import randint

import requests
from lxml import objectify

from mks.model.stuff import StuffReply
from mks.service.config import MKS_CLIENT_CERT, MKS_CLIENT_KEY, MKS_ENDPOINT, BRP_APPLICATIE, BRP_GEBRUIKER
from mks.service.exceptions import NoResultException

# print incoming soap xml when true
log_response = False


def _get_response(mks_brp_url, soap_request):
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'text/xml;charset=UTF-8',
        'SOAPAction': 'http://www.egem.nl/StUF/sector/bg/0310/npsLv01Integraal',
    })
    session.cert = (MKS_CLIENT_CERT, MKS_CLIENT_KEY)
    post_response = session.post(mks_brp_url, data=soap_request)
    return post_response.content


def _get_xml_response(mks_brp_url: str, soap_request: str) -> StuffReply:
    response_content = _get_response(mks_brp_url, soap_request)
    if log_response:
        from io import BytesIO
        from lxml import etree
        content_bytesio = BytesIO(response_content)
        tree = etree.parse(content_bytesio)
        formatted_xml = etree.tostring(tree, pretty_print=True)
        print(formatted_xml.decode())
    reply = StuffReply(
        objectify.fromstring(response_content))  # type: StuffReply

    if not reply.is_valid_response():
        raise NoResultException()

    return reply


def get_response(burgerservicenummer: int):
    return _get_xml_response(
        mks_brp_url=MKS_ENDPOINT,
        soap_request=_get_soap_request(burgerservicenummer)
    ).as_dict()


def _get_soap_request(bsn: int) -> str:
    # Timestamp format example: 2017041911110000
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S') + '00'
    applicatie = BRP_APPLICATIE
    gebruiker = BRP_GEBRUIKER
    ref = str(randint(100000, 999999))

    referentienummer = \
        f'MijnAmsterdam||{ref}'

    return f'''
<soapenv:Envelope
           xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
           xmlns:ns="http://www.egem.nl/StUF/sector/bg/0310"
           xmlns:stuf="http://www.egem.nl/StUF/StUF0301">
           <soapenv:Header/>
           <soapenv:Body>
           <ns:npsLv01>
           <ns:stuurgegevens>
           <stuf:berichtcode>Lv01</stuf:berichtcode>
           <stuf:zender>
           <stuf:applicatie>{applicatie}</stuf:applicatie>
           <stuf:gebruiker>{gebruiker}</stuf:gebruiker>
           </stuf:zender>
           <stuf:ontvanger>
           <stuf:organisatie>Amsterdam</stuf:organisatie>
           <stuf:applicatie>CGM</stuf:applicatie>
           </stuf:ontvanger>
           <stuf:referentienummer>{referentienummer}</stuf:referentienummer>
           <stuf:tijdstipBericht>{timestamp}</stuf:tijdstipBericht>
           <stuf:entiteittype>NPS</stuf:entiteittype>
           </ns:stuurgegevens>
           <ns:parameters>
           <stuf:sortering>07</stuf:sortering>
           <stuf:indicatorVervolgvraag>false</stuf:indicatorVervolgvraag>
           <stuf:maximumAantal>1</stuf:maximumAantal>
           <stuf:indicatorAfnemerIndicatie>
           false
           </stuf:indicatorAfnemerIndicatie>
           <stuf:indicatorAantal>false</stuf:indicatorAantal>
           </ns:parameters>
           <ns:gelijk stuf:entiteittype="NPS">
           <ns:inp.bsn>{bsn}</ns:inp.bsn>
           </ns:gelijk>
           <ns:scope>
           <ns:object stuf:entiteittype="NPS" stuf:scope="alles"/>
           </ns:scope>
           </ns:npsLv01>
           </soapenv:Body>
           </soapenv:Envelope>
'''
