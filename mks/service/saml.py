from base64 import b64decode

from signxml import XMLVerifier

NAMESPACE = '{urn:oasis:names:tc:SAML:2.0:assertion}'
STATEMENT_TAG = f'{NAMESPACE}AttributeStatement'
ATTRIBUTE_TAG = f'{NAMESPACE}Attribute'
ATTR_VALUE_TAG = f'{NAMESPACE}AttributeValue'


class SamlVerificationException(Exception):
    pass


def get_saml_assertion_attributes(saml_xml):
    statement = saml_xml.find(STATEMENT_TAG)
    return {attrib.attrib['Name']: attrib.find(ATTR_VALUE_TAG).text for attrib
            in statement.iter(ATTRIBUTE_TAG)}


def get_verified_data(token, cert):
    return XMLVerifier().verify(b64decode(token), x509_cert=cert).signed_xml


def verify_saml_token_and_retrieve_saml_attribute(saml_token, attribute,
                                                  saml_cert):
    if not saml_token:
        raise SamlVerificationException('Missing SAML token')

    try:
        verified_data = get_verified_data(saml_token, saml_cert)
        saml_attributes = get_saml_assertion_attributes(verified_data)
    except Exception as e:
        raise SamlVerificationException(e)

    if attribute not in saml_attributes:
        raise SamlVerificationException(f"Missing attribute {attribute} "
                                        "in SAML token")

    return saml_attributes[attribute]
