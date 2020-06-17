import logging
from collections import defaultdict
from datetime import datetime
from hashlib import sha256

from bs4 import Tag

from mks.model.gba import lookup_prsidb_soort_code, lookup_geslacht, lookup_gemeenten, lookup_landen
from mks.model.stuf_utils import _set_value_on, to_string, to_date, to_bool, to_is_amsterdam, to_int, set_fields, \
    set_extra_fields, as_postcode


def get_nationaliteiten(nationaliteiten: Tag):
    result = []

    fields = [
        {'name': 'omschrijving', 'parser': to_string},
        {'name': 'code', 'parser': to_int},
    ]

    for nat in nationaliteiten:
        nationaliteit = {}
        set_fields(nat, fields, nationaliteit)
        result.append(nationaliteit)

    # For people not living in Amsterdam we dont get the omschrijving.
    # Quick fix for Nederlandse if code == 1
    for n in result:
        if not n['omschrijving']:
            if n['code'] == 1:
                n['omschrijving'] = "Nederlandse"

    return result


def extract_persoon_data(persoon_tree: Tag):
    result = {}

    prs_fields = [
        {'name': 'bsn-nummer', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string},
        {'name': 'codeGemeenteVanInschrijving', 'parser': to_int},
        {'name': 'codeGemeenteVanInschrijving', 'parser': to_is_amsterdam, 'save_as': 'mokum'},
        {'name': 'geboorteplaats', 'parser': to_string},
        {'name': 'codeGeboorteland', 'parser': to_string, 'save_as': 'geboorteLand'},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'codeLandEmigratie', 'parser': to_int},
        {'name': 'datumVertrekUitNederland', 'parser': to_date},
        {'name': 'indicatieGeheim', 'parser': to_bool},
    ]

    prs_extra_fields = [
        {'name': 'aanduidingNaamgebruikOmschrijving', 'parser': to_string},
        {'name': 'geboortelandnaam', 'parser': to_string},
        {'name': 'geboorteplaatsnaam', 'parser': to_string},
        {'name': 'gemeentenaamInschrijving', 'parser': to_string},
        {'name': 'omschrijvingBurgerlijkeStaat', 'parser': to_string},
        {'name': 'omschrijvingGeslachtsaanduiding', 'parser': to_string},
        {'name': 'omschrijvingIndicatieGeheim', 'parser': to_string},
        {'name': 'opgemaakteNaam', 'parser': to_string},
        {'name': 'omschrijvingAdellijkeTitel', 'parser': to_string},
    ]

    set_fields(persoon_tree, prs_fields, result)
    set_extra_fields(persoon_tree.extraElementen, prs_extra_fields, result)

    opgemaakte_naam(result)

    # vertrokken onbekend waarheen
    result['vertrokkenOnbekendWaarheen'] = False
    # if result['mokum']:
    #     if result['codeLandEmigratie'] == 0 and result['codeGemeenteVanInschrijving'] == 1999:
    #         result['vertrokkenOnbekendWaarheen'] = True

    result['nationaliteiten'] = get_nationaliteiten(persoon_tree.find_all('NAT'))

    set_omschrijving_geslachtsaanduiding(result)
    set_geboorteLandnaam(result)
    set_geboorteplaatsNaam(result)

    return result


