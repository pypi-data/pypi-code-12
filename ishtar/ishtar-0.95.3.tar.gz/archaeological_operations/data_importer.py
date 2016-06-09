#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

import re

from django.db import IntegrityError
from django.template.defaultfilters import slugify

from ishtar_common.data_importer import *
from ishtar_common.models import Town, OrganizationType, SourceType, \
    SupportType, Format, AuthorType

from archaeological_operations import models
from archaeological_operations.forms import OPERATOR
from archaeological_operations.utils import parse_parcels

RE_PERMIT_REFERENCE = re.compile('[A-Za-z]*(.*)')


class ImportParcelFormater(ImportFormater):
    NEED = ['town', ]
    PARCEL_OWNER_KEY = 'associated_file'

    def post_process(self, obj, context, value, owner=None):
        value = value.strip()
        base_dct = {self.PARCEL_OWNER_KEY: obj, 'history_modifier': owner}
        if 'parcels' in context:
            for key in context['parcels']:
                if context['parcels'][key]:
                    base_dct[key] = context['parcels'][key]
        for parcel_dct in parse_parcels(value, owner=owner):
            parcel_dct.update(base_dct)
            try:
                models.Parcel.objects.get_or_create(**parcel_dct)
            except IntegrityError:
                try:
                    p = unicode(parcel_dct)
                except UnicodeDecodeError:
                    try:
                        p = str(parcel_dct).decode('utf-8')
                    except UnicodeDecodeError:
                        p = u""
                raise ImporterError(u"Erreur d'import parcelle, contexte : %s"
                                    % p)


class ImportYearFormater(ImportFormater):
    def post_process(self, obj, context, value, owner=None):
        value = self.formater.format(value)
        if not value:
            return
        obj.year = value.year
        obj.save()


class TownFormater(Formater):
    def __init__(self, town_full_dct={}, town_dct={}):
        self._town_full_dct = town_full_dct
        self._town_dct = town_dct
        self._initialized = False if not self._town_full_dct else True

    def town_dct_init(self):
        for town in Town.objects.all():
            key = (slugify(town.name.strip()), town.numero_insee[:2])
            if key in self._town_full_dct:
                # print("Danger! %s is ambiguous with another town on the same"
                #       " department." % town.name)
                continue
            self._town_full_dct[key] = town
            key = slugify(town.name.strip())
            if key in self._town_dct:
                # print("Warning %s is ambiguous with no department provided" %
                #       town.name)
                continue
            self._town_dct[key] = town
            self._initialized = True

    def format(self, value, extra=None):
        if not self._initialized:
            self.town_dct_init()
        m = RE_FILTER_CEDEX.match(value)
        if m:
            value = m.groups()[0]
        if not value:
            return None
        if extra:
            key = (slugify(value), extra)
            if key in self._town_full_dct:
                return self._town_full_dct[key]
        key = slugify(value)
        if key in self._town_dct:
            return self._town_dct[key]


class TownINSEEFormater(Formater):
    def __init__(self):
        self._town_dct = {}

    def format(self, value, extra=None):
        value = value.strip()
        if not value:
            return None
        if value in self._town_dct:
            return self._town_dct[value]
        q = Town.objects.filter(numero_insee=value)
        if not q.count():
            return
        self._town_dct[value] = q.all()[0]
        return self._town_dct[value]


class SurfaceFormater(Formater):
    def test(self):
        assert self.format(u"352 123") == 352123
        assert self.format(u"456 789 m²") == 456789
        assert self.format(u"78ha") == 780000

    def format(self, value, extra=None):
        value = value.strip()
        if not value:
            return None
        factor = 1
        if value.endswith(u"m2") or value.endswith(u"m²"):
            value = value[:-2]
        if value.endswith(u"ha"):
            value = value[:-2]
            factor = 10000
        try:
            return int(value.replace(' ', '')) * factor
        except ValueError:
            raise ImporterError("Erreur import surface : %s" % unicode(value))

# RE_ADD_CD_POSTAL_TOWN = re.compile("(.*)[, ](\d{5}) (.*?) *(?: "\
#                                    "*CEDEX|cedex|Cedex *\d*)*")

RE_NAME_ADD_CD_POSTAL_TOWN = re.compile(
    "(.+)?[, ]*" + NEW_LINE_BREAK + "(.+)?[, ]*(\d{2} *\d{3})[, ]*(.+)")

RE_ADD_CD_POSTAL_TOWN = re.compile("(.+)?[, ]*(\d{2} *\d{3})[, ]*(.+)")

