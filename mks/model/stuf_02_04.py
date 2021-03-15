import logging
from collections import defaultdict
from datetime import datetime
from hashlib import sha256

from bs4 import Tag, ResultSet
from dateutil.relativedelta import relativedelta

from mks.model.gba import lookup_prsidb_soort_code, lookup_geslacht, lookup_gemeenten, lookup_landen, \
    lookup_nationaliteiten
from mks.model.stuf_utils import _set_value_on, to_string, to_datetime, to_bool, to_is_amsterdam, to_int, set_fields, \
    set_extra_fields, as_postcode, encrypt, geheim_indicatie_to_bool, as_bsn, landcode_to_name, is_nil, to_string_4x0


def get_nationaliteiten(nationaliteiten: ResultSet):
    result = []

    fields = [
        {'name': 'datumVerlies', 'parser': to_datetime},
    ]

    nat_fields = [
        {'name': 'omschrijving', 'parser': to_string},
        {'name': 'code', 'parser': to_int},
    ]

    if is_nil(nationaliteiten):
        return []

    for nat in nationaliteiten:
        nationaliteit = {}
        set_fields(nat, fields, nationaliteit)
        set_fields(nat.find("NAT"), nat_fields, nationaliteit)
        result.append(nationaliteit)

    # For people not living in Amsterdam we dont get the omschrijving.
    # Quick fix for Nederlandse if code == 1
    for n in result:
        if not n['omschrijving']:
            code = str(n['code']).zfill(4)
            n['omschrijving'] = lookup_nationaliteiten.get(code)

    result = [n for n in result if not n['datumVerlies']]

    # cleanup
    for n in result:
        del n['datumVerlies']

    return result


def extract_persoon_data(persoon_tree: Tag):
    result = {}

    prs_fields = [
        {'name': 'bsn-nummer', 'parser': as_bsn, 'save_as': 'bsn'},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_datetime},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string},
        {'name': 'codeGemeenteVanInschrijving', 'parser': to_int},
        {'name': 'codeGemeenteVanInschrijving', 'parser': to_is_amsterdam, 'save_as': 'mokum'},
        {'name': 'geboorteplaats', 'parser': to_string},
        {'name': 'codeGeboorteland', 'parser': to_string_4x0, 'save_as': 'geboorteLand'},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'codeLandEmigratie', 'parser': to_int},
        {'name': 'datumVertrekUitNederland', 'parser': to_datetime},
        {'name': 'indicatieGeheim', 'parser': geheim_indicatie_to_bool},
        {'name': 'aanduidingNaamgebruik', 'parser': to_string},
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

    # vertrokken onbekend waarheen
    result['vertrokkenOnbekendWaarheen'] = False

    result['nationaliteiten'] = get_nationaliteiten(persoon_tree.find_all('PRSNAT'))

    set_omschrijving_geslachtsaanduiding(result)
    set_geboorteLandnaam(result)
    set_geboorteplaatsNaam(result)

    return result


