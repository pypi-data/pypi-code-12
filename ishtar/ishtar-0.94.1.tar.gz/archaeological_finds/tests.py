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

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from ishtar_common.models import ImporterType

from archaeological_finds import models

from archaeological_context_records.tests import ImportContextRecordTest

from ishtar_common import forms_common


class ImportFindTest(ImportContextRecordTest):
    test_context_records = False

    fixtures = ImportContextRecordTest.fixtures + [
        settings.ROOT_PATH +
        '../archaeological_finds/fixtures/initial_data-fr.json',
    ]

    def testMCCImportFinds(self, test=True):
        self.testMCCImportContextRecords(test=False)

        old_nb = models.BaseFind.objects.count()
        MCC = ImporterType.objects.get(name=u"MCC - Mobilier")
        mcc_file = open(
            settings.ROOT_PATH +
            '../archaeological_finds/tests/MCC-finds-example.csv', 'rb')
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
        ceram = models.MaterialType.objects.get(txt_idx='ceramic').pk
        self.setTargetKey('find__material_types', 'terre-cuite', ceram)
        impt.importation()
        if not test:
            return
        # new finds has now been imported
        current_nb = models.BaseFind.objects.count()
        self.assertTrue(current_nb == (old_nb + 4))
        self.assertEqual(
            models.Find.objects.filter(material_types__pk=ceram).count(), 4)
