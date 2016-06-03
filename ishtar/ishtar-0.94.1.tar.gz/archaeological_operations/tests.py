#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
import json
import datetime

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User, Permission
import models

from ishtar_common.models import OrganizationType, Organization, \
    ImporterType, IshtarUser, TargetKey

from ishtar_common import forms_common


class ImportOperationTest(TestCase):
    fixtures = [settings.ROOT_PATH +
                '../fixtures/initial_data-auth-fr.json',
                settings.ROOT_PATH +
                '../ishtar_common/fixtures/initial_data-fr.json',
                settings.ROOT_PATH +
                '../ishtar_common/fixtures/test_towns.json',
                settings.ROOT_PATH +
                '../ishtar_common/fixtures/initial_importtypes-fr.json',
                settings.ROOT_PATH +
                '../archaeological_operations/fixtures/initial_data-fr.json']
    test_operations = True

    def setTargetKey(self, target, key, value):
        tg = TargetKey.objects.get(target__target=target, key=key)
        tg.value = value
        tg.is_set = True
        tg.save()

    def setUp(self):
        self.username, self.password, self.user = create_superuser()
        self.ishtar_user = IshtarUser.objects.get(pk=self.user.pk)

    def testMCCImportOperation(self, test=True):
        # MCC opérations
        if self.test_operations is False:
            test = False
        first_ope_nb = models.Operation.objects.count()
        MCC_OPERATION = ImporterType.objects.get(name=u"MCC - Opérations")
        mcc_operation_file = open(
            settings.ROOT_PATH +
            '../archaeological_operations/tests/MCC-operations-example.csv',
            'rb')
        file_dict = {'imported_file': SimpleUploadedFile(
            mcc_operation_file.name, mcc_operation_file.read())}
        post_dict = {'importer_type': MCC_OPERATION.pk, 'skip_lines': 1,
                     "encoding": 'utf-8'}
        form = forms_common.NewImportForm(data=post_dict, files=file_dict,
                                          instance=None)
        form.is_valid()
        if test:
            self.assertTrue(form.is_valid())
        impt = form.save(self.ishtar_user)
        target_key_nb = TargetKey.objects.count()
        impt.initialize()
        # new key have to be set
        if test:
            self.assertTrue(TargetKey.objects.count() > target_key_nb)

        # first try to import
        impt.importation()
        current_ope_nb = models.Operation.objects.count()
        # no new operation imported because of a missing connection for
        # operation_type value
        if test:
            self.assertTrue(current_ope_nb == first_ope_nb)

        # doing manualy connections
        tg = TargetKey.objects.filter(target__target='operation_type'
                                      ).order_by('-pk').all()[0]
        tg.value = models.OperationType.objects.get(
            txt_idx='prog_excavation').pk
        tg.is_set = True
        tg.save()

        target = TargetKey.objects.get(key='gallo-romain')
        gallo = models.Period.objects.get(txt_idx='gallo-roman')
        target.value = gallo.pk
        target.is_set = True
        target.save()

        target = TargetKey.objects.get(key='age-du-fer')
        iron = models.Period.objects.get(txt_idx='iron_age')
        target.value = iron.pk
        target.is_set = True
        target.save()

        impt.importation()
        if not test:
            return
        # a new operation has now been imported
        current_ope_nb = models.Operation.objects.count()
        self.assertTrue(current_ope_nb == (first_ope_nb + 1))
        # and well imported
        last_ope = models.Operation.objects.order_by('-pk').all()[0]
        self.assertEqual(last_ope.name, u"Oppìdum de Paris")
        self.assertTrue(last_ope.code_patriarche == 4200)
        self.assertTrue(last_ope.operation_type.txt_idx == 'prog_excavation')
        self.assertEqual(last_ope.periods.count(), 2)
        periods = last_ope.periods.all()
        self.assertTrue(iron in periods and gallo in periods)

        # a second importation will be not possible: no two same patriarche
        # code
        impt.importation()
        models.Operation.objects.count()
        self.assertTrue(last_ope ==
                        models.Operation.objects.order_by('-pk').all()[0])

    def testMCCImportParcels(self, test=True):
        if self.test_operations is False:
            test = False
        self.testMCCImportOperation(test=False)
        old_nb = models.Parcel.objects.count()
        MCC_PARCEL = ImporterType.objects.get(name=u"MCC - Parcelles")
        mcc_file = open(
            settings.ROOT_PATH +
            '../archaeological_operations/tests/MCC-parcelles-example.csv',
            'rb')
        file_dict = {'imported_file': SimpleUploadedFile(mcc_file.name,
                                                         mcc_file.read())}
        post_dict = {'importer_type': MCC_PARCEL.pk, 'skip_lines': 1,
                     "encoding": 'utf-8'}
        form = forms_common.NewImportForm(data=post_dict, files=file_dict,
                                          instance=None)
        form.is_valid()
        if test:
            self.assertTrue(form.is_valid())
        impt = form.save(self.ishtar_user)
        impt.initialize()
        impt.importation()
        if not test:
            return
        # new parcels has now been imported
        current_nb = models.Parcel.objects.count()
        self.assertTrue(current_nb == (old_nb + 2))
        # and well imported
        last_parcels = models.Parcel.objects.order_by('-pk').all()[0:2]
        external_ids = sorted(['4200-59350-YY55', '4200-75101-XXXX'])
        parcel_numbers = sorted(['42', '55'])
        sections = sorted(['ZX', 'YY'])
        self.assertEqual(external_ids,
                         sorted([p.external_id for p in last_parcels]))
        self.assertEqual(parcel_numbers,
                         sorted([p.parcel_number for p in last_parcels]))
        self.assertEqual(sections,
                         sorted([p.section for p in last_parcels]))
        last_ope = models.Operation.objects.order_by('-pk').all()[0]
        towns_ope = last_ope.towns.all()
        imported = [imp for acc, imp in impt.get_all_imported()]
        for p in last_parcels:
            self.assertTrue(p.town in towns_ope)
            self.assertTrue(p in imported)
        self.assertEqual(len(imported), len(last_parcels))
        self.assertEqual(models.Parcel.objects.get(parcel_number='55',
                                                   section='YY').external_id,
                         '4200-59350-YY55')
        # delete associated parcel with the import deletion
        parcel_count = models.Parcel.objects.count()
        impt.delete()
        self.assertEqual(parcel_count - 2, models.Parcel.objects.count())

    def testParseParcels(self):
        if not self.test_operations:
            return
        # the database needs to be initialised before importing
        from archaeological_operations.import_from_csv import parse_parcels
        # default_town = Town.objects.create(numero_insee="12345",
        #                                    name="default_town")
        test_values = (
            (u"1996 : XT:53,54,56,57,59,60,61,62",
             {1996: [
                 ("XT", "53"), ("XT", "54"), ("XT", "56"), ("XT", "57"),
                 ("XT", "59"), ("XT", "60"), ("XT", "61"), ("XT", "62"),
             ]}
             ),
            (u"AD:23",
             {None: [
                 ("AD", "23")
             ]}),
            (u"1961 :B1:227;",
             {1961: [
                 ("B1", '227')
             ]}),
            (u"1982 CV:35;CV:36",
             {1982: [
                 ("CV", "35"), ("CV", "36"),
             ]}),
            (u"E:24;E:25",
             {None: [
                 ("E", "24"), ("E", "25"),
             ]}),
            (u"B : 375, 376, 386, 387, 645, 646 / C : 412 à 415, 432 à 435, "
             u"622 / F : 120, 149, 150, 284, 287, 321 à 323",
             {None: [
                 ("B", "375"), ("B", "376"), ("B", "386"), ("B", "387"),
                 ("B", "645"), ("B", "646"),
                 ("C", "412"), ("C", "413"), ("C", "414"), ("C", "415"),
                 ("C", "432"), ("C", "433"), ("C", "434"), ("C", "435"),
                 ("C", "622"),
                 ("F", "120"), ("F", "149"), ("F", "150"), ("F", "284"),
                 ("F", "287"), ("F", "321"), ("F", "322"), ("F", "323"),
             ]}),
            (u"AD : 95, 96, 86, 87, 81, 252, AE : 58, AD : 115 à 132",
             {None: [
                 ("AD", "95"), ("AD", "96"), ("AD", "86"), ("AD", "87"),
                 ("AD", "81"), ("AD", "252"), ("AD", "115"), ("AD", "116"),
                 ("AD", "117"), ("AD", "118"), ("AD", "119"), ("AD", "120"),
                 ("AD", "121"), ("AD", "122"), ("AD", "123"), ("AD", "124"),
                 ("AD", "125"), ("AD", "126"), ("AD", "127"), ("AD", "128"),
                 ("AD", "129"), ("AD", "130"), ("AD", "131"), ("AD", "132"),
                 ("AE", "58"),
             ]}),
            (u"XD:1 à 13, 24 à 28, 33 à 39, 50 à 52, 80, 83, 84 à 86, 259 à "
             u"261, 182, 225 ; XH:5 ; P:1640, 1888, 1889, 1890 ; R:1311, "
             u"1312, 1314,1342, 1343, 1559 à 1569",
             {None: [
                 ('XD', "1"), ('XD', "2"), ('XD', "3"), ('XD', "4"),
                 ('XD', "5"), ('XD', "6"), ('XD', "7"), ('XD', "8"),
                 ('XD', "9"), ('XD', "10"), ('XD', "11"), ('XD', "12"),
                 ('XD', "13"), ("XD", "24"), ("XD", "25"), ("XD", "26"),
                 ("XD", "27"), ("XD", "28"), ("XD", "33"), ("XD", "34"),
                 ("XD", "35"), ("XD", "36"), ("XD", "37"), ("XD", "38"),
                 ("XD", "39"), ("XD", "50"), ("XD", "51"), ("XD", "52"),
                 ("XD", "80"), ("XD", "83"), ("XD", "84"), ("XD", "85"),
                 ("XD", "86"), ("XD", "259"), ("XD", "260"), ("XD", "261"),
                 ("XD", "182"), ("XD", "225"), ("XH", "5"),
                 ("P", "1640"), ("P", "1888"), ("P", "1889"), ("P", "1890"),
                 ("R", "1311"), ("R", "1312"), ("R", "1314"), ("R", "1342"),
                 ("R", "1343"), ("R", "1559"), ("R", "1560"), ("R", "1561"),
                 ("R", "1562"), ("R", "1563"), ("R", "1564"), ("R", "1565"),
                 ("R", "1566"), ("R", "1567"), ("R", "1568"), ("R", "1569"),
             ]}),
            (u"BZ:2 à 5, 365 ; CD:88 à 104, 106, 108, 326",
             {None: [
                 ('BZ', '2'), ('BZ', '3'), ('BZ', '4'), ('BZ', '5'),
                 ('BZ', '365'), ('CD', '88'), ('CD', '89'), ('CD', '90'),
                 ('CD', '91'), ('CD', '92'), ('CD', '93'), ('CD', '94'),
                 ('CD', '95'), ('CD', '96'), ('CD', '97'), ('CD', '98'),
                 ('CD', '99'), ('CD', '100'), ('CD', '101'), ('CD', '102'),
                 ('CD', '103'), ('CD', '104'), ('CD', '106'), ('CD', '326'),
                 ('CD', '108')
             ]}),
            (u"AV 118 à 125, 127, 132 à 137, 153, 398p, 399, 402; BI 27, 30, "
             u"32, 33, 188, 255, 256 à 258, 260, 284p, 294; BL 297",
             {None: [
                 ('AV', '118'), ('AV', '119'), ('AV', '120'), ('AV', '121'),
                 ('AV', '122'), ('AV', '123'), ('AV', '124'), ('AV', '125'),
                 ('AV', '127'), ('AV', '132'), ('AV', '133'), ('AV', '134'),
                 ('AV', '135'), ('AV', '136'), ('AV', '137'), ('AV', '153'),
                 ('AV', '398p'), ('AV', '399'), ('AV', '402'),
                 ('BI', '27'), ('BI', '30'), ('BI', '32'), ('BI', '33'),
                 ('BI', '188'), ('BI', '255'), ('BI', '256'), ('BI', '257'),
                 ('BI', '258'), ('BI', '260'), ('BI', '284p'), ('BI', '294'),
                 ('BL', '297'),
             ]}),
            (u"A : 904 à 906, 911 ; E:40, 41",
             {None: [
                 ("A", '904'), ("A", '905'), ("A", '906'), ("A", '911'),
                 ("E", '40'), ("E", "41")
             ]}),
            (u"1991 : BE:8, 12",
             {"1991": [
                 ('BE', '8'), ('BE', '12'),
             ]}),
            (u"1979 : EM:1",
             {"1979": [
                 ('EM', '1')
             ]},),
            (u"B:448;B:449;B:450;B:451;B:452;B:455;B:456;B:457;B:458;B:459;"
             u"B:1486;",
             {None: [
                 ("B", "448"), ("B", "449"), ("B", "450"), ("B", "451"),
                 ("B", "452"), ("B", "455"), ("B", "456"), ("B", "457"),
                 ("B", "458"), ("B", "459"), ("B", "1486"),
             ]}),
            (u"AC : 72 à 81, 91 à 100, 197 / ZC:180 à 189",
             {None: [
                 ('AC', '72'), ('AC', '73'), ('AC', '74'), ('AC', '75'),
                 ('AC', '76'), ('AC', '77'), ('AC', '78'), ('AC', '79'),
                 ('AC', '80'), ('AC', '81'), ('AC', '91'), ('AC', '92'),
                 ('AC', '93'), ('AC', '94'), ('AC', '95'), ('AC', '96'),
                 ('AC', '97'), ('AC', '98'), ('AC', '99'), ('AC', '100'),
                 ('AC', '197'), ('ZC', '180'), ('ZC', '181'), ('ZC', '182'),
                 ('ZC', '183'), ('ZC', '184'), ('ZC', '185'), ('ZC', '186'),
                 ('ZC', '187'), ('ZC', '188'), ('ZC', '189'),
             ]}),
            (u"AB 37 et 308",
             {None: [
                 ('AB', '37'), ('AB', '308'),
             ]}),
            (u"1983  D2 n° 458 et 459",
             {"1983": [
                 ('D2', '458'), ('D2', '459'),
             ]}),
            (u"ZS : 21p, 66",
             {None: [
              ('ZS', '21p'), ('ZS', '66'),
              ]}),
            (u"VV:166, 167, domaine public",
             {None: [
                 ('VV', '166'), ('VV', '167'),
             ]}),
            (u" AS:13 à 15, 17 à 19, 21 à 32, 34 à 45, 47 à 53, 69, 70, 82, "
             u"84 / CK:1, 24, 25, 29, 30, 37 à 43",
             {None: [
              ("AS", "13"), ("AS", "14"), ("AS", "15"), ("AS", "17"),
              ("AS", "18"), ("AS", "19"), ("AS", "21"), ("AS", "22"),
              ("AS", "23"), ("AS", "24"), ("AS", "25"), ("AS", "26"),
              ("AS", "27"), ("AS", "28"), ("AS", "29"), ("AS", "30"),
              ("AS", "31"), ("AS", "32"), ("AS", "34"), ("AS", "35"),
              ("AS", "36"), ("AS", "37"), ("AS", "38"), ("AS", "39"),
              ("AS", "40"), ("AS", "41"), ("AS", "42"), ("AS", "43"),
              ("AS", "44"), ("AS", "45"), ("AS", "47"), ("AS", "48"),
              ("AS", "49"), ("AS", "50"), ("AS", "51"), ("AS", "52"),
              ("AS", "53"), ('AS', "69"), ('AS', "70"), ('AS', "82"),
              ('AS', "84"), ('CK', "1"), ('CK', "24"), ('CK', "25"),
              ('CK', "29"), ('CK', "30"), ('CK', "37"), ('CK', "38"),
              ('CK', "39"), ('CK', "40"), ('CK', "41"), ('CK', "42"),
              ('CK', "43"), ]}),
            (u" ZN:37, 15, 35, 28, 29 / ZM:9, 73",
             {None: [
                 ("ZN", "37"), ("ZN", "15"), ("ZN", "35"), ("ZN", "28"),
                 ("ZN", "29"), ("ZM", "9"), ("ZM", "73"),
             ]}),
            (u" Tranche n°1 : YP:243, 12, 14 à 16, 18 à 26, DP / Tranche n°2 :"
             u"YP:17, 307, 27, 308, 44 à 46, 683, BM:1, 250, 488 à 492",
             {None: [
                 ('YP', '243'), ('YP', '12'), ('YP', '14'), ('YP', '15'),
                 ('YP', '16'), ('YP', '18'), ('YP', '19'), ('YP', '20'),
                 ('YP', '21'), ('YP', '22'), ('YP', '23'), ('YP', '24'),
                 ('YP', '25'), ('YP', '26'), ('YP', '17'), ('YP', '27'),
                 ('YP', '308'), ('YP', '44'), ('YP', '45'), ('YP', '46'),
                 ('YP', '683'), ('YP', '307'), ('BM', '1'), ('BM', '250'),
                 ('BM', '488'), ('BM', '489'), ('BM', '490'), ('BM', '491'),
                 ('BM', '492'),
             ]}),
            (u" H : 106, 156, 158",
             {None: [
                 ('H', '106'), ('H', '156'), ('H', '158'),
             ]}),
            (u"Section YO : parcelles n° 19; 20",
             {None: [
                 ('YO', '19'), ('YO', '20'),
             ]}),
            (u"1991 :AI:23;19;20;21;22;181;AM:116;214;215;233;235",
             {u"1991": [
                 (u"AI", "19"), (u"AI", "20"), (u"AI", "21"), (u"AI", "22"),
                 (u"AI", "23"), (u"AI", "181"),
                 (u"AM", "116"), (u"AM", "214"), (u"AM", "215"),
                 (u"AM", "233"), (u"AM", "235"),
             ]})
        )
        # ),(u"Domaine public", {}
        # ),(u"Tranche 1 : AV:4 à 6, 18, 80, 104 / partiellement : 5 et 18", {}
        # ),(u" 1987 : ZD: ?", {}
        # ),(u"A:26a, 26b, 27 / AB:95 / AK:4, 12, 20", {}
        for value, result in test_values:
            parcels = parse_parcels(value)
            if not parcels and not result:
                continue
            self.assertTrue(parcels != [],
                            msg="No parcel parsed for \"%s\"" % value)
            parcels_copy = parcels[:]
            for year in result.keys():
                for values in parcels_copy:
                    if values['year'] != year and \
                       values['year'] != unicode(year):
                        continue
                    self.assertTrue(
                        (values['section'], values['parcel_number'])
                        in result[year],
                        msg="Section - Parcel number: \"%s - %s\" is not "
                        "in \"%s\"" % (
                            values['section'], values['parcel_number'],
                            unicode(result[year])))
                    parcels.pop(parcels.index(values))
                    result[year].pop(result[year].index(
                        (values['section'], values['parcel_number'])))
            # all parcels have been imported
            self.assertEqual(parcels, [], msg="Parcel(s): \"%s\" haven't be "
                             "recognized in \"%s\"" % (str(parcels), value))
            not_imported = [data for data in result.values() if data]
            self.assertEqual(
                not_imported, [], msg="Parcel(s): \"%s\" haven't be "
                "recognized in \"%s\"" % (str(not_imported), value))


