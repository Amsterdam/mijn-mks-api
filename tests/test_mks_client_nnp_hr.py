import os
from datetime import date

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
NNP_RESPONSE_PATH = os.path.join(FIXTURE_PATH, "hr_nnp_response.xml")

NNP_HR_RESPONSE = {
    'gemachtigden': [{
        'functie': 'Gevolmachtigde',
        'naam': 'Joppie Wappie Jarmander',
        'geboortedatum': None,
        'datumIngangMachtiging': None,
    }],
    'overigeFunctionarissen': [
        {
            'functie': 'Commissaris',
            'naam': 'Georges Rudy Janssen van Son',
            'geboortedatum': date(1976, 10, 1),
        },
        {
            'functie': 'Commissaris',
            'naam': 'Jan Jansen',
            'geboortedatum': date(1976, 10, 1)
        },
        {
            'functie': 'Commissaris',
            'naam': 'Boris Johnsson',
            'geboortedatum': date(1976, 10, 1)
        },
        {
            'functie': 'Enig aandeelhouder',
            'naam': 'Kamlawatie Katar',
            'geboortedatum': date(1976, 10, 1)
        },
    ],
    'bestuurders': [
        {
            'functie': 'Bestuurder',
            'soortBevoegdheid': 'AlleenZelfstandigBevoegd',
            'naam': 'Wesley Vlag',
            'geboortedatum': date(1976, 10, 1),
        },
        {
            'functie': 'Bestuurder',
            'soortBevoegdheid': 'AlleenZelfstandigBevoegd',
            'naam': 'Hendrika Johanna Theodora Grupstal',
            'geboortedatum': date(1976, 10, 1),
        },
        {
            'functie': 'Bestuurder',
            'soortBevoegdheid': 'AlleenZelfstandigBevoegd',
            'naam': 'Pierre Vlag',
            'geboortedatum': date(1976, 10, 1),
        },
        {
            'functie': 'Bestuurder',
            'soortBevoegdheid': 'AlleenZelfstandigBevoegd',
            'naam': 'Dennis Uiersin',
            'geboortedatum': date(1976, 10, 1),
        },
    ],
    'aansprakelijken': [
        {
            'functie': 'Vennoot',
            'geboortedatum': '1992-11-21',
            'naam': 'Cammie Konopka',
            'soortBevoegdheid': 'BeperktBevoegd'
        }
    ],
}


def get_nnp_xml_response_fixture(*args):
    with open(NNP_RESPONSE_PATH, 'rb') as response_file:
        return response_file.read().decode('utf-8')
