#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
import json, datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from ishtar_common.models import PersonType, Town
from archaeological_files import models
from archaeological_operations.models import Parcel, ParcelOwner
from archaeological_operations.tests import OperationInitTest

class FileInit(object):
    def login_as_superuser(self):
        self.client.login(username='username', password='tralala')

    def create_file(self):
        self.extra_models, self.model_list = {}, []
        self.user, created = User.objects.get_or_create(username='username',
                                                        is_superuser=True)
        self.user.set_password('tralala')
        self.user.save()
        self.o_user, created = User.objects.get_or_create(username='ousername')
        person_type = PersonType(label=u'Test person type',
                                 txt_idx='test_person', available=True)
        person_type.save()
        self.extra_models['person_type'] = person_type
        self.model_list.append(person_type)

        person = models.Person(title='Mr', surname='Surname', name='Name',
                               history_modifier=self.o_user)
        person.save()
        self.extra_models['person'] = person
        self.model_list.append(person)

        file_type = models.FileType(label=u'Test file type',
                                    txt_idx='test_file', available=True)
        file_type.save()
        self.extra_models['file_type'] = file_type
        self.model_list.append(file_type)

        dct = {'year':2010, 'numeric_reference':1000, 'file_type':file_type,
               'internal_reference':u'UNIT_testÉ ?', 'in_charge':person,
               'history_modifier':self.o_user, 'total_surface':10000}
        self.item = self.model(**dct)
        self.item.save()

class FileTest(TestCase, FileInit):
    fixtures = [settings.ROOT_PATH + \
                '../fixtures/initial_data-auth-fr.json',
                settings.ROOT_PATH + \
                '../ishtar_common/fixtures/initial_data-fr.json']
    model = models.File

    def setUp(self):
        self.create_file()

    def testAddAndGetHistorized(self):
        """
        Test correct new version and correct access to history
        """
        nb_hist = self.item.history.count()
        self.assertTrue(self.item.history.count() >= 1)
        base_label = self.item.internal_reference
        self.item.internal_reference = u"Unité_Test"
        self.item.history_modifier = self.user
        self.item.save()
        self.failUnlessEqual(self.item.history.count(), nb_hist+1)
        self.failUnlessEqual(self.item.history.all()[1].internal_reference,
                             base_label)
        self.item.internal_reference = u"Unité_Testée"
        self.item.history_modifier = self.user
        self.item.skip_history_when_saving = True
        self.item.save()
        self.item.skip_history_when_saving = False
        self.failUnlessEqual(self.item.history.count(), nb_hist+1)

    def testCreatorHistorized(self):
        """
        Test creator association
        """
        self.failUnlessEqual(self.item.history_creator, self.o_user)
        altuser, created = User.objects.get_or_create(username='altusername')
        self.item.internal_reference = u"Unité_Test"
        self.item.history_modifier = altuser
        self.item.save()
        self.failUnlessEqual(self.item.history_creator, self.o_user)

    def testIntelligentHistorisation(self):
        """
        Test that two identical version are not recorded twice in the history
        and that multiple saving in a short time are not considered
        """
        nb_hist = self.item.history.count()
        self.item.internal_reference = u"Unité_Test"
        self.item.history_modifier = self.user
        self.item.save()
        self.failUnlessEqual(self.item.history.count(), nb_hist+1)
        nb_hist = self.item.history.count()
        self.item.save()
        self.failUnlessEqual(self.item.history.count(), nb_hist)

    def testRollbackFile(self):
        nb_hist = self.item.history.count()
        initial_values = self.item.values()
        backup_date = self.item.history.all()[0].history_date
        self.item.internal_reference = u"Unité_Test"
        self.item.history_modifier = self.user
        self.item.save()
        self.item.rollback(backup_date)
        self.failUnlessEqual(self.item.history.count(), nb_hist)
        new_values = self.item.values()
        for k in initial_values.keys():
            self.assertTrue(k in new_values)
            self.assertEqual(new_values[k], initial_values[k],
                        msg=u"for %s: %s != %s" % (k, unicode(new_values[k]),
                                                   unicode(initial_values[k])))

    def testRESTGetFile(self):
        response = self.client.post('/get-file/',
                             {'numeric_reference':self.item.numeric_reference})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # not allowed -> no data
        self.assertTrue(not data)

        self.login_as_superuser()
        response = self.client.post('/get-file/',
                             {'numeric_reference':self.item.numeric_reference})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('records' in data)
        self.assertTrue(data['records'] == 1)

    def testRESTGetOldFile(self):
        initial_ref = self.item.internal_reference
        new_ref = u"Unité_Test_old_file"
        new_ref = initial_ref != new_ref and new_ref or new_ref + u"extra"
        self.item.internal_reference = new_ref
        self.item.history_modifier = self.user
        self.item.save()
        response = self.client.post('/get-file/',
                     {'numeric_reference':self.item.numeric_reference, 'old':1})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # not allowed -> no data
        self.assertTrue(not data)

        self.login_as_superuser()
        response = self.client.post('/get-file/',
                     {'numeric_reference':self.item.numeric_reference, 'old':1})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('records' in data)
        self.assertTrue(data['records'] == 1)
        self.assertEqual(data['rows'][0]['internal_reference'], initial_ref)