def create_superuser():
    username = 'username4277'
    password = 'dcbqj756456!@%'
    user = User.objects.create_superuser(username, "nomail@nomail.com",
                                         password)
    return username, password, user


def create_user():
    username = 'username678'
    password = 'dcbqj756456!@%'
    user = User.objects.create_user(username, email="nomail2@nomail.com")
    user.set_password(password)
    user.save()
    return username, password, user


def create_orga(user):
    orga_type, created = OrganizationType.objects.get_or_create(
        txt_idx='operator')
    orga, created = Organization.objects.get_or_create(
        name='Operator', organization_type=orga_type, history_modifier=user)
    return orga


def create_operation(user, orga=None):
    dct = {'year': 2010, 'operation_type_id': 1,
           'history_modifier': user}
    if orga:
        dct['operator'] = orga
    operation = models.Operation.objects.create(**dct)
    return operation


class OperationInitTest(object):
    def create_user(self):
        username, password, self.user = create_user()

    def get_default_user(self):
        if not hasattr(self, 'user') or not self.user:
            self.create_user()
        return self.user

    def create_orgas(self, user=None):
        if not user:
            user = self.get_default_user()
        self.orgas = [create_orga(user)]
        return self.orgas

    def get_default_orga(self, user=None):
        if not hasattr(self, 'orgas') or not self.orgas:
            self.create_orgas(user)
        return self.orgas[0]

    def create_towns(self, datas={}):
        default = {'numero_insee': '12345', 'name': 'default_town'}
        default.update(datas)
        town = models.Town.objects.create(**default)
        if not hasattr(self, 'towns') or not self.towns:
            self.towns = []
        self.towns.append(town)
        return self.towns

    def get_default_town(self):
        town = getattr(self, 'towns', None)
        if not town:
            self.create_towns()
            town = self.towns[0]
        return town

    def create_parcel(self, data={}):
        default = {'town': self.get_default_town(),
                   'section': 'A', 'parcel_number': '1'}
        default.update(data)
        if not getattr(self, 'parcels', None):
            self.parcels = []
        self.parcels.append(models.Parcel.objects.create(**default))
        return self.parcels

    def get_default_parcel(self):
        return self.create_parcel()[0]

    def create_operation(self, user=None, orga=None):
        if not orga:
            self.get_default_orga(user)
        if not user:
            self.get_default_user()
        if not getattr(self, 'operations', None):
            self.operations = []
        self.operations.append(create_operation(user, orga))
        return self.operations

    def get_default_operation(self):
        return self.create_operation()[0]


