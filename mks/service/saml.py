""" SAML logic

This module interprets and verifies SAML tokens
"""
import os
from tma_saml import get_digi_d_bsn


def get_bsn_from_request(request):
    """
    Get the BSN based on a request, expecting a SAML token in the headers
    """
    # Load the TMA certificate
    tma_certificate = get_tma_certificate()

    # Decode the BSN from the request with the TMA certificate
    bsn = get_digi_d_bsn(request, tma_certificate)
    return bsn


def get_tma_certificate():
    return os.getenv('TMA_CERTIFICATE')
