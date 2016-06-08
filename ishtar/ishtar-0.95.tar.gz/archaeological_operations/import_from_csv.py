#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

"""
Utils: import archaelogical operation from a CSV file
"""

DELIMITER = ";"
QUOTECHAR = '"'

import datetime
import csv, codecs
import re

from django.conf import settings
from django.db import transaction
from django.template.defaultfilters import slugify

from archaeological_operations.utils import *

from django.contrib.auth.models import User
from ishtar_common.models import Town, Person, PersonType, OrganizationType, \
    Organization, SourceType
from archaeological_files.models import PermitType, File, FileType
from archaeological_operations.models import Operation, OperationType, Period, \
                            AdministrativeAct, ActType, OperationSource, Parcel

class Column:
    def __init__(self, col_models, format, associated_cols=None, multi=False):
        self.col_models, self.format = col_models, format
        self.associated_cols, self.multi = associated_cols, multi

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:

    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

# attrs, convert
DEFAULT_OPE_COLS = [
 [], # numéro de dossier ?
 (('operation_type',), parse_operationtype),
 (('common_name',), unicode),
 (('in_charge', 'name'), unicode),
 (('in_charge', 'surname'), unicode),
 [], # État ?
 [], # Adresse ?
 [], # origine ?
 (('periods',), parse_period),
 [], # Programme ?
 [], # Rattach PC ?
 [], # vide
 (('administrative_act', 'ref_sra'), unicode),
 (('administrative_act', 'signature_date'), parse_date),
 (('start_date',), parse_date),
 (('excavation_end_date',), parse_date),
 (('year',), parse_year),
 [], # identification
 (('code_patriarche',), int),
 [], # X degré
 [], # Y degré
 [], # X saisi ?
 [], # Y saisi ?
 [], # georef
 [], # geometrie
 (('surface',), parse_surface),
]

_OPE_COLS = settings.ISHTAR_OPE_COL_FORMAT if settings.ISHTAR_OPE_COL_FORMAT \
                                          else DEFAULT_OPE_COLS

OPE_COLS = []
for cols in _OPE_COLS:
    if cols:
        OPE_COLS.append(Column(*cols))
    else:
        OPE_COLS.append(None)

def ope_postimportfix(ope, dct):
    changed = False
    if not ope.year:
        sd = dct.get('start_date')
        ed = dct.get('end_date')
        if sd:
            ope.year = sd.year
            changed = True
        elif ed:
            ope.year = ed.year
            changed = True
    if changed:
        ope.save()
    return ope

class BreakIt(Exception):
    pass

class RelatedClass:
    def __init__(self, key, cls, default_data={}, reverse_key=False,
                 unique_keys=[], extra_data=[], mandatory_fields=[],
                 multi=None):
        self.key, self.cls, self.default_data = key, cls, default_data
        self.reverse_key, self.unique_keys = reverse_key, unique_keys
        self.extra_data, self.multi = extra_data, multi
        self.mandatory_fields = mandatory_fields

    def create_object(self, data):
        for mandatory_field in self.mandatory_fields:
            if not data.get(mandatory_field):
                return None
        if self.unique_keys:
            unique_data = {}
            for k in self.unique_keys:
                unique_data[k] = data.pop(k)
            created = False
            filtr = unique_data.copy()
            q = None
            # check if all condition have a value
            if not [k for k in filtr if not filtr[k]]:
                q = self.cls.objects.filter(**unique_data)
            if q and q.count() > 1:
                obj = q.all()[0]
            else:
                unique_data['defaults'] = data
                try:
                    obj, created = self.cls.objects.get_or_create(**unique_data)
                except ValueError:
                    return None
            if not created:
                for k in unique_data['defaults']:
                    try:
                        setattr(obj, k, unique_data['defaults'][k])
                    except ValueError:
                        continue
                obj.save()
        else:
            obj = self.cls.objects.create(**data)
        return obj

    def create(self, item, data, attr=None):
        datas = data
        if not self.multi:
            datas = [data]
        objs = []
        for data in datas:
            if self.reverse_key:
                data[self.reverse_key] = item
                if self.reverse_key not in self.unique_keys:
                    self.unique_keys.append(self.reverse_key)
                obj = self.create_object(data)
            else:
                obj = getattr(item, attr)
                if not obj:
                    obj = self.create_object(data)
                    setattr(item, attr, obj)
                    item.save()
                else:
                    for k in data:
                        setattr(obj, k, data[k])
                    obj.save()
            objs.append(obj)
        if not self.multi:
            return objs[0]
        return objs

