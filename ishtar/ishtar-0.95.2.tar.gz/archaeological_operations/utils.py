#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# See the file COPYING for details.

DELIMITER = ";"
QUOTECHAR = '"'

import datetime
import re

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify

from django.contrib.auth.models import User
from ishtar_common.models import Town, Person, PersonType, OrganizationType, \
    Organization, SourceType
from archaeological_files.models import PermitType
from archaeological_operations.models import OperationType, Period, \
    ActType


def get_default_person():
    return User.objects.order_by('pk').all()[0]


def _get_parse_string(trunc_number=None):
    def parse_string(value):
        value = value.strip()
        if value == '#EMPTY':
            value = ''
        value = value.replace('  ', ' ')
        if trunc_number:
            value = value[:trunc_number]
        return value
    return parse_string

parse_string = _get_parse_string()


def parse_multivalue(value):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', value)
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    return re.sub('([0-9])([a-z])', r'\1 \2', s1)

ope_types = {}


def _init_ope_types():
    for k in settings.ISHTAR_OPE_TYPES.keys():
        ot, created = OperationType.objects.get_or_create(
            txt_idx=settings.ISHTAR_OPE_TYPES[k][0],
            defaults={'label': settings.ISHTAR_OPE_TYPES[k][1],
                      'preventive': k[0] == u'préventive'})
        ope_types[k] = ot


def parse_operationtype(value, preventive, owner):
    value = (preventive.strip(), value.strip())
    if not ope_types:
        _init_ope_types()
    if value not in ope_types:
        return None
    return ope_types[value]

periods = {}
periods_keys = []


def _init_period():
    for k in settings.ISHTAR_PERIODS.keys():
        periods[k] = Period.objects.get(txt_idx=settings.ISHTAR_PERIODS[k])
    periods_keys = periods.keys()
    periods_keys.sort(key=len)
    periods_keys.reverse()
    for k in settings.ISHTAR_PERIODS.keys():
        period = Period.objects.get(txt_idx=settings.ISHTAR_PERIODS[k])
        slug = slugify(period.label)
        period_names[slug] = period
        for k in REPLACED_PERIOD_DCT.keys():
            if k in slug:
                period_names[slug.replace(k, REPLACED_PERIOD_DCT[k])] = period
    period_names_keys = period_names.keys()
    period_names_keys.sort(key=len)
    period_names_keys.reverse()


def parse_period(value):
    value = parse_string(value)
    value = value[3:] if value.startswith('EUR') else value
    while value.endswith('-'):
        value = value[:-1]
    value = value[3:] if value.startswith('EUR') else value
    if not periods:
        _init_period()
    if not value:
        return [periods[u'']]
    period, old_val = [], u''
    while value and old_val != value:
        old_val = value
        for k in periods_keys:
            if value.startswith(k):
                period.append(periods[k])
                value = value[len(k):]
                break
    return period

_REPLACED_PERIOD = [('deuxieme', 'second')]
_REPLACED_PERIOD += [(y, x) for x, y in _REPLACED_PERIOD]
REPLACED_PERIOD_DCT = dict(_REPLACED_PERIOD)

period_names = {}
period_names_keys = {}


def parse_period_name(value):
    if not period_names:
        _init_period()
    value = parse_string(value)
    if not value:
        return [period_names[u'']]
    period, old_val = [], u''
    value = slugify(value)
    while value and old_val != value:
        old_val = value
        for k in period_names_keys:
            if value.startswith(k):
                period.append(period_names[k])
                value = value[len(k):]
                break
    return period

_CACHED_PERMIT_TYPES = {}


def _init_permit_type():
    for k in settings.ISHTAR_PERMIT_TYPES:
        txt_idx, label = settings.ISHTAR_PERMIT_TYPES[k]
        permit_type, created = PermitType.objects.get_or_create(
            txt_idx=txt_idx, defaults={'label': label,
                                       'available': True})
        _CACHED_PERMIT_TYPES[k] = permit_type


def parse_permittype(value):
    value = parse_string(value).lower()
    if not _CACHED_PERMIT_TYPES:
        _init_permit_type()
    if value not in _CACHED_PERMIT_TYPES:
        if "" not in _CACHED_PERMIT_TYPES:
            return
        value = ""
    return _CACHED_PERMIT_TYPES[value]

_CACHED_ADMIN_ACT_TYPES = {}


def parse_admin_act_typ(value, code, owner):
    value = parse_string(value).lower()
    code = parse_string(code).lower()
    if not value or not code:
        return
    if code not in _CACHED_ADMIN_ACT_TYPES:
        act_type, created = ActType.objects.get_or_create(
            txt_idx=code, defaults={'label': value})
        _CACHED_ADMIN_ACT_TYPES[code] = act_type
    return _CACHED_ADMIN_ACT_TYPES[code]