class OperationTest(TestCase, OperationInitTest):
    fixtures = [settings.ROOT_PATH +
                '../fixtures/initial_data-auth-fr.json',
                settings.ROOT_PATH +
                '../ishtar_common/fixtures/initial_data-fr.json',
                settings.ROOT_PATH +
                '../archaeological_files/fixtures/initial_data.json',
                settings.ROOT_PATH +
                '../archaeological_operations/fixtures/initial_data-fr.json']

    def setUp(self):
        self.username, self.password, self.user = create_superuser()
        self.alt_username, self.alt_password, self.alt_user = create_user()
        self.alt_user.user_permissions.add(Permission.objects.get(
            codename='view_own_operation'))
        self.orgas = self.create_orgas(self.user)
        self.operations = self.create_operation(self.user, self.orgas[0])
        self.operations += self.create_operation(self.alt_user, self.orgas[0])
        self.item = self.operations[0]

    def testSearch(self):
        c = Client()
        response = c.get(reverse('get-operation'), {'year': '2010'})
        # no result when no authentification
        self.assertTrue(not json.loads(response.content))
        c.login(username=self.username, password=self.password)
        response = c.get(reverse('get-operation'), {'year': '2010'})
        self.assertTrue(json.loads(response.content)['total'] == 2)
        response = c.get(reverse('get-operation'),
                         {'operator': self.orgas[0].pk})
        self.assertTrue(json.loads(response.content)['total'] == 2)

    def testRelatedSearch(self):
        c = Client()
        rel1 = models.RelationType.objects.create(
            symmetrical=True, label='Include', txt_idx='include')
        rel2 = models.RelationType.objects.create(
            symmetrical=False, label='Included', txt_idx='included',
            inverse_relation=rel1)
        models.RecordRelations.objects.create(
            left_record=self.operations[0],
            right_record=self.operations[1],
            relation_type=rel1)
        self.operations[1].year = 2011
        self.operations[1].save()
        search = {'year': '2010', 'relation_types_0': rel2.pk}
        response = c.get(reverse('get-operation'), search)
        # no result when no authentification
        self.assertTrue(not json.loads(response.content))
        c.login(username=self.username, password=self.password)
        response = c.get(reverse('get-operation'), search)
        self.assertTrue(json.loads(response.content)['total'] == 2)

    def testOwnSearch(self):
        c = Client()
        response = c.get(reverse('get-operation'), {'year': '2010'})
        # no result when no authentification
        self.assertTrue(not json.loads(response.content))
        c.login(username=self.alt_username, password=self.alt_password)
        response = c.get(reverse('get-operation'), {'year': '2010'})
        # only one "own" operation available
        self.assertTrue(json.loads(response.content)['total'] == 1)
        response = c.get(reverse('get-operation'),
                         {'operator': self.orgas[0].pk})
        self.assertTrue(json.loads(response.content)['total'] == 1)