def extract_kinderen_data(persoon_tree: Tag):
    result = []

    knd_fields = [
        {'name': 'bsn-nummer', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
        {'name': 'geboorteplaats', 'parser': to_string},
        {'name': 'codeGeboorteland', 'parser': to_string, 'save_as': 'geboorteLand'},
        {'name': 'datumOverlijden', 'parser': to_date, 'save_as': 'overlijdensdatum'},  # Save as name to match 3.10
        {'name': 'adellijkeTitelPredikaat', 'parser': to_string},
    ]

    knd_extra_fields = [
        {'name': 'omschrijvingAdellijkeTitel', 'parser': to_string},
        {'name': 'geboortelandnaam', 'parser': to_string},
        {'name': 'geboorteplaatsnaam', 'parser': to_string},
        {'name': 'omschrijvingGeslachtsaanduiding', 'parser': to_string},
        {'name': 'opgemaakteNaam', 'parser': to_string},
    ]

    kinderen = persoon_tree.find_all('PRSPRSKND')
    if kinderen[0].get("xsi:nil") == 'true':
        return []

    for kind in kinderen:
        result_kind = {}
        set_fields(kind.PRS, knd_fields, result_kind)
        set_extra_fields(kind.PRS, knd_extra_fields, result_kind)

        set_omschrijving_geslachtsaanduiding(result_kind)
        set_geboorteLandnaam(result_kind)
        set_geboorteplaatsNaam(result_kind)

        result.append(result_kind)

    result.sort(key=lambda x: x['geboortedatum'] or datetime.min)

    return result


def extract_parents_data(persoon_tree: Tag):
    result = []

    parent_fields = [
        {'name': 'bsn-nummer', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
        {'name': 'geboorteplaats', 'parser': to_string},
        {'name': 'codeGeboorteland', 'parser': to_string, 'save_as': 'geboorteLand'},  # save as to match 3.10
        {'name': 'datumOverlijden', 'parser': to_date, 'save_as': 'overlijdensdatum'},  # save as to match 3.10'
        {'name': 'adellijkeTitelPredikaat', 'parser': to_string},
    ]

    parent_extra_fields = [
        {'name': 'omschrijvingAdellijkeTitel', 'parser': to_string},
        {'name': 'geboortelandnaam', 'parser': to_string},
        {'name': 'geboorteplaatsnaam', 'parser': to_string},
        {'name': 'omschrijvingGeslachtsaanduiding', 'parser': to_string},
        {'name': 'opgemaakteNaam', 'parser': to_string},
    ]

    parents = persoon_tree.find_all('PRSPRSOUD')
    if parents[0].get("xsi:nil") == 'true':
        return []

    for ouder in parents:
        result_parent = {}
        set_fields(ouder.PRS, parent_fields, result_parent)
        set_extra_fields(ouder.PRS, parent_extra_fields, result_parent)

        set_omschrijving_geslachtsaanduiding(result_parent)
        set_geboorteLandnaam(result_parent)
        set_geboorteplaatsNaam(result_parent)

        result.append(result_parent)

    result.sort(key=lambda x: x['geboortedatum'] or datetime.min)

    return result


def extract_verbintenis_data(persoon_tree: Tag):
    result = []

    verbintenis_fields = [
        {'name': 'datumSluiting', 'parser': to_date},
        {'name': 'datumOntbinding', 'parser': to_date},
        {'name': 'soortVerbintenis', 'parser': to_string},
    ]

    verbintenis_extra_fields = [
        {'name': 'soortVerbintenisOmschrijving', 'parser': to_string},
        {'name': 'landnaamSluiting', 'parser': to_string},
        {'name': 'plaatsnaamSluitingOmschrijving', 'parser': to_string},
    ]

    partner_fields = [
        {'name': 'bsn-nummer', 'parser': to_string, 'save_as': 'bsn'},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_date},
        {'name': 'datumOverlijden', 'parser': to_date, 'save_as': 'overlijdensdatum'},  # to match 3.10 field name
        {'name': 'adellijkeTitelPredikaat', 'parser': to_string},
    ]

    partner_extra_fields = [
        {'name': 'omschrijvingAdellijkeTitel', 'parser': to_string},
        {'name': 'geboortelandnaam', 'parser': to_string},
        {'name': 'geboorteplaatsnaam', 'parser': to_string},
        {'name': 'omschrijvingGeslachtsaanduiding', 'parser': to_string},
        {'name': 'opgemaakteNaam', 'parser': to_string},
    ]

    verbintenissen = persoon_tree.find_all('PRSPRSHUW')

    if verbintenissen[0].get("xsi:nil") == 'true':
        return {
            'verbintenis': {},
            'verbintenisHistorisch': [],
        }

    for verb in verbintenissen:
        result_verbintenis = {'persoon': {}}

        set_fields(verb, verbintenis_fields, result_verbintenis)
        set_extra_fields(verb, verbintenis_extra_fields, result_verbintenis)

        set_fields(verb.PRS, partner_fields, result_verbintenis['persoon'])
        set_extra_fields(verb.PRS, partner_extra_fields, result_verbintenis['persoon'])

        set_omschrijving_geslachtsaanduiding(result_verbintenis['persoon'])

        set_reden_ontbinding_omschrijving_custom(result_verbintenis, verb.find('redenOntbinding').string)

        result.append(result_verbintenis)

    # if there is no datumSluiting, sort using the minimum datetime
    # sort to be sure that the most current partner is on top
    result.sort(key=lambda x: x['datumSluiting'] or datetime.min)

    current_results = [p for p in result if not p['datumOntbinding']]

    if current_results:
        current_result = current_results[0]
    else:
        current_result = {}

    past_result = [p for p in result if p['datumOntbinding']]

    return {
        'verbintenis': current_result,
        'verbintenisHistorisch': past_result,
    }


def extract_address(persoon_tree: Tag, is_amsterdammer):
    result = {}
    fiels_tijdvak = [
        {'name': 'begindatumRelatie', 'parser': to_date, 'save_as': 'begindatumVerblijf'},
        {'name': 'einddatumRelatie', 'parser': to_date, 'save_as': 'einddatumVerblijf'},

    ]
    extra_fields = []
    if is_amsterdammer:
        extra_fields.append({'name': 'aanduidingGegevensInOnderzoek', 'parser': to_bool, 'save_as': 'inOnderzoek'})

    address_fields = [
        {'name': 'woonplaatsnaam', 'parser': to_string, 'save_as': 'woonplaatsNaam'},
        {'name': 'postcode', 'parser': as_postcode},
        {'name': 'huisnummer', 'parser': to_string},
        {'name': 'huisletter', 'parser': to_string},
        {'name': 'huisnummertoevoeging', 'parser': to_string},
        {'name': 'straatnaam', 'parser': to_string},

        {'name': 'centroidXCoordinaat', 'parser': to_string},
        {'name': 'centroidYCoordinaat', 'parser': to_string},
        {'name': 'centroidZCoordinaat', 'parser': to_string},
    ]
    address_extra_fields = [
        {'name': 'authentiekeWoonplaatsnaam', 'parser': to_string},
        {'name': 'officieleStraatnaam', 'parser': to_string},
    ]

    address = persoon_tree.find('PRSADRINS')
    if address.get("xsi:nil") == 'true':
        return {}

    set_fields(address.tijdvakRelatie, fiels_tijdvak, result)
    set_extra_fields(address, extra_fields, result)

    address_adr = address.ADR
    set_fields(address_adr, address_fields, result)
    set_extra_fields(address_adr, address_extra_fields, result)

    if result['authentiekeWoonplaatsnaam']:
        result['woonplaatsNaam'] = result['authentiekeWoonplaatsnaam']
    del result['authentiekeWoonplaatsnaam']

    if result['officieleStraatnaam']:
        result['straatnaam'] = result['officieleStraatnaam']
    del result['officieleStraatnaam']

    result['_adresSleutel'] = address.attrs['StUF:sleutelVerzendend']

    return result


def extract_identiteitsbewijzen(persoon_tree: Tag):
    result = []
    result_per_type = defaultdict(list)
    fields = [
        {'name': 'nummerIdentiteitsbewijs', 'parser': to_string, 'save_as': 'documentNummer'},
    ]
    extra_fields = [
        {'name': 'datumAfgifte', 'parser': to_date, 'save_as': 'datumUitgifte'},
        {'name': 'datumEindeGeldigheid', 'parser': to_date, 'save_as': 'datumAfloop'},
    ]
    SIB_fields = [
        {'name': 'soort', 'parser': to_int, 'save_as': 'documentType'},
    ]

    identiteitsbewijzen = persoon_tree.find_all('PRSIDB')

    if identiteitsbewijzen[0].get("xsi:nil") == 'true':
        return []

    for id in identiteitsbewijzen:
        result_id = {}
        set_fields(id, fields, result_id)
        set_extra_fields(id, extra_fields, result_id)
        set_fields(id.SIB, SIB_fields, result_id)

        try:
            result_id['documentType'] = lookup_prsidb_soort_code[result_id['documentType']]
        except Exception as e:
            logging.info(f"unknown document type {result_id['documentType']} {type(e)} {e}")
            result_id['documentType'] = f"onbekend type ({result_id['documentType']})"  # unknown doc type

        hash = sha256()
        hash.update(result_id['documentNummer'].encode())
        result_id['id'] = hash.hexdigest()

        result_per_type[result_id['documentType']].append(result_id)

    now = datetime.now()

    # pick current documents per type, if there isn't a valid one per type, pick the last one
    for doc_type in result_per_type:
        docs = result_per_type[doc_type]
        docs.sort(key=lambda x: x['datumAfloop'] or datetime.min)
        # select current ones
        new_list = [i for i in docs if i['datumAfloop'] > now]
        # no current docs, pick last one
        if not new_list:
            new_list = [docs[-1]]

        result.extend(new_list)

    return result


def extract_data(persoon_tree: Tag):
    verbintenissen = extract_verbintenis_data(persoon_tree)

    persoon = extract_persoon_data(persoon_tree)

    isAmsterdammer = persoon['mokum']
    adres = extract_address(persoon_tree, is_amsterdammer=persoon['mokum'])

    if isAmsterdammer:
        kinderen = extract_kinderen_data(persoon_tree)
        ouders = extract_parents_data(persoon_tree)
        verbintenis = verbintenissen['verbintenis']
        verbintenis_historisch = verbintenissen['verbintenisHistorisch']
        identiteitsbewijzen = extract_identiteitsbewijzen(persoon_tree)
    else:
        kinderen = []
        ouders = []
        verbintenis = {}
        verbintenis_historisch = []
        identiteitsbewijzen = []

    return {
        "persoon": persoon,
        "kinderen": kinderen,
        "ouders": ouders,
        'verbintenis': verbintenis,
        'verbintenisHistorisch': verbintenis_historisch,
        'adres': adres,
        'identiteitsbewijzen': identiteitsbewijzen,
    }


def opgemaakte_naam(persoon):
    # in case we do not have the opgemaakteNaam
    if persoon['opgemaakteNaam'] is None:
        if persoon['voornamen']:
            initials_list = ['%s.' % i[0] for i in persoon['voornamen'].split(' ')]
            initials = ''.join(initials_list)
        else:
            initials = ""

        if persoon['geslachtsnaam']:
            geslachtsnaam = persoon['geslachtsnaam']
            if persoon['voorvoegselGeslachtsnaam']:
                geslachtsnaam = f'{persoon["voorvoegselGeslachtsnaam"]} {geslachtsnaam}'
        else:
            geslachtsnaam = ""

        if initials and geslachtsnaam:
            persoon['opgemaakteNaam'] = "%s %s" % (initials, geslachtsnaam)
        else:
            # if all fails.. A standard text will have to do
            persoon['opgemaakteNaam'] = "Mijn gegevens"


def set_omschrijving_geslachtsaanduiding(target):
    # if omschrijving is set, do not attempt to overwrite it.
    if target.get('omschrijvingGeslachtsaanduiding'):
        return

    if not target.get('geslachtsaanduiding'):
        target['omschrijvingGeslachtsaanduiding'] = None
        return

    geslacht = lookup_geslacht.get(target['geslachtsaanduiding'], None)
    target['omschrijvingGeslachtsaanduiding'] = geslacht


def set_reden_ontbinding_omschrijving_custom(verbintenis, reden):
    reden_custom = None

    # see also: https://publicaties.rvig.nl/dsresource?objectid=17001&type=org
    if reden == 'O':
        reden_custom = 'Overlijden'
    elif reden == 'S':
        reden_custom = 'Echtscheiding'

    verbintenis['redenOntbindingOmschrijving'] = reden_custom


def set_geboorteplaatsNaam(target):
    _set_value_on(target, 'geboorteplaats', 'geboorteplaatsnaam', lookup_gemeenten)


def set_geboorteLandnaam(target):
    _set_value_on(target, 'geboorteLand', 'geboortelandnaam', lookup_landen)


