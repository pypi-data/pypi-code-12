#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
Unit tests
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ishtar_common.models import ImporterType
from archaeological_operations.tests import OperationInitTest, \
    ImportOperationTest
from archaeological_context_records import models
from ishtar_common import forms_common


class ImportContextRecordTest(ImportOperationTest):
    test_operations = False
    test_context_records = True

    fixtures = ImportOperationTest.fixtures + [
        settings.ROOT_PATH +
        '../archaeological_context_records/fixtures/initial_data-fr.json',
    ]

    def testMCCImportContextRecords(self, test=True):
        if test and not self.test_context_records:
            return
        self.testMCCImportParcels(test=False)

        old_nb = models.ContextRecord.objects.count()
        MCC = ImporterType.objects.get(name=u"MCC - UE")
        mcc_file = open(
            settings.ROOT_PATH +
            '../archaeological_context_records/tests/'
            'MCC-context-records-example.csv', 'rb')
        file_dict = {'imported_file': SimpleUploadedFile(mcc_file.name,
                                                         mcc_file.read())}
        post_dict = {'importer_type': MCC.pk, 'skip_lines': 1,
                     "encoding": 'utf-8'}
        form = forms_common.NewImportForm(data=post_dict, files=file_dict,
                                          instance=None)
        form.is_valid()
        if test:
            self.assertTrue(form.is_valid())
        impt = form.save(self.ishtar_user)
        impt.initialize()

        # doing manual connections
        hc = models.Unit.objects.get(txt_idx='not_in_context').pk
        self.setTargetKey('unit', 'hc', hc)
        self.setTargetKey('unit', 'hors-contexte', hc)
        layer = models.Unit.objects.get(txt_idx='layer').pk
        self.setTargetKey('unit', 'couche', layer)

        impt.importation()
        if not test:
            return

        # new ues has now been imported
        current_nb = models.ContextRecord.objects.count()
        self.assertTrue(current_nb == (old_nb + 4))
        self.assertEqual(
            models.ContextRecord.objects.filter(unit__pk=hc).count(), 3)
        self.assertEqual(
            models.ContextRecord.objects.filter(unit__pk=layer).count(), 1)


class ContextRecordInit(OperationInitTest):
    test_operations = False

    def create_context_record(self, user=None, data={}):
        if not getattr(self, 'context_records', None):
            self.context_records = []

        default = {'label': "Context record"}
        if not data.get('operation'):
            data['operation'] = self.get_default_operation()
        if not data.get('parcel'):
            data['parcel'] = self.get_default_parcel()
        if not data.get('history_modifier'):
            data['history_modifier'] = self.get_default_user()

        default.update(data)
        self.context_records.append(models.ContextRecord.objects.create(
            **default))
        return self.context_records

    def get_default_context_record(self):
        return self.create_context_record()[0]


class RecordRelationsTest(TestCase, ContextRecordInit):
    fixtures = [settings.ROOT_PATH +
                '../fixtures/initial_data.json',
                settings.ROOT_PATH +
                '../ishtar_common/fixtures/initial_data.json',
                settings.ROOT_PATH +
                '../archaeological_files/fixtures/initial_data.json',
                settings.ROOT_PATH +
                '../archaeological_operations/fixtures/initial_data-fr.json']
    model = models.ContextRecord

    def setUp(self):
        # two different context records
        self.create_context_record({"label": u"CR 1"})
        self.create_context_record({"label": u"CR 2"})

    def testRelations(self):
        sym_rel_type = models.RelationType.objects.create(
            symmetrical=True, txt_idx='sym')
        rel_type_1 = models.RelationType.objects.create(
            symmetrical=False, txt_idx='rel_1')
        # cannot be symmetrical and have an inverse_relation
        with self.assertRaises(ValidationError):
            rel_test = models.RelationType.objects.create(
                symmetrical=True, inverse_relation=rel_type_1, txt_idx='rel_3')
            rel_test.full_clean()
        # auto fill inverse relations
        rel_type_2 = models.RelationType.objects.create(
            symmetrical=False, inverse_relation=rel_type_1, txt_idx='rel_2')
        self.assertEqual(rel_type_1.inverse_relation, rel_type_2)

        cr_1 = self.context_records[0]
        cr_2 = self.context_records[1]

        # inserting a new symmetrical relation automatically creates the same
        # relation for the second context record
        rel = models.RecordRelations.objects.create(
            left_record=cr_1, right_record=cr_2, relation_type=sym_rel_type)
        self.assertEqual(models.RecordRelations.objects.filter(
            left_record=cr_2, right_record=cr_1,
            relation_type=sym_rel_type).count(), 1)

        # removing one symmetrical relation removes the other
        rel.delete()
        self.assertEqual(models.RecordRelations.objects.filter(
            left_record=cr_2, right_record=cr_1,
            relation_type=sym_rel_type).count(), 0)

        # for non-symmetrical relation, adding one relation automatically
        # adds the inverse
        rel = models.RecordRelations.objects.create(
            left_record=cr_1, right_record=cr_2, relation_type=rel_type_1)
        self.assertEqual(models.RecordRelations.objects.filter(
            left_record=cr_2, right_record=cr_1,
            relation_type=rel_type_2).count(), 1)