#class ImporterTest(TestCase):
#    def testFormaters(self):
#        from archaeological_files import data_importer
#        for formater in [data_importer.SurfaceFormater]:
#            formater().test()

class FileOperationTest(TestCase, OperationInitTest, FileInit):
    model = models.File
    fixtures = [settings.ROOT_PATH + \
                '../fixtures/initial_data-auth-fr.json',
                settings.ROOT_PATH + \
                '../ishtar_common/fixtures/initial_data-fr.json',
                settings.ROOT_PATH +
                '../ishtar_common/fixtures/test_towns.json',
                settings.ROOT_PATH +
                '../ishtar_common/fixtures/initial_importtypes-fr.json',
                settings.ROOT_PATH +
                '../archaeological_files/fixtures/initial_data.json',
                settings.ROOT_PATH +
                '../archaeological_operations/fixtures/initial_data-fr.json']

    def setUp(self):
        self.create_file()
        self.orgas = self.create_orgas(self.user)
        self.operations = self.create_operation(self.user, self.orgas[0])
        self.operation = self.operations[0]

    def testFileAssociation(self):
        # parcel association
        default_town = Town.objects.all()[0]
        for p in range(0, 10):
            parcel = Parcel.objects.create(parcel_number=unicode(p),
                                     section='YY',
                                     town=default_town,
                                     operation=self.operation)
            if p == 1:
                ParcelOwner.objects.create(
                        owner=self.extra_models['person'],
                        parcel=parcel, start_date=datetime.date.today(),
                        end_date=datetime.date.today())
        initial_nb = self.item.parcels.count()
        # no parcel on the file -> new parcels are copied from the
        # operation
        self.operation.associated_file = self.item
        self.operation.save()
        self.assertEqual(self.item.parcels.count(), initial_nb+10)
        # parcel owner well attached
        q = ParcelOwner.objects.filter(parcel__associated_file=self.item)
        self.assertEqual(q.count(), 1)

        # when attaching parcel from a file to an operation, copy is done
        parcel = Parcel.objects.create(parcel_number='42',
                                 section='ZZ',
                                 town=default_town,
                                 associated_file=self.item)
        ParcelOwner.objects.create(
                owner=self.extra_models['person'],
                parcel=parcel, start_date=datetime.date.today(),
                end_date=datetime.date.today())
        parcel.operation = self.operation
        parcel.save()
        # double reference to operation and associated_file is deleted
        self.assertEqual(parcel.operation, None)
        # now 2 objects with the same parameters
        q = Parcel.objects.filter(parcel_number='42', section='ZZ',
                                  town=default_town)
        self.assertEqual(q.count(), 2)
        q = q.filter(operation=self.operation, associated_file=None)
        self.assertEqual(q.count(), 1)
        # parcel owner well attached
        q = ParcelOwner.objects.filter(parcel__operation=self.operation,
                                       parcel__parcel_number='42')
        self.assertEqual(q.count(), 1)


