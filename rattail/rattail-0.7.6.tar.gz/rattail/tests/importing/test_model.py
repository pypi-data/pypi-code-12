# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from rattail.db import model, auth
from rattail.importing import model as import_model
from rattail.tests import RattailTestCase


class TestAdminUser(RattailTestCase):

    def make_importer(self, **kwargs):
        kwargs.setdefault('session', self.session)
        return import_model.AdminUserImporter(**kwargs)

    def get_admin(self):
        return auth.administrator_role(self.session)

    def test_supported_fields(self):
        importer = import_model.UserImporter()
        standard_fields = importer.fields
        importer = self.make_importer()
        extra_fields = set(importer.fields) - set(standard_fields)
        self.assertEqual(len(extra_fields), 1)
        self.assertEqual(list(extra_fields)[0], 'admin')

    def test_normalize_local_object(self):
        importer = self.make_importer()
        user = model.User()
        data = importer.normalize_local_object(user)
        self.assertFalse(data['admin'])
        user.roles.append(self.get_admin())
        data = importer.normalize_local_object(user)
        self.assertTrue(data['admin'])

    def test_update_object(self):
        importer = self.make_importer(fields=['uuid', 'admin'])
        data = {'uuid': 'ccb1915419e511e6a3ad3ca9f40bc550'}
        user = model.User(**data)
        admin = self.get_admin()
        self.assertNotIn(admin, user.roles)

        data['admin'] = True
        importer.update_object(user, data)
        self.assertIn(admin, user.roles)

        data['admin'] = False
        importer.update_object(user, data)
        self.assertNotIn(admin, user.roles)