def parse_fileref(value):
    value = parse_string(value).split('/')[0]
    value = value.split('.')[0]
    match = re.search('[0-9].[0-9]*', value)
    if not match:
        return None
    return int(match.group())


def parse_orga(value, alternate_value, owner):
    value = parse_string(value)
    if not value:
        value = parse_string(alternate_value)
        if not value:
            return
    q = Organization.objects.filter(name__iexact=value)
    if q.count():
        return q.all()[0]
    try:
        organization_type = OrganizationType.objects.get(label__iexact=value)
    except ObjectDoesNotExist:
        organization_type = OrganizationType.objects.get(txt_idx='undefined')
    orga = Organization.objects.create(name=value,
                                       organization_type=organization_type,
                                       history_modifier=owner)
    return orga


def parse_bool(value):
    value = parse_string(value)
    if value.lower() in ('yes', 'oui'):
        value = True
    elif value.lower() in ('no', 'non'):
        value = False
    else:
        value = None
    return value


def parse_date(value):
    value = parse_string(value).split(' ')[0]
    try:
        return datetime.datetime.strptime(value, '%d/%m/%Y')
    except:
        return None


def parse_yearref(value):
    value = parse_string(value).split('.')[0]
    match = re.search('[0-9].[0-9]*', value)
    if not match:
        return None
    return int(match.group())


def parse_surface(value):
    value = parse_string(value)
    value = value.replace(',', '.')
    try:
        # hectare en metre carrés
        value = float(value) * 10000
        if value:
            return value
        return None
    except:
        return None


def parse_year(value):
    value = parse_string(value)
    try:
        yr = int(value)
    except:
        return None
    if yr < 1900 or yr > 2100:
        return None
    return yr


def parse_trunc_patriarche(value):
    value = parse_string(value)
    if not value:
        return
    value = value.replace(' ', '')
    try:
        int(value)
    except:
        return
    return '18' + unicode(value)


def parse_operation_code(value):
    value = parse_string(value)
    code = value.split('.')[-1]
    try:
        return int(code)
    except:
        return


def parse_title(value):
    value = parse_string(value)
    if not value:
        return
    return value.title()


def parse_name_surname(value):
    value = parse_string(value)
    items = value.split(' ')
    name = items[0]
    surname = ""
    if len(items) > 1:
        name = " ".join(items[:-1])
        surname = items[-1]
    values = {"surname": parse_title(surname)[:30],
              "name": parse_title(name)[:30]}
    if not values['surname'] and not values['name']:
        return
    q = Person.objects.filter(**values)
    if q.count():
        return q.all()[0]
    else:
        defaults = {'history_modifier': get_default_user(),
                    'title': ''}
        defaults.update(values)
        p = Person.objects.create(**defaults)
        p.person_types.add(PersonType.objects.get(
            txt_idx='head_scientist'))
        return p


def parse_person(surname, name, old_ref, owner):
    values = {"surname": parse_title(surname),
              "name": parse_title(name)}
    if not values['surname'] and not values['name']:
        return
    q = Person.objects.filter(**values)
    if q.count():
        return q.all()[0]
    else:
        defaults = {'history_modifier': owner,
                    'title': ''}
        defaults.update(values)
        p = Person.objects.create(**defaults)
        p.person_types.add(PersonType.objects.get(
            txt_idx='head_scientist'))
        return p


def parse_comment_addr_nature(nature, addr, owner):
    addr = parse_string(addr)
    nature = parse_string(nature)
    comments = []
    if nature:
        comments += [u"Aménagement :", nature]
    if addr:
        comments += [u"Adresse :", addr]
    if not comments:
        return ""
    return u"\n".join(comments)

# si pas de start date : premier janvier de year

ope_types = {
    'AET': ('other_study',
            'Autre étude', True),
    'APP': ('assistance_preparation_help',
            'Aide à la préparation de publication', True),
    'DOC': ('documents_study',
            'Étude documentaire', True),
    'EV': ('evaluation',
           "Fouille d'évaluation", True),
    'FOU': ('ancient_excavation',
            "Fouille ancienne", True),
    'FP': ('prog_excavation',
           "Fouille programmée", False),
    'MH': ('building_study', "Fouille avant MH", True),
    'OPD': ('arch_diagnostic',
            "Diagnostic archéologique", True),
    'PAN': ('analysis_program',
            "Programme d'analyses", False),
    'PCR': ('collective_research_project',
            "Projet collectif de recherche", False),
    'PMS': ('specialized_eqp_prospection',
            "Prospection avec matériel spécialisé", False),
    'PRD': ('diachronic_prospection',
            "Prospection diachronique", False),
    'PI': ('diachronic_prospection',
           "Prospection diachronique", False),
    'PRM': ('metal_detector_prospection',
            "Prospection détecteur de métaux", False),
    'PRT': ('thematic_prospection',
            "Prospection thématique", False),
    'PT': ('thematic_prospection',
           "Prospection thématique", False),
    'RAR': ('cave_art_record',
            "Relevé d'art rupestre", False),
    'SD': ('sampling_research',
           "Sondage", False),
    'SP': ('prev_excavation',
           "Fouille préventive", True),
    'SU': ('emergency_excavation',
           "Fouille préventive d'urgence", True),
}