def create_administrativact(user, operation):
    act_type, created = models.ActType.objects.get_or_create(
        txt_idx='act_type')
    dct = {'history_modifier': user,
           'act_type': act_type,
           'operation': operation,
           'signature_date': datetime.date(2014, 05, 12),
           'index': 322}
    adminact, created = models.AdministrativeAct.objects.get_or_create(**dct)
    return [act_type], [adminact]


class RegisterTest(TestCase, OperationInitTest):
    fixtures = [settings.ROOT_PATH +
                '../ishtar_common/fixtures/initial_data.json',
                settings.ROOT_PATH +
                '../archaeological_files/fixtures/initial_data.json',
                settings.ROOT_PATH +
                '../archaeological_operations/fixtures/initial_data-fr.json']

    def setUp(self):
        self.username, self.password, self.user = create_superuser()
        self.operations = self.create_operation(self.user)
        self.act_types, self.operations = create_administrativact(
            self.user, self.operations[0])

    def testSearch(self):
        c = Client()
        response = c.get(reverse('get-administrativeact'), {'year': '2014'})
        # no result when no authentification
        self.assertTrue(not json.loads(response.content))
        c.login(username=self.username, password=self.password)
        response = c.get(reverse('get-administrativeact'), {'year': '2014'})
        self.assertTrue(json.loads(response.content)['total'] == 1)
        response = c.get(reverse('get-administrativeact'), {'indexed': '2'})
        self.assertTrue(json.loads(response.content)['total'] == 1)
