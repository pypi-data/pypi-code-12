# -*- coding: utf-8 -*-
# ++ This file `test_management_export_routes.py` is generated at 4/12/16 7:32 PM ++
import os
import glob
import json
import shutil
import tempfile
from django.test import TestCase
from django.conf import settings
from django.utils import six
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
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


class TestExportModule(TestCase):
    """ """
    fixtures = (TEST_FIXTURE, )

    def setUp(self):

        super(TestCase, self).setUp()
        self.clean()
        call_command('import_routes', source=ROUTE_FIXTURE)

    def clean(self):
        """ Cleaning all existing Routing records those are comes with fixture """
        ContentTypeRoutingTable.objects.all().delete()
        SiteRoutingTable.objects.all().delete()
        RoutingTable.objects.all().delete()

    def test_with_destination(self):
        """ """

        _test_user = 'test_user'
        _test_group = 'administrator'
        _test_site = 'testserver'
        _test_route1 = 'test-route1'

        _test_destination = os.path.join(tempfile.gettempdir(), 'generated_serialized_routes.json')
        call_command('export_routes', destination=_test_destination)

        # we make sure serialized  files is usable
        self.clean()
        call_command('import_routes', source=_test_destination)

        # We make sure serialized  file is usable
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

        # Test: extended natural keys
        call_command('export_routes', destination=_test_destination, extended_natural_keys=True)

        # Make sure extended natural keys applied
        with open(_test_destination, 'r') as fp:
            entries = json.load(fp)
            _applicable_models = (
                "%s.%s" % (SiteRoutingTable._meta.app_label, SiteRoutingTable._meta.model_name),
                "%s.%s" % (ContentTypeRoutingTable._meta.app_label, ContentTypeRoutingTable._meta.model_name),
            )

            for entry in entries:
                if entry['model'].lower() not in _applicable_models:
                    continue

                if not isinstance(entry['fields']['site'], (list, tuple, )):
                    raise AssertionError("Code should not come here! site value must be iterable, after wrapping with "
                                         "extended natural keys")

                if entry['model'].lower() == _applicable_models[1]:
                    if not isinstance(entry['fields']['object_id'], (list, tuple,)):
                        raise AssertionError("Code should not come here! object_id value must be iterable, "
                                             "after wrapping with extended natural keys")
        self.clean()
        # Make sure with extended natural keys, the serialized file is importable without errors
        call_command('import_routes', source=_test_destination)

        # Test: exclude routes
        exclude_routes = [_test_route1, ]
        call_command('export_routes', destination=_test_destination + '.tmp', extended_natural_keys=True,
                     exclude_routes=exclude_routes)
        # Make sure there is no record of excluded route
        with open(_test_destination + '.tmp', 'r') as fp:
            entries = json.load(fp)
            _applicable_models = (
                "%s.%s" % (RoutingTable._meta.app_label, RoutingTable._meta.model_name),
                "%s.%s" % (SiteRoutingTable._meta.app_label, SiteRoutingTable._meta.model_name),
                "%s.%s" % (ContentTypeRoutingTable._meta.app_label, ContentTypeRoutingTable._meta.model_name),
            )

            for entry in entries:

                if entry['model'].lower() not in _applicable_models:
                    continue

                if entry['model'].lower() == _applicable_models[0]:
                    if entry['fields']['route_name'] in exclude_routes:
                        raise AssertionError(
                            "Code should not come here! this `%s` must be ignored" % entry['fields']['route_name'])
                    continue

                if entry['fields']['route'][0] in exclude_routes:
                    raise AssertionError("Code should not come here! ref route `%s` must be ignored." %
                                         entry['fields']['route'][0])

        os.unlink(_test_destination + '.tmp')

        # Test: exclude site
        exclude_sites = [_test_site, ]
        self.clean()
        call_command('import_routes', source=_test_destination)
        call_command('export_routes', destination=_test_destination + '.tmp', extended_natural_keys=True,
                     exclude_sites=exclude_sites)

        # Make sure there is no record of excluded site
        with open(_test_destination + '.tmp', 'r') as fp:
            entries = json.load(fp)
            _applicable_models = (
                "%s.%s" % (SiteRoutingTable._meta.app_label, SiteRoutingTable._meta.model_name),
                "%s.%s" % (ContentTypeRoutingTable._meta.app_label, ContentTypeRoutingTable._meta.model_name),
            )

            for entry in entries:

                if entry['model'].lower() not in _applicable_models:
                    continue

                if entry['fields']['site'][0] in exclude_sites:
                    raise AssertionError("Code should not come here! ref site `%s` must be ignored." %
                                         entry['fields']['site'][0])

        os.unlink(_test_destination + '.tmp')

        # Test: exclude group
        exclude_groups = [_test_group, ]
        self.clean()
        call_command('import_routes', source=_test_destination)
        call_command('export_routes', destination=_test_destination + '.tmp', extended_natural_keys=True,
                     exclude_groups=exclude_groups)

        # Make sure there is no record of excluded group
        with open(_test_destination + '.tmp', 'r') as fp:
            entries = json.load(fp)
            _applicable_models = (
                "%s.%s" % (ContentTypeRoutingTable._meta.app_label, ContentTypeRoutingTable._meta.model_name),
            )

            for entry in entries:

                if entry['model'].lower() not in _applicable_models:
                    continue

                if entry['fields']['object_id'][0] in exclude_groups:
                    raise AssertionError("Code should not come here! ref group `%s` must be ignored." %
                                         entry['fields']['object_id'][0])

        os.unlink(_test_destination + '.tmp')

        # Test: exclude user
        exclude_users = [_test_user, ]
        self.clean()
        call_command('import_routes', source=_test_destination)
        call_command('export_routes', destination=_test_destination + '.tmp', extended_natural_keys=True,
                     exclude_users=exclude_users)

        # Make sure there is no record of excluded user
        with open(_test_destination + '.tmp', 'r') as fp:
            entries = json.load(fp)
            _applicable_models = (
                "%s.%s" % (ContentTypeRoutingTable._meta.app_label, ContentTypeRoutingTable._meta.model_name),
            )

            for entry in entries:

                if entry['model'].lower() not in _applicable_models:
                    continue

                if entry['fields']['object_id'][0] in exclude_users:
                    raise AssertionError("Code should not come here! ref user `%s` must be ignored." %
                                         entry['fields']['object_id'][0])

        os.unlink(_test_destination + '.tmp')

        # Test: XML output
        self.clean()
        call_command('import_routes', source=_test_destination)

        call_command('export_routes', destination=_test_destination + '.tmp.xml', output_format='xml')
        # Make sure xml output is importable
        self.clean()
        call_command('import_routes', source=_test_destination + '.tmp.xml')
        # We make sure serialized  file is usable
        self.assertEqual(4, len(RoutingTable.objects.all()))
        self.assertEqual(2, len(SiteRoutingTable.objects.all()))
        self.assertEqual(7, len(ContentTypeRoutingTable.objects.all()))
        os.unlink(_test_destination + '.tmp.xml')

        # Test: only file name is provided and save to specified directory
        with self.settings(HACS_SERIALIZED_ROUTING_DIR=tempfile.gettempdir()):

            call_command('export_routes', destination='generated_routes.tmp.json')

            try:
                os.unlink(os.path.join(settings.HACS_SERIALIZED_ROUTING_DIR, 'generated_routes.tmp.json'))
            except OSError:
                raise AssertionError('Code should not come here, because serialized file should be save at specified '
                                     'location `%s`'
                                     % os.path.join(settings.HACS_SERIALIZED_ROUTING_DIR, 'generated_routes.tmp.json'))

        # Test: provide the directoy location ans file name is auto generated
        _dest_dir = tempfile.mkdtemp()
        call_command('export_routes', destination=_dest_dir)
        # we make sure new file is created
        self.assertEqual(1, len(glob.glob(os.path.join(_dest_dir, '*'))))
        shutil.rmtree(_dest_dir)

        # Finally remove the generated file
        os.unlink(_test_destination)

    def test_with_print_only(self):
        """ """
        _applicable_models = (
            "%s.%s" % (RoutingTable._meta.app_label, RoutingTable._meta.model_name),
            "%s.%s" % (SiteRoutingTable._meta.app_label, SiteRoutingTable._meta.model_name),
            "%s.%s" % (ContentTypeRoutingTable._meta.app_label, ContentTypeRoutingTable._meta.model_name),
        )
        # Test: print output instead of generate file
        stdout = six.StringIO()
        call_command('export_routes', print_only=True, stdout=stdout)
        stdout.seek(0)
        results = json.load(fp=stdout,encoding=settings.DEFAULT_CHARSET)

        routes = [route_entry for route_entry in results if route_entry['model'] == _applicable_models[0]]
        site_routes = [route_entry for route_entry in results if route_entry['model'] == _applicable_models[1]]
        contenttypes_routes = [route_entry for route_entry in results if route_entry['model'] == _applicable_models[2]]
        # We make sure correct output printed
        self.assertEqual(4, len(routes))
        self.assertEqual(2, len(site_routes))
        self.assertEqual(7, len(contenttypes_routes))

        # Test: print only has first priority
        _test_destination = os.path.join(tempfile.gettempdir(), 'generated_serialized_routes.json')
        stdout = six.StringIO()
        call_command('export_routes', destination=_test_destination, print_only=True, stdout=stdout)

        try:
            stdout.seek(0)
            json.load(stdout, encoding=settings.DEFAULT_CHARSET)
        except ValueError:
            raise AssertionError('Code should not come here, because `stdout` should have valid contents!')
        try:
            with open(_test_destination, 'r'):
                # We test the file is empty, because `print only` is the winner
                raise AssertionError("Code should not reach here, because specified file should not be created yet")
        except IOError:
            pass

        # Test: valid xml print output
        stdout = six.StringIO()
        call_command('export_routes', print_only=True, output_format='xml', stdout=stdout)

        # definitely should be invalid json
        try:
            stdout.seek(0)
            json.load(stdout, encoding=settings.DEFAULT_CHARSET)
            raise AssertionError("Code should not come here, because contents are xml!")
        except ValueError:
            pass

        _test_destination = os.path.join(tempfile.gettempdir(), 'generated_serialized_routes.xml')
        # Test: xml output is importable
        with open(_test_destination, 'w') as f:
            call_command('export_routes', print_only=True, output_format='xml', stdout=f)
        self.clean()
        call_command('import_routes', source=_test_destination)

        # We make sure captured output  file is usable
        self.assertEqual(4, len(RoutingTable.objects.all()))
        self.assertEqual(2, len(SiteRoutingTable.objects.all()))
        self.assertEqual(7, len(ContentTypeRoutingTable.objects.all()))

        os.unlink(_test_destination)

    def test_exceptions(self):
        """ """
        _test_user = 'test_user'
        _test_group = 'administrator'
        _test_site = 'testserver'
        _test_route1 = 'test-route1'
        # Test: validation error:: required param missing
        try:
            call_command('export_routes')
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertEqual("You have to pass either destination of output file or enable print only", exc.message)

        # Test: validation error:: serialized routing directory location not set
        try:
            call_command('export_routes', destination='my_fake.json')
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('You provide destination file name, not with full path', exc.message)

        # Test: validation error:: invalid/not installed app provided
        try:
            call_command('export_routes', print_only=True, exclude_apps=['fake_app'])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('Invalid app', exc.message)

        # Test: validation error:: invalid route name is provided
        try:
            call_command('export_routes', print_only=True, exclude_routes=[_test_route1, 'fake_route',])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_route', exc.message)

        # Test: validation error:: invalid site name is provided
        try:
            call_command('export_routes', print_only=True, exclude_sites=[_test_site, 'fake_site', ])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_site', exc.message)

        # Test: validation error:: invalid group name is provided
        try:
            call_command('export_routes', print_only=True, exclude_groups=[_test_group, 'fake_group', ])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_group', exc.message)

        # Test: validation error:: invalid user name is provided
        try:
            call_command('export_routes', print_only=True, exclude_users=[_test_user, 'fake_user', ])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_user', exc.message)

        # Test: validation error:: extended natural key not applied if omit natural PK and FK
        try:
            call_command('export_routes', print_only=True, no_natural_primary_keys=True,
                         no_natural_foreign_keys=True, extended_natural_keys=True)
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('--extended-natural-keys could be only applied', exc.message)


    def tearDown(self):

        super(TestExportModule, self).tearDown()