_CACHED_OPE_TYPES = {}


def _prepare_ope_types():
    for k in ope_types.keys():
        txt_idx, label, preventive = ope_types[k]
        ot, created = OperationType.objects.get_or_create(
            txt_idx=txt_idx, defaults={'label': label,
                                       'preventive': preventive})
        if k not in _CACHED_OPE_TYPES.keys():
            _CACHED_OPE_TYPES[k] = ot


def parse_patriarche_operationtype(value):
    if value not in _CACHED_OPE_TYPES.keys():
        return None
    return _CACHED_OPE_TYPES[value]

_dpt_re_filter = re.compile('^\([0-9]*\) ')


def parse_ope_name(value):
    if not value:
        return ''
    value = value.strip()
    if value.lower() == 'null':
        return ''
    value = _dpt_re_filter.sub('', value)
    return value


def parse_ha(value):
    value = parse_string(value)
    try:
        value = float(value) * 10000
    except:
        value = None
    return value


def parse_rapp_index(value):
    value = parse_string(value)
    items = re.findall(r'[0-9]+$', value)
    if items:
        return int(items[-1])

_CACHED_DOC_TYPES = {}


def parse_doc_types(value):
    value = parse_string(value)
    if value not in _CACHED_DOC_TYPES:
        if value not in settings.ISHTAR_DOC_TYPES:
            return
        _CACHED_DOC_TYPES[value], created = SourceType.objects.get_or_create(
            txt_idx=value,
            defaults={"label": settings.ISHTAR_DOC_TYPES[value]})
    return _CACHED_DOC_TYPES[value]


def parse_insee(value):
    value = parse_string(value)
    values = []
    while len(value) > 4:
        values.append(value[:5])
        value = value[5:]
    towns = []
    for value in values:
        try:
            town = Town.objects.get(numero_insee=value)
            towns.append(town)
        except:
            # sys.stderr.write('Numero INSEE : %s non existant en base'
            # % value)
            continue
    return towns


PARCEL_YEAR_REGEXP = re.compile(r"^([0-9]{4})[ :]+")
PARCEL_SECTION_REGEXP = re.compile(
    ur"(?: )*(?:[Ss]ection(?:s)?)?(?: )*([A-Z][A-Z0-9]{0,3})[ :]*"
    ur"((?:(?: |;|,|[Pp]arcelle(?:s)?|n°|et|à|to)*[0-9]+[p]?)+)")
PARCEL_NB_RANGE_REGEXP = re.compile(ur'([0-9]+[p]?) (?:à|to) ([0-9]+[p]?)')
PARCEL_NB_REGEXP = re.compile(
    ur'(?: |;|,|[Pp]arcelle(?:s)?|n°|et|à|to)*([0-9]+[p]?)')


def parse_parcels(parcel_str, insee_code=None, owner=None):
    parcels, town = [], None
    if insee_code:
        town = parse_insee(insee_code)
        # manage only one town at a time
        assert len(town) < 2
        if not town:
            return parcels
        town = town[0]
    m = PARCEL_YEAR_REGEXP.match(parcel_str)
    year = None
    if m:
        year = m.groups()[0]
        parcel_str = parcel_str[m.span()[1]:]
    for parcel in PARCEL_SECTION_REGEXP.findall(parcel_str):
        sector, nums = parcel[0], parcel[1]
        for num in PARCEL_NB_REGEXP.findall(nums):
            if len(unicode(num)) > 6:
                continue
            dct = {'year': year, 'section': sector, 'parcel_number': num}
            if town:
                dct['town'] = town
            if owner:
                dct['history_modifier'] = owner
            parcels.append(dct)
        for parcel_ranges in PARCEL_NB_RANGE_REGEXP.findall(nums):
            lower_range, higher_range = parcel_ranges
            try:
                # the lower range itself has been already kept
                lower_range = int(lower_range) + 1
                higher_range = int(higher_range)
            except ValueError:
                continue
            for num in xrange(lower_range, higher_range):
                dct = {'year': year, 'section': sector,
                       'parcel_number': unicode(num)}
                if town:
                    dct['town'] = town
                if owner:
                    dct['history_modifier'] = owner
                parcels.append(dct)
    return parcels
