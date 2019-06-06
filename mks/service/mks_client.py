from _datetime import datetime
from random import randint

import requests
from lxml import objectify

from mks.model.stuff import StuffReply
from mks.service.config import MKS_CLIENT_CERT, MKS_CLIENT_KEY, MKS_ENDPOINT, BRP_APPLICATIE, BRP_GEBRUIKER
from mks.service.exceptions import NoResultException

# print incoming soap xml when true
log_response = False


def _get_xml_response(mks_brp_url: str, soap_request: str) -> StuffReply:
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'text/xml;charset=UTF-8',
        'SOAPAction': 'http://www.egem.nl/StUF/sector/bg/0310/npsLv01Integraal',
    })
    session.cert = (MKS_CLIENT_CERT, MKS_CLIENT_KEY)
    post_response = session.post(mks_brp_url, data=soap_request)
    response_content = post_response.content
    if log_response:
        print(response_content)
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
    ref = '%s' % (randint(100000, 999999))

    referentienummer = \
        f'MijnAmsterdam||{ref}'

    return f'<soapenv:Envelope ' \
           f'xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" ' \
           f'xmlns:ns="http://www.egem.nl/StUF/sector/bg/0310" ' \
           f'xmlns:stuf="http://www.egem.nl/StUF/StUF0301">' \
           f'<soapenv:Header/>' \
           f'<soapenv:Body>' \
           f'<ns:npsLv01>' \
           f'<ns:stuurgegevens>' \
           f'<stuf:berichtcode>Lv01</stuf:berichtcode>' \
           f'<stuf:zender>' \
           f'<stuf:applicatie>{applicatie}</stuf:applicatie>' \
           f'<stuf:gebruiker>{gebruiker}</stuf:gebruiker>' \
           f'</stuf:zender>' \
           f'<stuf:ontvanger>' \
           f'<stuf:organisatie>Amsterdam</stuf:organisatie>' \
           f'<stuf:applicatie>CGM</stuf:applicatie>' \
           f'</stuf:ontvanger>' \
           f'<stuf:referentienummer>{referentienummer}</stuf:referentienummer>' \
           f'<stuf:tijdstipBericht>{timestamp}</stuf:tijdstipBericht>' \
           f'<stuf:entiteittype>NPS</stuf:entiteittype>' \
           f'</ns:stuurgegevens>' \
           f'<ns:parameters>' \
           f'<stuf:sortering>07</stuf:sortering>' \
           f'<stuf:indicatorVervolgvraag>false</stuf:indicatorVervolgvraag>' \
           f'<stuf:maximumAantal>1</stuf:maximumAantal>' \
           f'<stuf:indicatorAfnemerIndicatie>' \
           f'false' \
           f'</stuf:indicatorAfnemerIndicatie>' \
           f'<stuf:indicatorAantal>false</stuf:indicatorAantal>' \
           f'</ns:parameters>' \
           f'<ns:gelijk stuf:entiteittype="NPS">' \
           f'<ns:inp.bsn>{bsn}</ns:inp.bsn>' \
           f'</ns:gelijk>' \
           f'<ns:scope>' \
           f'<ns:object stuf:entiteittype="NPS" stuf:scope="alles"/>' \
           f'</ns:scope>' \
           f'</ns:npsLv01>' \
           f'</soapenv:Body>' \
           f'</soapenv:Envelope>'
