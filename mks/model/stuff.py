import datetime
import re
import traceback
from typing import List, Dict, Any

from lxml import objectify
from lxml.etree import ElementTree
from lxml.objectify import ObjectifiedElement

from mks.model.gba import lookup_landen, lookup_gemeenten, lookup_geslacht

_namespaces = {
    'StUF': 'http://www.egem.nl/StUF/StUF0301',
    'BG': 'http://www.egem.nl/StUF/sector/bg/0310',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/'
}  # type: Dict[str, str]


def set_fields(source, fields, target):
    """ Iterate over the list of fields to be put on target dict from the source

        source: subscriptable object (like a dict)
        fields: A list of fields which data to include. Format:
                [
                  {
                    'name': source field name,
                    'parser': a function to put the value through. For example to parse a date or number,
                    'save_as': the key name the value is stored under in the result dict
                  },
                  ...
                ]
        target: a dict where the result will be put on
     """
    for field in fields:
        try:
            value = source[field['name']]
        except AttributeError:
            # if optional is set, continue with the next field, Else error
            if field.get('optional'):
                continue
            else:
                raise
        value = field['parser'](value)
        key = field.get('save_as', field['name'])
        target[key] = value


def set_extra_fields(source, fields, target):
    """ Same set_fields, but then for the lovely stuf extra fields. """
    stufns = "{" + _namespaces['StUF'] + "}"

    for field in fields:
        value = source.find(f"{stufns}extraElement[@naam='{field['name']}']")
        key = field.get('save_as', field['name'])
        target[key] = field['parser'](value)


