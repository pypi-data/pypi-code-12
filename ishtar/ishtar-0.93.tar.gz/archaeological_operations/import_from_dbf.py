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

"""
Utils: import archaelogical operation from a DBF file
"""

from __future__ import unicode_literals

import datetime
import dbf
import re

from django.contrib.auth.models import User
from django.db import transaction

from archaeological_operations.import_from_csv import parse_operationtype, \
                    parse_multivalue, parse_person as _parse_person, parse_date,\
    Column, parse_patriarche_operationtype, parse_ope_name
from archaeological_operations.models import Operation, OperationType, Period, \
                                             AdministrativeAct, ActType

def parse_person(surname, name, owner):
    return _parse_person(surname, name, None, owner)

def parse_ha(value):
    try:
        val = float(value)
    except ValueError:
        val = 0
    return val * 10000

period_types = {
    '':'not_yet_documented',
    'IND':'indetermined',
    'CON': 'contemporan',
    'MOD': 'modern',
    'REC': 'recent_times',
    'BMA': 'low_middle_age',
    'MAC': 'classic_middle_age',
    'HMA': 'high_middle_age',
    'MA' : 'middle_age',
    'MED': 'middle_age',
    'BAS': 'low_empire',
    'HAU': 'high-empire',
    'NRE': 'republic',
    'GAL': 'gallo-roman',
    'FE2': 'second_iron_age',
    'FE1': 'first_iron_age',
    'BRF': 'final_bronze_age',
    'BRM': 'middle_bronze_age',
    'BRA': 'old_bronze_age',
    'FER': 'iron_age',
    'BRO': 'bronze_age',
    'PRO': 'protohistory',
    'NEF': 'final_neolithic',
    'NER': 'recent_neolithic',
    'NEM': 'middle_neolithic',
    'NEA': 'old_neolithic',
    'NEO': 'neolithic',
    'MER': 'recent_mesolithic',
    'MEM': 'middle_mesolithic',
    'MEA': 'old_mesolithic',
    'MES': 'mesolithic',
    'PAF': 'final_paleolithic',
    'PAS': 'late_paleolithic',
    'PAM': 'middle_paleolithic',
    'PAA': 'ancien_paleolithic',
    'PAL': 'paleolithic'
}

_CACHED_PERIOD_TYPES = {}

def _prepare_period_types():
    for k in period_types.keys():
        _CACHED_PERIOD_TYPES[k] = Period.objects.get(txt_idx=period_types[k])

_period_re_filter = re.compile('^EUR')
_period2_re_filter = re.compile('-*$')

def parse_period(value):
    value = _period_re_filter.sub('', value)
    value = _period2_re_filter.sub('', value)
    if value not in _CACHED_PERIOD_TYPES.keys():
        value = ''
    return _CACHED_PERIOD_TYPES[value]

PATRIARCHE_DBF_OPE_COLS = [
    Column(('operation_type',), 'parse_patriarche_operationtype'),
    Column(('common_name',), 'parse_ope_name'),
    [],
    Column(('in_charge',), 'parse_person', [2]),
    [],  # 'etat'
    Column(('comment',), unicode),  #'adresse'
    [],  #'origine C(3)'
    Column(('periods',), 'parse_period', multi=True),
    [],  #'programme C(254)'
    [],  # 'rattach_pc C(254)'
    [],  # 'code_dossi N(8,0)'
    Column(('administrative_act', 'ref_sra'), unicode),
    Column(('administrative_act', 'signature_date'), parse_date),
    Column(('start_date',), parse_date),
    Column(('end_date',), parse_date),
    Column(('year',), int, []),
    [],  # 'identifica C(254)'
    Column(('code_patriarche',), int),
    [],  # 'x_degre N(16,6)'),
    [],  # 'y_degre N(16,6)'),
    [],  # 'x_saisi C(12)'),
    [],  # 'y_saisi C(12)'),
    [],  # 'georeferen C(3)'),
    [],  # 'geometrie C(3)'),
    Column(('surface',), parse_ha)
]

DBF_OPE_COLS = PATRIARCHE_DBF_OPE_COLS

def import_from_dbf(filename, update=False, col_defs=DBF_OPE_COLS,
                    person=None, stdout=None):
    """
    Import from a DBF file.
    Return number of operation treated and errors.
    """
    try:
        table =  dbf.Table(filename)
    except (dbf.DbfError, TypeError):
        return 0, ["Incorrect DBF file."]

    new_ops, errors = import_operations_dbf(table, col_defs=col_defs,
                                    update=update, person=person, stdout=stdout)
    return new_ops, errors