#@transaction.commit_manually
def import_operations_csv(values, col_defs=OPE_COLS, update=True, person=None,
                      stdout=None, lines=None):
    default_person = person or User.objects.order_by('pk').all()[0]
    RELATED_CLASSES = [
        RelatedClass('administrative_act', AdministrativeAct,
                     default_data={'history_modifier':default_person,
                                     'act_type':ActType.objects.get(
                                            txt_idx='excavation_order')
                                     },
                     reverse_key='operation',
                     unique_keys=['ref_sra']),
        #RelatedClass('associated_file', File,
        #             extra_data=['year'],
        #             default_data={'history_modifier':default_person,
        #                           'file_type':FileType.objects.get(
        #                                        txt_idx='undefined')},
        #             unique_keys=['internal_reference', 'year']),
        RelatedClass('source', OperationSource, reverse_key='operation',
                     unique_keys=['index']),
        RelatedClass('parcels', Parcel, reverse_key='operation',
                     unique_keys=['operation', 'town', 'section',
                                  'parcel_number'],
                     multi=True),
    ]
    RELATED_CLASSES_KEYS = dict([(rel_cls.key, rel_cls)
                                   for rel_cls in RELATED_CLASSES])
    related_classes = RELATED_CLASSES_KEYS
    _prepare_ope_types()

    ope_default = {'history_modifier':default_person}
    new_ops = 0
    error_ope, error_reversed, error_multis = [], [], []
    multi_keys = set([column.col_models[0]
                      for column in col_defs if column and column.multi])

    restrict_lines = []
    start_line, end_line = None, None
    if lines:
        if '-' not in lines:
            restrict_lines = [int(line) for line in lines.split(',')]
        else:
            start_line, end_line = lines.split('-')
            start_line, end_line = int(start_line), int(end_line)+1
    if start_line:
        values = list(values)[start_line:]
    if end_line:
        values = list(values)[:end_line+1]
    for line_idx, vals in enumerate(values):
        if restrict_lines:
            if line_idx > max(restrict_lines):
                break
            if line_idx not in restrict_lines:
                continue
        if start_line:
            line_idx = line_idx + start_line
        if stdout:
            stdout.write("\r* line %d" % (line_idx))
        if not line_idx:
            continue # remove header
        args = {}
        for col_idx, val in enumerate(vals):
            if len(col_defs) <= col_idx or not col_defs[col_idx]:
                continue
            col_def = col_defs[col_idx]
            attrs, typ = col_def.col_models, col_def.format
            extra_cols = col_def.associated_cols
            if not callable(typ):
                if typ.startswith('parse_string_'):
                    typ = _get_parse_string(int(typ.split('_')[-1]))
                else:
                    typ = globals()[typ]
            c_args = args
            for attr in attrs:
                if attr not in c_args:
                    c_args[attr] = {}
                c_args = c_args[attr]
            try:
                if not extra_cols:
                        v = typ(val)
                else:
                    arguments = [vals[col_number] for col_number in extra_cols]
                    if not [arg for arg in arguments if arg]:
                        continue
                    arguments += [default_person]
                    v = typ(val, *arguments)
            except:
                v = None
            if len(attrs) == 1:
                args[attrs[0]] = v
            elif len(attrs) == 2:
                args[attrs[0]][attrs[1]] = v
            elif len(attrs) == 3:
                args[attrs[0]][attrs[1]][attrs[2]] = v
        # manage exploded dates
        for k in args.keys():
            if '__year' in k:
                key = k[:-len('__year')]
                try:
                    v = datetime.datetime(args[k], args[key+'__month'],
                                          args[key+'__day'])
                    args[key] = v
                except:
                    pass
                args.pop(k)
                args.pop(key+'__month')
                args.pop(key+'__day')
        related_items = []
        multis = []
        attached_models = {}
        for k in args.keys():
            try:
                if k in related_classes:
                    rel_cls = related_classes[k]
                    cls, default = rel_cls.cls, rel_cls.default_data
                    reverse_key = rel_cls.reverse_key
                    values = None
                    if rel_cls.multi:
                        values = []
                        for v in args[k]:
                            v.update(default)
                            values.append(v)
                    else:
                        values = default.copy()
                        values.update(args[k])
                    exited = False
                    for extra in rel_cls.extra_data:
                        if not args.get(extra):
                            raise BreakIt
                        values[extra] = args[extra]
                    args.pop(k)
                    related_items.append((rel_cls, values, k))
                elif k in multi_keys:
                    multis.append((k, args[k]))
                    args.pop(k)
                elif '__' in k:
                    mod, value = k.split('__')
                    attached_models[(mod, value)] = args.pop(k)
            except BreakIt:
                args.pop(k)
                continue
        op = None
        if not args.get('operation_type'):
            #print "Pas d'operation_type"
            continue
        #transaction.commit()
        try:
            int(args['code_patriarche'])
        except ValueError:
            continue
        q = Operation.objects.filter(code_patriarche=args['code_patriarche'])
        if q.count():
            if not update:
                #print "Code patriarche existant"
                continue
            op = q.all()[0]
        # check
        if not args.get('year') and args.get('start_date'):
            args['year'] = args['start_date'].year
        # creation
        """
        print "args", args
        print "multis", multis
        print "attached_models", attached_models
        """
        if not op:
            args.update(ope_default)
            #if not args.get('operation_code'):
            #    args['operation_code'] = Operation.get_available_operation_code(
            #                                                    args['year'])
            #try:
            op = Operation.objects.create(**args)
            #op.save()
            new_ops += 1
            #except:
            #    error_ope.append((line_idx, args))
            #    transaction.rollback()
            #    continue
            #transaction.commit()
        else: # mise à jour
            try:
                for k in args:
                    if getattr(op, k):
                        continue
                    setattr(op, k, args[k])
                op.save()
            except:
                #transaction.rollback()
                continue
            #transaction.commit()
        try:
            for k, vals in multis:
                if not vals:
                    continue
                for v in vals:
                    getattr(op, k).add(v)
                    op.save()
        except:
            #transaction.rollback()
            error_multis.append((line_idx, multis))
        for attr, attached_attr in attached_models:
            field = getattr(op, attr)
            if field:
                setattr(field, attached_attr, attached_models[(attr,
                                                               attached_attr)])
                field.save()
        #transaction.commit()
        for rel_cls, data, attr in related_items:
            rel_cls.create(op, data, attr)
            #try:
            #    rel_cls.create(op, data, attr)
            #except:
            #    error_reversed.append((line_idx, data))
        ope_postimportfix(op, args)
        #transaction.commit()

    errors = []
    if error_ope:
        error = "Error while recording these operations:\n"
        for line_idx, args in error_ope:
            error += "line: " + str(line_idx) + " args: " + str(args) + '\n'
        errors.append(error)
    if error_multis:
        error = "Error while recording these multiples items attached to "\
                "operation:"
        for line_idx, args in error_multis:
            error += "line: " + str(line_idx) + " args: " + str(args) + '\n'
        errors.append(error)
    if error_reversed:
        error = "Error while recording these items that depend to operation:"
        for line_idx, args in error_reversed:
            error += "line: " + str(line_idx) + " args: " + str(args) + '\n'
        errors.append(error)
    #transaction.commit()
    return new_ops, errors

def import_from_csv(filename, update=True, col_defs=OPE_COLS,
                    person=None, stdout=None, lines=None):
    """
    Import from a CSV file.
    Return number of operation treated and errors.
    """
    try:
        values = unicode_csv_reader(codecs.open(filename, 'rb', "utf-8"),
                        delimiter=DELIMITER, quotechar=QUOTECHAR)
    except (IOError):
        return 0, [u"Incorrect CSV file."]

    new_ops, errors = import_operations_csv(values, col_defs=col_defs,
                                    update=update, person=person, stdout=stdout,
                                    lines=lines)
    return new_ops, errors