class StuffReply:
    _base_paths = {
        'base': [
            "Envelope",
            "Body",
            "{http://www.egem.nl/StUF/sector/bg/0310}npsLa01",
            "antwoord",
            "object"],
        'gerelateerde': ['{%s}gerelateerde' % _namespaces["BG"]],
        'partner': ["inp.heeftAlsEchtgenootPartner"],
        'kinderen': ["inp.heeftAlsKinderen"],
        'ouders': ["inp.heeftAlsOuders"],
        'nationaliteiten': ["inp.heeftAlsNationaliteit"],
        'adres': [
            "{%s}inp.verblijftIn" % _namespaces["BG"],
            '{%s}gerelateerde' % _namespaces["BG"],
            "{%s}adresAanduidingGrp" % _namespaces["BG"]
        ],
        'verblijftIn': ["{%s}inp.verblijftIn" % _namespaces["BG"]],
    }  # type: Dict[str, List[str]]

    def __init__(self, response: ElementTree):
        self._process_response(response)

    def _process_response(self, resp: ElementTree) -> None:
        if isinstance(resp, ObjectifiedElement):
            self.response_root = resp
        else:
            self.response_root = resp.getroot()

        try:
            self.gerelateerde = objectify.ObjectPath(
                self._base_paths['gerelateerde'])

            self.gerelateerde_kind = objectify.ObjectPath(
                self._base_paths['kinderen'] +
                self._base_paths['gerelateerde'])

            self.gerelateerde_partner = objectify.ObjectPath(
                self._base_paths['partner'] +
                self._base_paths['gerelateerde'])

            # self.gerelateerde_ouder = objectify.ObjectPath(
            #     self._base_paths['ouders'] +
            #     self._base_paths['gerelateerde'])
            #
            self.gerelateerde_nationaliteit = objectify.ObjectPath(
                self._base_paths['nationaliteiten'] +
                self._base_paths['gerelateerde'])

            try:
                # this one is ok to fail
                self.adres = objectify.ObjectPath(
                    self._base_paths['base'] +
                    self._base_paths['adres'])(self.response_root)
                self.verblijft_in = objectify.ObjectPath(
                    self._base_paths['base'] +
                    self._base_paths['verblijftIn'])(self.response_root)
            except AttributeError:
                self.adres = None
                pass

            # self.kind_verblijfsadres = objectify.ObjectPath(
            #     self._base_paths['gerelateerde'] +
            #     ['verblijfsadres'])
            #
            # self.kind_correspondentieadres = objectify.ObjectPath(
            #     self._base_paths['gerelateerde'] +
            #     ['sub.correspondentieAdres'])

            self.persoon = objectify.ObjectPath(
                self._base_paths['base'])(self.response_root)

            self.partners = objectify.ObjectPath(
                self._base_paths['base'] +
                self._base_paths['partner'])(self.response_root)

            self.kinderen = objectify.ObjectPath(
                self._base_paths['base'] +
                self._base_paths['kinderen'])(self.response_root)

            # self.ouders = objectify.ObjectPath(
            #     self._base_paths['base'] +
            #     self._base_paths['ouders'])(self.response_root)
            #
            self.nationaliteiten = objectify.ObjectPath(
                self._base_paths['base'] +
                self._base_paths['nationaliteiten'])(self.response_root)
            self.parsed_successfully = True
        except AttributeError:
            traceback.print_exc()
            self.parsed_successfully = False

    def is_valid_response(self) -> bool:
        return (self.parsed_successfully and
                self.persoon['inp.bsn'] is not None and
                self.persoon['inp.bsn'].pyval > 0)

    def get_persoon(self):
        result = {}

        stufns = "{" + _namespaces['StUF'] + "}"
        fields = [
            {'name': 'inp.bsn', 'parser': self.to_string, 'save_as': 'bsn'},
            {'name': 'geslachtsnaam', 'parser': self.to_string},
            {'name': 'voornamen', 'parser': self.to_string},
            {'name': 'geboortedatum', 'parser': self.to_date},
            {'name': 'voorvoegselGeslachtsnaam', 'parser': self.to_string},
            {'name': 'inp.gemeenteVanInschrijving', 'parser': self.to_is_amsterdam, 'save_as': 'mokum'},
            {'name': 'inp.geboorteplaats', 'parser': self.to_string, 'save_as': 'geboorteplaats'},
            {'name': 'inp.geboorteLand', 'parser': self.to_string, 'save_as': 'geboorteLand'},
            {'name': 'geslachtsaanduiding', 'parser': self.to_string},
            {'name': 'inp.emigratieLand', 'parser': self.to_int, 'save_as': "emigratieLand"},
            {'name': 'inp.datumVertrekUitNederland', 'parser': self.to_date, 'save_as': "datumVertrekUitNederland"},
        ]
        extra_fields = [
            {'name': 'aanduidingNaamgebruikOmschrijving', 'parser': self.to_string},
            {'name': 'geboortelandnaam', 'parser': self.to_string},
            {'name': 'geboorteplaatsnaam', 'parser': self.to_string},
            {'name': 'gemeentenaamInschrijving', 'parser': self.to_string},
            {'name': 'omschrijvingBurgerlijkeStaat', 'parser': self.to_string},
            {'name': 'omschrijvingGeslachtsaanduiding', 'parser': self.to_string},
            {'name': 'omschrijvingIndicatieGeheim', 'parser': self.to_string},
            {'name': 'opgemaakteNaam', 'parser': self.to_string},
            {'name': 'omschrijvingAdellijkeTitel', 'parser': self.to_string},

        ]

        extra = self.persoon[f'{stufns}extraElementen']
        set_fields(self.persoon, fields, result)
        set_extra_fields(extra, extra_fields, result)

        if result['geboorteplaats'] and not result['geboorteplaatsnaam']:
            try:
                key = "%04d" % int(result['geboorteplaats'])
                gemeente_naam = lookup_gemeenten.get(key, None)
                if gemeente_naam:
                    result['geboorteplaatsnaam'] = gemeente_naam
            except ValueError:
                # int() fails when it already is filled with a name, so use that instead.
                result['geboorteplaatsnaam'] = result['geboorteplaats']

        if result['geboorteLand'] and not result['geboortelandnaam']:
            land_naam = lookup_landen.get(result['geboorteLand'], None)
            if land_naam:
                result['geboortelandnaam'] = land_naam

        if result['geslachtsaanduiding'] and not result['omschrijvingGeslachtsaanduiding']:
            geslacht = lookup_geslacht.get(result['geslachtsaanduiding'], None)
            if geslacht:
                result['omschrijvingGeslachtsaanduiding'] = geslacht

        # vertrokken onbekend waarheen
        if result['emigratieLand'] == 0:
            result['vertrokkenOnbekendWaarheen'] = True
        else:
            result['vertrokkenOnbekendWaarheen'] = False

        result['nationaliteiten'] = self.get_nationaliteiten()

        return result

    def get_partner(self):
        """ Get only the current partner """
        if not self.partners:
            return {}

        stufns = "{" + _namespaces['StUF'] + "}"

        result = []

        partners = [{
            'partner': p,
            'gerelateerde': self.gerelateerde_partner(p)
        } for p in self.partners]

        fields = [
            {'name': 'soortVerbintenis', 'parser': self.to_string},
            {'name': 'datumSluiting', 'parser': self.to_date},
            {'name': 'datumOntbinding', 'parser': self.to_date},
        ]

        fields_extra = [
            {'name': 'soortVerbintenisOmschrijving', 'parser': self.to_string},
            {'name': 'landnaamSluiting', 'parser': self.to_string},
            {'name': 'plaatsnaamSluitingOmschrijving', 'parser': self.to_string},
        ]

        fields_partner = [
            {'name': 'inp.bsn', 'parser': self.to_string, 'save_as': 'bsn'},
            {'name': 'voornamen', 'parser': self.to_string},
            {'name': 'voorvoegselGeslachtsnaam', 'parser': self.to_string},
            {'name': 'geslachtsnaam', 'parser': self.to_string},
            {'name': 'geslachtsaanduiding', 'parser': self.to_string},
            {'name': 'geboortedatum', 'parser': self.to_date},
            {'name': 'overlijdensdatum', 'parser': self.to_date},
            {'name': 'adellijkeTitelPredikaat', 'parser': self.to_date},

        ]

        for p in partners:
            partner = {'persoon': {}}
            set_fields(p['partner'], fields, partner)
            set_fields(p['gerelateerde'], fields_partner, partner['persoon'])

            extra = p['partner'].find(f'{stufns}extraElementen')
            set_extra_fields(extra, fields_extra, partner)

            extra = p['partner'].find(f'{stufns}extraElementen')
            set_extra_fields(extra, fields_extra, partner)

            self.set_omschrijving_geslachtsaanduiding(partner['persoon'])

            result.append(partner)

        # if there is no datumSluiting, sort using the minimum datetime
        # sort to be sure that the most current partner is on top
        result.sort(key=lambda x: x['datumSluiting'] or datetime.datetime.min)

        result = [p for p in result if not p['datumOntbinding']]

        if result:
            return result[0]
        else:
            return {}

    def get_kinderen(self):
        if not self.kinderen:
            return {}

        result = []

        kinderen = [{
            'kind': k,
            'gerelateerde': self.gerelateerde_kind(k)
        } for k in self.kinderen]

        fields = [
            {'name': 'inp.bsn', 'parser': self.to_string, 'save_as': 'bsn'},
            {'name': 'voornamen', 'parser': self.to_string},
            {'name': 'voorvoegselGeslachtsnaam', 'parser': self.to_string},
            {'name': 'geslachtsnaam', 'parser': self.to_string},
            {'name': 'geslachtsaanduiding', 'parser': self.to_string},
            {'name': 'geboortedatum', 'parser': self.to_date},
            {'name': 'inp.geboorteplaats', 'parser': self.to_date, 'save_as': 'geboorteplaats'},
            {'name': 'inp.geboorteLand', 'parser': self.to_date, 'save_as': 'geboorteLand'},
            {'name': 'overlijdensdatum', 'parser': self.to_date},
            {'name': 'adellijkeTitelPredikaat', 'parser': self.to_date},
        ]

        for k in kinderen:
            kind = {}
            set_fields(k['gerelateerde'], fields, kind)
            self.set_omschrijving_geslachtsaanduiding(kind)

            result.append(kind)

        result.sort(key=lambda x: x['geboortedatum'])

        return result

    # def get_ouders(self):
    #     return [{
    #         'ouder': o,
    #         'gerelateerde': self.gerelateerde_ouder(o)
    #     } for o in self.ouders]
    #
    def get_nationaliteiten(self):
        if not self.nationaliteiten:
            return {}

        result = []

        fields = [
            {'name': 'omschrijving', 'parser': self.to_string},
            {'name': 'code', 'parser': self.to_string}
        ]

        for n in self.nationaliteiten:
            nationaliteit = {}
            set_fields(n['gerelateerde'], fields, nationaliteit)
            result.append(nationaliteit)

        # For people not living in Amsterdam we dont get the omschrijving.
        # Quick fix for Nederlandse if code == 1
        for n in result:
            if not n['omschrijving']:
                if n['code'] == "1":
                    n['omschrijving'] = "Nederlandse"

        # Only add the omschrijving
        result = [{"omschrijving": n["omschrijving"]} for n in result if n['omschrijving']]
        return result

    def get_adres(self):
        if not self.adres:
            return {}

        fields = [
            {'name': 'wpl.woonplaatsNaam', 'parser': self.to_string, 'save_as': 'woonplaatsNaam'},
            {'name': 'gor.openbareRuimteNaam', 'parser': self.to_string, 'save_as': 'straatnaam'},
            {'name': 'aoa.postcode', 'parser': self.as_postcode, 'save_as': 'postcode'},
            {'name': 'aoa.huisnummer', 'parser': self.to_string, 'save_as': 'huisnummer'},
            {'name': 'aoa.huisletter', 'parser': self.to_string, 'save_as': 'huisletter'},
            {'name': 'aoa.huisnummertoevoeging', 'parser': self.to_string, 'save_as': 'huisnummertoevoeging'},
        ]

        result = {}
        set_fields(self.adres, fields, result)

        if self.verblijft_in:
            tijdvak = self.verblijft_in.find('{%s}tijdvakRelatie' % _namespaces['StUF'])\
                .find('{%s}beginRelatie' % _namespaces['StUF'])
            if tijdvak:
                result['begindatumVerblijf'] = self.to_date(tijdvak)

            verblijft_in_fields = [
                {'name': 'inOnderzoek', 'parser': self.to_bool, 'save_as': 'adresInOnderzoek', 'optional': True},
            ]
            set_fields(self.verblijft_in, verblijft_in_fields, result)
            # print("result", result)

        return result

    def as_dict(self) -> Dict[str, Any]:
        return {
            'persoon': self.get_persoon(),
            'verbintenis': self.get_partner(),
            'kinderen': self.get_kinderen(),
            'adres': self.get_adres(),
        }

    def set_omschrijving_geslachtsaanduiding(self, target):
        # if omschrijving is set, do not attempt to overwrite it.
        if target.get('omschrijvingGeslachtsaanduiding', False) is not False:
            return

        if target.get('geslachtsaanduiding', False) is False:
            target['omschrijvingGeslachtsaanduiding'] = None
            return

        if target['geslachtsaanduiding']:
            geslacht = lookup_geslacht.get(target['geslachtsaanduiding'], None)
            target['omschrijvingGeslachtsaanduiding'] = geslacht

    @staticmethod
    def to_date(value):
        """
        :param value:
        :return:
        """
        if not value:
            return None
        try:
            parsed_value = datetime.datetime.strptime(str(value), '%Y%m%d')
            return parsed_value
        except ValueError:
            pass
        return value

    @staticmethod
    def to_int(value):
        # our xml parser, automatically converts numbers. So this converter doesn't do much.
        if value == 0:
            return 0
        if not value:
            return None
        return int(value)

    @staticmethod
    def to_string(value):
        if not value:
            return None
        return str(value).strip()

    @staticmethod
    def to_bool(value):
        # breakpoint()
        if not value:
            return False
        return True

    @staticmethod
    def as_postcode(value):
        if not value:
            return None
        value = StuffReply.to_string(value)
        match = re.match(r'(?P<num>\d{4})(?P<let>[A-Z]{2})', value)
        if not match:
            return None

        return f"{match['num']} {match['let']}"

    @staticmethod
    def to_is_amsterdam(value):
        if not value:
            return False

        if value == 363:
            return True
        else:
            return False