def extract_kinderen_data(persoon_tree: Tag):
    result = []

    knd_fields = [
        {'name': 'bsn-nummer', 'parser': as_bsn, 'save_as': 'bsn'},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_datetime},
        {'name': 'geboorteplaats', 'parser': to_string},
        {'name': 'codeGeboorteland', 'parser': to_string_4x0, 'save_as': 'geboorteLand'},
        {'name': 'datumOverlijden', 'parser': to_datetime, 'save_as': 'overlijdensdatum'},  # Save as name to match 3.10
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
    if is_nil(kinderen):
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
        {'name': 'bsn-nummer', 'parser': as_bsn, 'save_as': 'bsn'},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_datetime},
        {'name': 'geboorteplaats', 'parser': to_string},
        {'name': 'codeGeboorteland', 'parser': to_string, 'save_as': 'geboorteLand'},  # save as to match 3.10
        {'name': 'datumOverlijden', 'parser': to_datetime, 'save_as': 'overlijdensdatum'},  # save as to match 3.10'
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
    if is_nil(parents):
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
        {'name': 'datumSluiting', 'parser': to_datetime},
        {'name': 'datumOntbinding', 'parser': to_datetime},
        {'name': 'soortVerbintenis', 'parser': to_string},
    ]

    verbintenis_extra_fields = [
        {'name': 'soortVerbintenisOmschrijving', 'parser': to_string},
        {'name': 'landnaamSluiting', 'parser': to_string},
        {'name': 'plaatsnaamSluitingOmschrijving', 'parser': to_string},
    ]

    partner_fields = [
        {'name': 'bsn-nummer', 'parser': as_bsn, 'save_as': 'bsn'},
        {'name': 'voornamen', 'parser': to_string},
        {'name': 'voorvoegselGeslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsnaam', 'parser': to_string},
        {'name': 'geslachtsaanduiding', 'parser': to_string},
        {'name': 'geboortedatum', 'parser': to_datetime},
        {'name': 'datumOverlijden', 'parser': to_datetime, 'save_as': 'overlijdensdatum'},  # to match 3.10 field name
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
    result = []
    fields_tijdvak = [
        {'name': 'begindatumRelatie', 'parser': to_datetime, 'save_as': 'begindatumVerblijf'},
        {'name': 'einddatumRelatie', 'parser': to_datetime, 'save_as': 'einddatumVerblijf'},

    ]
    extra_fields = []
    if is_amsterdammer:
        extra_fields.append({'name': 'aanduidingGegevensInOnderzoek', 'parser': to_bool, 'save_as': 'inOnderzoek'})

    address_fields = [
        {'name': 'woonplaatsnaam', 'parser': to_string, 'save_as': 'woonplaatsNaam'},
        {'name': 'landcode', 'parser': to_string_4x0},
        {'name': 'landcode', 'parser': landcode_to_name, 'save_as': 'landnaam'},
        {'name': 'postcode', 'parser': as_postcode},
        {'name': 'huisnummer', 'parser': to_string},
        {'name': 'huisletter', 'parser': to_string},
        {'name': 'huisnummertoevoeging', 'parser': to_string},
        {'name': 'straatnaam', 'parser': to_string},
        {'name': 'gemeentecode', 'parser': to_string_4x0},
        {'name': 'adresBuitenland1', 'parser': to_string},
        {'name': 'adresBuitenland2', 'parser': to_string},
        {'name': 'adresBuitenland3', 'parser': to_string},
    ]
    address_extra_fields = [
        {'name': 'authentiekeWoonplaatsnaam', 'parser': to_string},
        {'name': 'officieleStraatnaam', 'parser': to_string},
    ]

    addresses = persoon_tree.find_all('PRSADRINS')
    if is_nil(addresses):
        return {}, []

    for address in addresses:
        address_result = {}

        set_fields(address.tijdvakRelatie, fields_tijdvak, address_result)
        set_extra_fields(address, extra_fields, address_result)

        address_adr = address.ADR
        set_fields(address_adr, address_fields, address_result)
        set_extra_fields(address_adr, address_extra_fields, address_result)

        if address_result['authentiekeWoonplaatsnaam']:
            address_result['woonplaatsNaam'] = address_result['authentiekeWoonplaatsnaam']
        del address_result['authentiekeWoonplaatsnaam']

        _set_value_on(address_result, 'gemeentecode', 'woonplaatsNaam', lookup_gemeenten)
        del address_result['gemeentecode']

        if address_result['officieleStraatnaam']:
            address_result['straatnaam'] = address_result['officieleStraatnaam']
        del address_result['officieleStraatnaam']

        # get adressleutel to be able to get data about address resident count
        if address_adr.attrs.get('StUF:sleutelVerzendend'):
            address_result['_adresSleutel'] = encrypt(address_adr.attrs['StUF:sleutelVerzendend'])

        result.append(address_result)

    current = None
    past = []
    for address in result:
        end = address['einddatumVerblijf']
        if end is None or end > datetime.now():
            current = address
        else:
            if address.get('_adresSleutel'):
                del address['_adresSleutel']
            past.append(address)

    past.sort(key=lambda x: x['einddatumVerblijf'] or datetime.min, reverse=True)

    # Punt adres is a thing so people are not registered on an address (which has al kinds of implications for that adres)
    # take the most recent as current and mark it as Adres in onderzoek
    # see MIJN-2825
    if current['straatnaam'] == '.':
        # if there is a past address, use that as current (because that's what the punt adres replaced)
        if past:
            current = past.pop(0)

        current['inOnderzoek'] = True

    return current, past


def extract_identiteitsbewijzen(persoon_tree: Tag):
    result = []
    result_per_type = defaultdict(list)
    fields = [
        {'name': 'nummerIdentiteitsbewijs', 'parser': to_string, 'save_as': 'documentNummer'},
    ]
    extra_fields = [
        {'name': 'datumAfgifte', 'parser': to_datetime, 'save_as': 'datumUitgifte'},
        {'name': 'datumEindeGeldigheid', 'parser': to_datetime, 'save_as': 'datumAfloop'},
    ]
    SIB_fields = [
        {'name': 'soort', 'parser': to_int, 'save_as': 'documentType'},
    ]

    identiteitsbewijzen = persoon_tree.find_all('PRSIDB')

    if is_nil(identiteitsbewijzen):
        return []

    for id in identiteitsbewijzen:
        result_id = {}
        set_fields(id, fields, result_id)
        set_extra_fields(id, extra_fields, result_id)
        set_fields(id.SIB, SIB_fields, result_id)

        type_number = result_id['documentType']
        original_type_number = type_number
        if type_number == 2:
            type_number = 10  # manual fix for EU ID.

        # only allow these IDs
        if type_number not in [1, 6, 7, 10]:
            continue

        if type_number == 10:
            # do not show nederlandse identiteitskaart older than 3 months. passpoort etc stays
            if not result_id['datumAfloop']:
                logging.error(f"ID without a datumEindeGeldigheid. original soort: {original_type_number}")
            elif result_id['datumAfloop'] + relativedelta(months=+3) < datetime.now():
                # skip
                continue

        try:
            result_id['documentType'] = lookup_prsidb_soort_code[type_number]
        except Exception as e:
            logging.info(f"unknown document type {type_number} {type(e)} {e}")
            result_id['documentType'] = f"onbekend type ({type_number})"  # unknown doc type

        hash = sha256()
        hash.update(result_id['documentNummer'].encode())
        result_id['id'] = hash.hexdigest()

        result_per_type[type_number].append(result_id)

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
    address_current, address_history = extract_address(persoon_tree, is_amsterdammer=persoon['mokum'])

    # only show VOW when last know address was in Amsterdam, otherwise we're not responsible for it.
    if address_current and address_current['landcode'] == '0000':
        if len(address_history) > 0 and address_history[0]['woonplaatsNaam'] == "Amsterdam":
            persoon['vertrokkenOnbekendWaarheen'] = True

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

    # collect all partners in a list
    naam_verbintenissen = verbintenis_historisch
    if verbintenis:
        naam_verbintenissen = [verbintenis] + naam_verbintenissen
    set_opgemaakte_naam(persoon, [i['persoon'] for i in naam_verbintenissen])

    return {
        "persoon": persoon,
        "kinderen": kinderen,
        "ouders": ouders,
        'verbintenis': verbintenis,
        'verbintenisHistorisch': verbintenis_historisch,
        'adres': address_current,
        'adresHistorisch': address_history,
        'identiteitsbewijzen': identiteitsbewijzen,
    }


def _naam(persoon):
    geslachtsnaam = persoon['geslachtsnaam']
    if persoon['voorvoegselGeslachtsnaam']:
        return f'{persoon["voorvoegselGeslachtsnaam"]} {geslachtsnaam}'
    else:
        return geslachtsnaam


def _format_achternaam(persoon, partner):
    aanduiding = persoon['aanduidingNaamgebruik']

    if partner and partner['geslachtsnaam']:
        if aanduiding == 'N':
            return f"{_naam(persoon)} - {_naam(partner)}"
        if aanduiding == 'V':
            return f"{_naam(partner)} - {_naam(persoon)}"
        if aanduiding == 'P':
            return _naam(partner)

    # aanduiding E is left, this is also a default
    return _naam(persoon)


def _get_current_or_last_partner(verbintenissen):
    if verbintenissen:
        return verbintenissen[0]
    else:
        return None


def set_opgemaakte_naam(persoon, verbintenissen):
    """ Set the formatted name of person. When person already has a opgemaakteNaam, don't overwrite it. """
    # in case we do not have the opgemaakteNaam
    if persoon['opgemaakteNaam'] is None:
        if persoon['voornamen']:
            initials_list = ['%s.' % i[0] for i in persoon['voornamen'].split(' ')]
            initials = ''.join(initials_list)
        else:
            initials = ""

        current_or_last_partner = _get_current_or_last_partner(verbintenissen)
        geslachtsnaam = _format_achternaam(persoon, current_or_last_partner)

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
