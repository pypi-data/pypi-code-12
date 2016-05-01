# -*- coding: utf-8 -*-
# ++ This file `test_management_import_routes.py` is generated at 4/12/16 7:32 PM ++
import os
import shutil
import tempfile
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management import CommandError
from django.contrib.contenttypes.models import ContentType

from hacs.models import RoutingTable
from hacs.models import SiteRoutingTable
from hacs.models import ContentTypeRoutingTable

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_FIXTURE = os.path.join(CURRENT_PATH, 'fixtures', 'testing_fixture.json')
ROUTE_FIXTURE = os.path.join(CURRENT_PATH, 'fixtures', 'testing_routing_fixture.json')


class TestImportModule(TestCase):
    """ """
    fixtures = (TEST_FIXTURE, )

    def setUp(self):
        super(TestCase, self).setUp()
        self.clean()

    def clean(self):
        """ Cleaning all existing Routing records those are comes with fixture """
        ContentTypeRoutingTable.objects.all().delete()
        SiteRoutingTable.objects.all().delete()
        RoutingTable.objects.all().delete()

    def test_with_source_file(self):
        """ """
        call_command('import_routes', source=ROUTE_FIXTURE)
        _test_user = 'test_user'
        _test_group = 'administrator'
        _test_site = 'testserver'

        # We just checking all entries are inserted from fixture
        self.assertEqual(4, len(RoutingTable.objects.all()))
        self.assertEqual(2, len(SiteRoutingTable.objects.all()))
        self.assertEqual(7, len(ContentTypeRoutingTable.objects.all()))

        site = Site.objects.get(domain=_test_site)
        self.assertIsNotNone(SiteRoutingTable.objects.get(site=site))
        self.assertIsNotNone(ContentTypeRoutingTable.objects.get(
            site=site,
            content_type=ContentType.objects.get_for_model(Group),
            object_id=Group.objects.get_by_natural_key(_test_group).pk
        ))
        self.assertIsNotNone(ContentTypeRoutingTable.objects.get(
            site=site,
            content_type=ContentType.objects.get_for_model(User),
            object_id=User.objects.get(username=_test_user).pk
        ))

        self.clean()
        # Test: site exclude
        # Let's omit Site
        call_command('import_routes', source=ROUTE_FIXTURE, exclude_sites=[_test_site])
        # Excluded site should not have any route
        try:
            SiteRoutingTable.objects.get(site=site)
            raise AssertionError("Code should not reach here!, because object should not exist")
        except SiteRoutingTable.DoesNotExist:
            pass

        # As 5 entries are ignored, because those were related to exclude site
        self.assertEqual(2, len(ContentTypeRoutingTable.objects.all()))

        self.clean()
        # Test: group exclude
        call_command('import_routes', source=ROUTE_FIXTURE, exclude_groups=[_test_group])
        try:
            ContentTypeRoutingTable.objects.get(
                site=site,
                content_type=ContentType.objects.get_for_model(Group),
                object_id=Group.objects.get_by_natural_key(_test_group).pk
            )
            raise AssertionError("Code should not reach here!, because group object should not exist")
        except ContentTypeRoutingTable.DoesNotExist:
            pass

        # As 2 entries are ignored, because those were related to exclude group
        self.assertEqual(5, len(ContentTypeRoutingTable.objects.all()))

        self.clean()
        # Test: group exclude
        call_command('import_routes', source=ROUTE_FIXTURE, exclude_users=[_test_user])
        try:
            ContentTypeRoutingTable.objects.get(
                site=site,
                content_type=ContentType.objects.get_for_model(User),
                object_id=User.objects.get(username=_test_user).pk
            )
            raise AssertionError("Code should not reach here!, because object should not exist")
        except ContentTypeRoutingTable.DoesNotExist:
            pass

        # As 2 entries are ignored, because those were related to exclude user
        self.assertEqual(5, len(ContentTypeRoutingTable.objects.all()))

        self.clean()
        # Test: multi excluding
        call_command('import_routes', source=ROUTE_FIXTURE, exclude_groups=_test_group, exclude_users=_test_user)
        # As 2 + 2 entries are ignored, because those were related to exclude user and group
        self.assertEqual(3, len(ContentTypeRoutingTable.objects.all()))

    def test_with_autodiscover_files(self):
        """"""
        HACS_SERIALIZED_ROUTE_DIR_NAME = tempfile.mkdtemp('fixture')

        with self.settings(HACS_SERIALIZED_ROUTING_DIR=HACS_SERIALIZED_ROUTE_DIR_NAME):
            # Copy Test Route Fixture to tmp directory
            shutil.copyfile(ROUTE_FIXTURE, os.path.join(HACS_SERIALIZED_ROUTE_DIR_NAME, os.path.split(ROUTE_FIXTURE)[1]))
            call_command('import_routes')
            # We just checking all entries are inserted from fixture
            self.assertEqual(4, len(RoutingTable.objects.all()))
            self.assertEqual(2, len(SiteRoutingTable.objects.all()))
            self.assertEqual(7, len(ContentTypeRoutingTable.objects.all()))

        shutil.rmtree(HACS_SERIALIZED_ROUTE_DIR_NAME)

    def test_exceptions(self):
        """"""
        _test_user = 'test_user'
        _test_group = 'administrator'
        _test_site = 'testserver'
        _test_route1 = 'test-route1'
        # Test: validation error:: required param missing
        try:
            call_command('import_routes', omit_app_dir_walking=True)
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn("Required value is missing!", exc.message)

        # Test: validation error:: invalid/not installed app provided
        try:
            call_command('import_routes', exclude_apps=['fake_app'])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('Invalid app', exc.message)

        # Test: validation error:: invalid site name is provided
        try:
            call_command('import_routes', exclude_sites=[_test_site, 'fake_site', ])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_site', exc.message)

        # Test: validation error:: invalid group name is provided
        try:
            call_command('import_routes', exclude_groups=[_test_group, 'fake_group', ])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_group', exc.message)

        # Test: validation error:: invalid user name is provided
        try:
            call_command('import_routes', exclude_users=[_test_user, 'fake_user', ])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_user', exc.message)

        # Test: with `source`, invalid app and path
        try:
            call_command('import_routes', source='fake_app:fake_file.json')
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('Invalid app path pattern', exc.message)

        # Test: with source, correct app but invalid path
        try:
            call_command('import_routes', source='hacs:fake_file.json')
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('Invalid source path specified!', exc.message)
        _temp_dir = tempfile.mkdtemp()
        shutil.copyfile(TEST_FIXTURE, os.path.join(_temp_dir, 'test.json'))

        # Test: with `source` valid file but HACS_SERIALIZED_ROUTING_DIR is not set
        try:
            call_command('import_routes', source='test.json')
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('Invalid source path specified!', exc.message)

        # Test: with `source` HACS_SERIALIZED_ROUTING_DIR is set but invalid file
        with self.settings(HACS_SERIALIZED_ROUTING_DIR=_temp_dir):
            try:
                call_command('import_routes', source='fake_test.json')
                raise AssertionError("Code should not reach here!, because of validation error")
            except CommandError as exc:
                self.assertIn('Invalid source path specified!', exc.message)


    def tearDown(self):

        super(TestImportModule, self).tearDown()
