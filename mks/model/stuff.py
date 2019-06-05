import datetime
import traceback
from copy import deepcopy
from typing import List, Dict, Any, Optional

import xmltodict
from lxml import objectify
from lxml.etree import tostring, ElementTree
from lxml.objectify import ObjectifiedElement


class StuffReply:
    _namespaces = {
        'StUF': 'http://www.egem.nl/StUF/StUF0301',
        'BG': 'http://www.egem.nl/StUF/sector/bg/0310',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/'
    }  # type: Dict[str, str]

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
        'nationaliteiten': ["inp.heeftAlsNationaliteit"]

    }  # type: Dict[str, List[str]]

    def __init__(self, response: ElementTree) -> Optional[Any]:
        self._process_response(response)

    def _process_response(self, resp: ElementTree) -> None:
        if isinstance(resp, ObjectifiedElement):
            self.response_root = resp
        else:
            self.response_root = resp.getroot()

        # import ipdb; ipdb.set_trace()

        try:
            self.gerelateerde = objectify.ObjectPath(
                self._base_paths['gerelateerde'])

            self.gerelateerde_kind = objectify.ObjectPath(
                self._base_paths['kinderen'] +
                self._base_paths['gerelateerde'])

            self.gerelateerde_partner = objectify.ObjectPath(
                self._base_paths['partner'] +
                self._base_paths['gerelateerde'])

            self.gerelateerde_ouder = objectify.ObjectPath(
                self._base_paths['ouders'] +
                self._base_paths['gerelateerde'])

            self.gerelateerde_nationaliteit = objectify.ObjectPath(
                self._base_paths['nationaliteiten'] +
                self._base_paths['gerelateerde'])

            self.kind_verblijfsadres = objectify.ObjectPath(
                self._base_paths['gerelateerde'] +
                ['verblijfsadres'])

            self.kind_correspondentieadres = objectify.ObjectPath(
                self._base_paths['gerelateerde'] +
                ['sub.correspondentieAdres'])

            self.persoon = objectify.ObjectPath(
                self._base_paths['base'])(self.response_root)

            # FIXME: there might be multiple partners. Only show if it is a current partner (not gescheiden, still alive)
            self.partner = objectify.ObjectPath(
                self._base_paths['base'] +
                self._base_paths['partner'])(self.response_root)

            self.kinderen = objectify.ObjectPath(
                self._base_paths['base'] +
                self._base_paths['kinderen'])(self.response_root)

            self.ouders = objectify.ObjectPath(
                self._base_paths['base'] +
                self._base_paths['ouders'])(self.response_root)

            self.nationaliteiten = objectify.ObjectPath(
                self._base_paths['base'] +
                self._base_paths['nationaliteiten'])(self.response_root)
            self.parsed_successfully = True
        except AttributeError:
            traceback.print_exc()
            self.parsed_successfully = False

    def is_valid_response(self) -> bool:
        return self.parsed_successfully \
            and self.persoon['inp.bsn'] is not None \
            and self.persoon['inp.bsn'].pyval > 0

    def get_persoon(self):
        result = {}

        stufns = "{" + self._namespaces['StUF'] + "}"
        bgns = "{" + self._namespaces['BG'] + "}"
        fields = [
            {'name': 'inp.bsn', 'parser': self.to_string},
            {'name': 'geslachtsnaam', 'parser': self.to_string},
            {'name': 'voornamen', 'parser': self.to_string},
            {'name': 'geboortedatum', 'parser': self.to_date},
        ]
        extra_fields = [
            {'name': 'omschrijvingGeslachtsaanduiding', 'parser': self.to_string},
            {'name': 'aanduidingNaamgebruikOmschrijving', 'parser': self.to_string},
            {'name': 'geboortelandnaam', 'parser': self.to_string},
            {'name': 'geboorteplaatsnaam', 'parser': self.to_string},
            {'name': 'gemeentenaamInschrijving', 'parser': self.to_string},
            {'name': 'landnaamImmigratie', 'parser': self.to_string},
            {'name': 'omschrijvingBurgerlijkeStaat', 'parser': self.to_string},
            {'name': 'opgemaakteNaam', 'parser': self.to_string},
        ]

        for field in fields:
            value = self.persoon[f'{bgns}{field["name"]}']
            value = field['parser'](value)
            result[field['name']] = value

        extra = self.persoon[f'{stufns}extraElementen']

        for field in extra_fields:
            value = extra.find(f"{stufns}extraElement[@naam='{field['name']}']")
            value = field['parser'](value)
            result[field['name']] = value

        return result

    def get_partner(self):
        return {
            'partner': self.partner,
            'gerelateerde': self.gerelateerde_partner(self.partner)
        }

    def get_kinderen(self):
        result = []

        kinderen = [{
            'kind': k,
            'gerelateerde': self.gerelateerde_kind(k)
        } for k in self.kinderen]

        fields = [
            {'name': 'inp.bsn', 'parser': self.to_string},
            {'name': 'voornamen', 'parser': self.to_string},
            {'name': 'geslachtsnaam', 'parser': self.to_string},
            {'name': 'geslachtsaanduiding', 'parser': self.to_string},
            {'name': 'geboortedatum', 'parser': self.to_date},
            {'name': 'overlijdensdatum', 'parser': self.to_date},
        ]
        for k in kinderen:
            kind = {}
            for field in fields:
                value = k['gerelateerde'][field['name']]
                value = field['parser'](value)
                kind[field['name']] = value

            result.append(kind)

        result.sort(key=lambda x: x['geboortedatum'])

        return result

    def get_ouders(self):
        return [{
            'ouder': o,
            'gerelateerde': self.gerelateerde_ouder(o)
        } for o in self.ouders]

    def get_nationaliteiten(self):
        return [{
            'nationaliteit': n,
            'gerelateerde': self.gerelateerde_nationaliteit(n)
        } for n in self.nationaliteiten]

    def as_dict(self) -> Dict[str, Any]:
        json_nss = {
            'http://www.egem.nl/StUF/sector/bg/0310': None,
            'http://schemas.xmlsoap.org/soap/envelope/': None,
            'http://www.egem.nl/StUF/StUF0301': None,
            'http://www.w3.org/2001/XMLSchema-instance': None
        }

        res = xmltodict.parse(
            xml_input=tostring(self._cleaned_response()),
            process_namespaces=True,
            namespaces=json_nss
        )

        self.add_extra_information(res, self.response_root)

        self.check_and_fix_dates(res)

        return res

    def _cleaned_response(self):
        filtered_xml = deepcopy(self.response_root)
        for i in range(2):
            # After a first round of cleaning some empty parent tags will remain
            # hence the second round
            self._do_clean(filtered_xml)

        return filtered_xml.xpath('//persoon', namespaces=self._namespaces)[0]

    def check_and_fix_dates(self, iterable) -> None:  # noqa: C901
        """
        FIXME: dangerous
        :param item:
        :return:
        """
        print("!!! check_and_fix_dates")

        if isinstance(iterable, dict):
            for key, value in iterable.items():
                if isinstance(value, dict) or isinstance(value, list):
                    self.check_and_fix_dates(value)
                elif value is not None:
                    iterable[key] = self.to_date(value)
        elif isinstance(iterable, list):
            for i, item in enumerate(iterable):
                if isinstance(item, dict) or isinstance(item, list):
                    self.check_and_fix_dates(item)
                else:
                    iterable[i] = self.to_date(item)

    def add_extra_information(self, dict_to_add_to, original_tree):
        for i in self._add_data:
            value = self._get_value_from_extra_element(original_tree, i[0])
            if value:
                self._set_to_dict(dict_to_add_to, i[1], value)

    def _set_to_dict(self, dict_to_add_to, path, value):
        path_split = path.split('.')
        data = dict_to_add_to
        for key in path_split[:-1]:
            data = data[key]

        data[path_split[-1]] = value

    def _get_value_from_extra_element(self, tree, extra_name):
        result = tree.findall(f".//*[@naam='{extra_name}']")
        if result:
            if result[0]:
                return result[0].pyval.strip()

    @staticmethod
    def to_date(value):
        """
        FIXME: dangerous
        :param value:
        :return:
        """
        if value is not None:
            try:
                parsed_value = datetime.datetime.strptime(str(value), '%Y%m%d')
                return parsed_value.isoformat()
            except ValueError:
                pass
        return value

    @staticmethod
    def to_string(value):
        return str(value).strip()

    def _do_clean(self, xml: ElementTree) -> None:  # noqa: C901
        """
        Process response xml and clean, rename it in one go.
        :param xml: the xml rootnode to be cleaned
        """
        print("CLEAN")

        element_tags = xml.xpath('//StUF:extraElement', namespaces=self._namespaces)
        # fix extraElementen to have their own tag, works better with toDict
        for elem in element_tags:
            elem.tag = elem.attrib['naam']

        elementen_tags = xml.xpath('//StUF:extraElementen', namespaces=self._namespaces)
        # add inner extraelementen elements to parent (take out in between container)
        for elem in elementen_tags:
            parent = elem.getparent()
            for child in elem.getchildren():
                parent.append(child)

        alltags = xml.xpath('//*', namespaces=self._namespaces)
        for elem in alltags:
            if f'{{{self._namespaces["xsi"]}}}nil' in elem.attrib:
                #  remove empty attributes
                elem.getparent().remove(elem)
            elif elem.tag == f'{{{self._namespaces["StUF"]}}}extraElementen':
                if elem.getparent().tag == 'persoon':
                    elem.getparent().remove(elem)
            else:
                #  keep element but remove all attributes
                self.check_and_fix_dates(elem)
                elem.attrib.clear()
                if elem.tag.endswith('}object'):
                    # this tag is the root of the actual response
                    # rename it to something more recognizable
                    elem.tag = 'persoon'
                if '}' in elem.tag:
                    #  remove all namespacing
                    ns = elem.tag.split('}')[0][1:]
                    tag = elem.tag.split('}')[1]
                    if '.' in tag:
                        # remove prefixes from tagnames (prfx.tagname->tagname)
                        elem.tag = '{' + ns + '}' + tag.split('.', 1)[-1]
                else:
                    if '.' in elem.tag:
                        # remove prefixes from tagnames (prfx.tagname->tagname)
                        elem.tag = elem.tag.split('.', 1)[-1]

        alltags = xml.xpath('//*', namespaces=self._namespaces)

        for elem in alltags:
            if elem.text is None and len(elem.getchildren()) == 0:
                #  remove empty leave nodes
                elem.getparent().remove(elem)