RE_CD_POSTAL_FILTER = re.compile("(\d*) (\d*)")

RE_ORGA = re.compile("([^,\n]*)")


class OperationImporterBibracte(Importer):
    OBJECT_CLS = models.Operation
    DESC = u"Exports Bibracte : importeur pour l'onglet opération"
    DEFAULTS = {
        ('operator',): {
            'organization_type': OPERATOR
        },
    }
    LINE_FORMAT = [
        # CODE OPE
        ImportFormater('operation_code', IntegerFormater(),),
        # REGION
        None,
        # TYPE operation
        ImportFormater('operation_type', TypeFormater(models.OperationType),),
        # NOM
        ImportFormater('common_name', UnicodeFormater(120),),
        # OPERATEUR
        ImportFormater('operator__name', UnicodeFormater(120),),
        # resp. lien IMPORT avec personne
        ImportFormater('in_charge__raw_name', UnicodeFormater(300),),
        # début
        ImportFormater('start_date', DateFormater(['%Y/%m/%d']),),
        # fin
        ImportFormater('excavation_end_date', DateFormater(['%Y/%m/%d']),),
        # Chronos
        ImportFormater('periods', TypeFormater(models.Period, many_split="&"),
                       required=False),
    ]

RE_PARCEL_SECT_NUM = re.compile("([A-Za-z]*)([0-9]*)")
RE_NUM_INSEE = re.compile("([0-9]*)")


class ParcelImporterBibracte(Importer):
    OBJECT_CLS = models.Parcel
    DESC = u"Exports Bibracte : importeur pour l'onglet parcelles"
    DEFAULTS = {
        ('operator',): {
            'organization_type': OrganizationType.objects.get(
                txt_idx="operator")},
    }
    LINE_FORMAT = [
        # code OA
        ImportFormater('operation__operation_code', IntegerFormater(),),
        # identifiant parcelle
        ImportFormater(
            ['section', 'parcel_number'],
            [UnicodeFormater(4), UnicodeFormater(6), ],
            regexp=RE_PARCEL_SECT_NUM,
            regexp_formater_args=[[0], [1]], required=False,
            duplicate_fields=[('external_id', False)],),
        # numero parcelle
        ImportFormater('parcel_number', UnicodeFormater(6),
                       required=False,),
        # section cadastre
        ImportFormater('section', UnicodeFormater(4),
                       required=False,),
        # annee cadastre
        ImportFormater('year', YearFormater(), required=False,),
        # nom commune
        None,
        # numero INSEE commune
        ImportFormater('town__numero_insee', UnicodeFormater(6),
                       regexp=RE_NUM_INSEE, required=False,),
        # nom departement
        None,
        # lieu dit adresse
        ImportFormater('address', UnicodeFormater(500),
                       required=False,),
    ]

MAIN_AUTHOR, created = AuthorType.objects.get_or_create(txt_idx='main_author')


class DocImporterBibracte(Importer):
    OBJECT_CLS = models.OperationSource
    DEFAULTS = {
        ('authors',): {'author_type': MAIN_AUTHOR},
    }
    DESC = u"Exports Bibracte : importeur pour l'onglet documentation"
    LINE_FORMAT = [
        # code OA
        ImportFormater('operation__operation_code', IntegerFormater(),),
        # identifiant documentation
        ImportFormater('external_id', UnicodeFormater(12),),
        # type
        ImportFormater('source_type', TypeFormater(SourceType),
                       required=False),
        # nature support
        ImportFormater('support_type', TypeFormater(SupportType),
                       required=False),
        # nombre element
        ImportFormater('item_number', IntegerFormater(), required=False),
        # auteur
        ImportFormater('authors__person__raw_name', UnicodeFormater(300),
                       required=False),
        # annee
        ImportFormater('creation_date', DateFormater(['%Y']),),
        # format
        ImportFormater('format_type', TypeFormater(Format), required=False),
        # description legende
        ImportFormater('description', UnicodeFormater(1000), required=False),
        # type contenant
        None,
        # numero contenant
        None,
        # commentaire
        ImportFormater('comment', UnicodeFormater(1000), required=False),
        # echelle
        ImportFormater('scale', UnicodeFormater(30), required=False),
        # type sous contenant
        None,
        # numero sous contenant
        None,
        # informations complementaires
        ImportFormater('additional_information', UnicodeFormater(1000),
                       required=False),
    ]