ERROR_LBLS = {'missing_ope_type':'* Missing operation type: ',
              'missing_patriarche_code':'* Missing patriarche code: '}

@transaction.commit_manually
def import_operations_dbf(values, col_defs=DBF_OPE_COLS, update=False,
                          person=None, stdout=None):
    default_person = person or User.objects.order_by('pk').all()[0]
    # key : (class, default, reverse)
    key_classes = {
    'administrative_act':(AdministrativeAct, {'history_modifier':default_person,
                           'act_type':ActType.objects.get(
                                      txt_idx='excavation_order')}, 'operation'),
    }
    _prepare_ope_types()
    _prepare_period_types()

    ope_default = {'history_modifier':default_person}
    current_import = []
    new_ops = 0
    errors_nb = {}
    for error in ERROR_LBLS.keys():
        errors_nb[error] = 0
    error_ope, error_reversed, error_multis = [], [], []
    multi_keys = set([column.col_models[0]
                      for column in col_defs if column and column.multi])
    for line_idx, vals in enumerate(values):
        if stdout:
            stdout.write("\r* line %d" % (line_idx))
        args = {}
        for col_idx, val in enumerate(vals):
            if len(col_defs) <= col_idx or not col_defs[col_idx]:
                continue
            col_def = col_defs[col_idx]
            attrs, typ = col_def.col_models, col_def.format
            extra_cols = col_def.associated_cols
            if not callable(typ):
                typ = globals()[typ]
            c_args = args
            for attr in attrs:
                if attr not in c_args:
                    c_args[attr] = {}
                c_args = c_args[attr]
            if not extra_cols:
                try:
                    v = typ(val)
                except TypeError:
                    v = None
            else:
                arguments = [vals[col_number] for col_number in extra_cols]
                if not [arg for arg in arguments if arg]:
                    continue
                arguments += [default_person]
                v = typ(val, *arguments)
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
        reversed_items, multis = [], []
        for k in args.keys():
            if k in key_classes:
                cls, default, reverse = key_classes[k]
                default.update(args[k])
                if reverse:
                    reversed_items.append((cls, default, reverse))
                    args.pop(k)
                    continue
                try:
                    obj = cls.objects.get(**default)
                except:
                    obj = cls.objects.create(**default)
                    obj.save()
                transaction.commit()
                args[k] = obj
            elif type(args[k]) == list or k in multi_keys:
                multis.append((k, args[k]))
                args.pop(k)
        op = None
        if not update and not args.get('operation_type'):
            errors_nb['missing_ope_type'] += 1
            continue
        try:
            op = Operation.objects.get(code_patriarche=args['code_patriarche'])
            if not update and op.pk not in current_import:
                errors_nb['already_available_patriarche_code'] += 1
                continue
        except:
            pass
        # check
        if not args.get('year') and args.get('start_date'):
            args['year'] = args['start_date'].year
        updated = False
        # creation
        if not op:
            args.update(ope_default)
            for k in args.keys():
                if not args[k]:
                    args.pop(k)
            op = Operation.objects.create(**args)
            new_ops += 1
            transaction.commit()
        else: # mise à jour
            try:
                for k in args:
                    if not args[k]:
                        args[k] = None
                    #if getattr(op, k):
                    #    continue
                    setattr(op, k, args[k])
                op.save()
            except:
                transaction.rollback()
                continue
            transaction.commit()
            updated = True
        try:
            for cls, default, reverse in reversed_items:
                default[reverse] = op
                it = cls(**default).save()
        except:
            transaction.rollback()
            current_import.append(op.pk)
            error_reversed.append((line_idx, reversed_items))
            continue
        transaction.commit()
        try:
            for k, vals in multis:
                if op.pk not in current_import and updated:
                    getattr(op, k).clear()
                if type(vals) not in (list, tuple):
                    vals = [vals]
                for v in vals:
                    getattr(op, k).add(v)
                    op.save()
        except:
            transaction.rollback()
            current_import.append(op.pk)
            error_multis.append((line_idx, multis))
            continue
        transaction.commit()
        current_import.append(op.pk)

    errors = []
    for error_key in errors_nb:
        nb_error = errors_nb[error_key]
        if nb_error:
            errors.append(ERROR_LBLS[error_key] + str(nb_error))
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
    return new_ops, errors

