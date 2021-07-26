""" SAML logic

This module interprets and verifies SAML tokens
"""
import os
from tma_saml import (
    get_digi_d_bsn,
    get_e_herkenning_attribs,
    HR_KVK_NUMBER_KEY,
    get_user_type,
)


def get_bsn_from_request(request):
    """
    Get the BSN based on a request, expecting a SAML token in the headers
    """
    # Load the TMA certificate
    tma_certificate = get_tma_certificate()

    # Decode the BSN from the request with the TMA certificate
    bsn = get_digi_d_bsn(request, tma_certificate)
    return bsn


def get_kvk_number_from_request(request):
    """
    Get the KVK number based on a request, expecting a SAML token in the headers
    """
    # Load the TMA certificate
    tma_certificate = get_tma_certificate()

    # Decode the BSN from the request with the TMA certificate
    attribs = get_e_herkenning_attribs(request, tma_certificate)
    kvk_number = attribs[HR_KVK_NUMBER_KEY]
    return kvk_number


def get_type(request):
    type = get_user_type(request, get_tma_certificate())
    return type


def get_tma_certificate():
    return os.getenv("TMA_CERTIFICATE")
