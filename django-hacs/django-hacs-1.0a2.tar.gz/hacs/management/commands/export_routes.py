# -*- coding: utf-8 -*-
# ++ This file `export_routes.py` is generated at 4/18/16 4:20 PM ++
import os
import time
import json
import shutil
from django.utils import six
from django.apps import apps
from django.db.models import Q
from django.conf import settings
from django.core import serializers
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.utils.encoding import smart_text
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.core.management import CommandError
from django.utils.module_loading import import_string
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder

from hacs.models import RoutingTable
from hacs.models import SiteRoutingTable
from hacs.models import ContentTypeRoutingTable
from hacs.defaults import HACS_SERIALIZED_ROUTING_DIR
from hacs.defaults import HACS_USER_OBJECT_QUERY_CALLABLE

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

UserModel = get_user_model()


class Command(BaseCommand):
    """ """
    help = "HACS: Command tool for exporting"
    can_import_settings = True

    def add_arguments(self, parser):
        """"""
        # Add option for source file
        parser.add_argument(
            '-d',
            '--destination',
            action='store',
            dest='destination',
            help='The destination where serialized data will be stored physically. Value could be directory or absolute'
                 ' file path'
        )
        # Add exclude app option
        parser.add_argument(
            '-a',
            '--exclude-apps',
            action='store',
            dest='exclude_apps',
            nargs='+',
            help='List of apps you want to ignore. Example: --exclude-apps app1 app2 ..'
        )
        # Add exclude site options
        parser.add_argument(
            '-s',
            '--exclude-sites',
            action='store',
            dest='exclude_sites',
            nargs='+',
            help='List of sites you want to ignore. Value must be `domain name` of site not ID '
                 'Example: --exclude-sites site1 site2 ..'
        )
        # Add exclude user group options
        parser.add_argument(
            '-g',
            '--exclude-groups',
            action='store',
            dest='exclude_groups',
            nargs='+',
            help='List of user groups you want to ignore. Value must group name not ID.'
                 ' Example: --exclude-groups group1 group2 ..'
        )
        # Add exclude user options
        parser.add_argument(
            '-u',
            '--exclude-users',
            action='store',
            dest='exclude_users',
            nargs='+',
            help='List of users you want to ignore. Value must username or email not ID.'
                 ' Example: --exclude-users user1 user2 ..'
        )
        # Add exclude route options
        parser.add_argument(
            '-r',
            '--exclude-routes',
            action='store',
            dest='exclude_routes',
            nargs='+',
            help='List of routes you want to ignore. Value must provide route name not ID.'
                 ' Example: --exclude-routes route1 route2 ..'
        )
        # Add option for print only instead of storing
        parser.add_argument(
            '-p',
            '--print-only',
            action='store_true',
            dest="print_only",
            help="Use this option if you want to just print serialized data instead of store to filesystem"
        )
        # Add option for extended natural key
        # By default serialization will be here with enabling `natural primary and foreign key` but we may need more.
        # For example: Site model has no natural key, in ContentType `GenericForeignKey` relation's object_id does't
        # support natural key.
        parser.add_argument(
            '-x',
            '--extended-natural-keys',
            action='store_true',
            dest='extended_natural_keys',
            help='Enable extended natural keys.I.e for Site, objects_is'
        )
        # Add option for output format
        parser.add_argument(
            '-f',
            '--format',
            action='store',
            dest='output_format',
            choices=('json', 'xml',),
            default='json',
            help='Output format of serialized data or type of serializer. by default is json'
        )
        # Add option for no natural  primary keys
        parser.add_argument(
            '--no-natural-primary',
            action='store_true',
            dest='no_natural_primary_keys',
            help='By default this tool uses natural primary keys, but you can omit by using this option'
        )
        # Add option for no natural foreign keys
        parser.add_argument(
            '--no-natural-foreign',
            action='store_true',
            dest='no_natural_foreign_keys',
            help='By default this tool uses natural foreign keys, but you can omit by using this option'
        )

    def handle(self, *args, **options):
        """"""
        self._validate(*args, **options)
        objects = self.collect_all_objects_list(*args, **options)

        if not objects:
            self.stdout.write('Nothing to export. Empty result.')
            return
        filename, serializer = self._calculate_output_filename(*args, **options)
        serializer_options = {}

        if not options['no_natural_primary_keys']:
            serializer_options['use_natural_primary_keys'] = True

        if not options['no_natural_foreign_keys']:
            serializer_options['use_natural_foreign_keys'] = True

        if filename:
            with open(filename, 'w') as f:
                serializers.serialize(serializer, objects, stream=f, **serializer_options)
            if options['extended_natural_keys'] and serializer == 'json':
                with open(filename, 'r') as f:
                    objects = json.load(f, encoding=settings.DEFAULT_CHARSET)
                    self._wrap_extended_natural_keys(objects)

                    with open(filename + '.tmp', 'w') as fp:
                        json.dump(objects, fp=fp, cls=DjangoJSONEncoder)

                shutil.move(filename + '.tmp', filename)

        else:
            data = serializers.serialize(serializer, objects, **serializer_options)
            if options['extended_natural_keys'] and serializer == 'json':
                data = json.loads(data)
                self._wrap_extended_natural_keys(data)
                data = json.dumps(data, cls=DjangoJSONEncoder)
            self.stdout.write(data)

    def collect_all_objects_list(self, *args, **kwargs):
        """"""
        filters = {}
        exclude_routes = kwargs['exclude_routes']
        if exclude_routes is not None and isinstance(exclude_routes, six.string_types):
            exclude_routes = (exclude_routes,)
        if exclude_routes:
            filters['route_name__in'] = exclude_routes

        routing_table_queryset = RoutingTable.objects.exclude(**filters)

        if filters.get('route_name__in', None):
            filters['route__in'] = [RoutingTable.objects.get_by_natural_key(x) for x in filters.get('route_name__in')]
            del filters['route_name__in']

        exclude_sites = kwargs['exclude_sites']
        if exclude_sites is not None and isinstance(exclude_sites, six.string_types):
            exclude_sites = (exclude_sites,)

        if exclude_sites:
            filters['site__in'] = [Site.objects.get(domain=x) for x in exclude_sites]

        site_routing_queryset = SiteRoutingTable.objects.exclude(**filters)

        filter_arg = ()
        exclude_groups = kwargs['exclude_groups']
        if exclude_groups is not None and isinstance(exclude_groups, six.string_types):
            exclude_groups = (exclude_groups,)

        if exclude_groups:
            exclude_groups = [Group.objects.get_by_natural_key(x).pk for x in exclude_groups]
            filter_arg = (Q(content_type=ContentType.objects.get_for_model(Group), object_id__in=exclude_groups), )

        exclude_users = kwargs['exclude_users']
        if exclude_users is not None and isinstance(exclude_users, six.string_types):
            exclude_users = (exclude_users,)
        if exclude_users:
            exclude_users = [import_string(getattr(settings, 'HACS_USER_OBJECT_QUERY_CALLABLE',
                                                   HACS_USER_OBJECT_QUERY_CALLABLE))(x, silent=False).pk
                             for x in exclude_users]
            if filter_arg:
                filter_arg = (filter_arg[0] | Q(content_type=ContentType.objects.get_for_model(UserModel),
                                            object_id__in=exclude_users), )
            else:
                filter_arg = (Q(content_type=ContentType.objects.get_for_model(UserModel),
                                object_id__in=exclude_users), )

        contenttype_routing_queryset = ContentTypeRoutingTable.objects.exclude(*filter_arg, **filters)

        return list(routing_table_queryset) + list(site_routing_queryset) + list(contenttype_routing_queryset)

    def _validate(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        if not kwargs['destination'] and not kwargs['print_only']:
            raise CommandError("You have to pass either destination of output file or enable print only")

        if kwargs['destination']:
            if '/' not in kwargs['destination'] and os.path.splitext(kwargs['destination'])[1]:
                # We are sure only file name is provided
                if not getattr(settings, 'HACS_SERIALIZED_ROUTING_DIR', HACS_SERIALIZED_ROUTING_DIR):
                    raise CommandError("You provide destination file name, not with full path, in that case you must "
                                       "define `HACS_SERIALIZED_ROUTING_DIR` at django settings")

        exclude_apps = kwargs['exclude_apps']
        if exclude_apps is not None and isinstance(exclude_apps, six.string_types):
            exclude_apps = (exclude_apps,)
        if exclude_apps:
            for app_label in exclude_apps:
                try:
                    apps.get_app_config(app_label)
                except LookupError as err:
                    raise CommandError("Invalid app: " + smart_text(err))

        exclude_sites = kwargs['exclude_sites']
        if exclude_sites is not None and isinstance(exclude_sites, six.string_types):
            exclude_sites = (exclude_sites,)

        if exclude_sites:
            for site in exclude_sites:
                try:
                    Site.objects.get(domain=site)
                except Site.DoesNotExist:
                    raise CommandError("Specified site `%s` doesn't exists!" % site)

        exclude_groups = kwargs['exclude_groups']
        if exclude_groups is not None and isinstance(exclude_groups, six.string_types):
            exclude_groups = (exclude_groups,)

        if exclude_groups:
            for group in exclude_groups:
                try:
                    Group.objects.get_by_natural_key(group)
                except Group.DoesNotExist:
                    raise CommandError("Specified group `%s` doesn't exists!" % group)

        exclude_users = kwargs['exclude_users']
        if exclude_users is not None and isinstance(exclude_users, six.string_types):
            exclude_users = (exclude_users,)
        if exclude_users:
            for user in exclude_users:
                try:
                    import_string(getattr(settings, 'HACS_USER_OBJECT_QUERY_CALLABLE',
                                          HACS_USER_OBJECT_QUERY_CALLABLE))(user, silent=False)
                except UserModel.DoesNotExist:
                    raise CommandError("Specified user `%s` doesn't exists!" % user)

        exclude_routes = kwargs['exclude_routes']
        if exclude_routes is not None and isinstance(exclude_routes, six.string_types):
            exclude_routes = (exclude_routes,)
        if exclude_routes:
            for route in exclude_routes:
                try:
                    RoutingTable.objects.get_by_natural_key(route)
                except RoutingTable.DoesNotExist:
                    raise CommandError("Specified route `%s` doesn't exists!" % route)

        if kwargs['extended_natural_keys'] and (kwargs['no_natural_primary_keys'] or kwargs['no_natural_foreign_keys']):
            raise CommandError("--extended-natural-keys could be only applied, if enable natural PK and FK")

    def _calculate_output_filename(self, *args, **kwargs):
        """ """

        if kwargs['print_only']:
            # we don't care whether has destination
            return None, kwargs['output_format']

        filename = kwargs['destination']
        if filename:
            if '/' not in filename and os.path.splitext(filename)[1]:
                # We are sure only file name is provided
                filename = os.path.join(getattr(settings, 'HACS_SERIALIZED_ROUTING_DIR', HACS_SERIALIZED_ROUTING_DIR),
                                        filename)
            elif '/' in filename and not os.path.splitext(filename)[1]:
                filename = os.path.join(filename,
                                        'hacs_serialized_routes_generated_%s.%s' %
                                        (time.time(), kwargs['output_format']))

        return filename, kwargs['output_format']

    def _wrap_extended_natural_keys(self, entries):

        """"""
        _allowed_models = (
            "%s.%s" % (SiteRoutingTable._meta.app_label, SiteRoutingTable._meta.model_name),
            "%s.%s" % (ContentTypeRoutingTable._meta.app_label, ContentTypeRoutingTable._meta.model_name),
        )

        for entry in entries:

            if entry['model'].lower() not in _allowed_models:
                continue
            entry['fields']['site'] = (Site.objects.get(pk=entry['fields']['site']).domain, )

            if entry['model'].lower() == _allowed_models[1]:
                # Check if for Auth User Model
                if UserModel._meta.app_label in entry['fields']['content_type'] and \
                        UserModel._meta.model_name in entry['fields']['content_type']:
                    entry['fields']['object_id'] = \
                    (getattr(UserModel.objects.get(pk=entry['fields']['object_id']), UserModel.USERNAME_FIELD), )

                elif Group._meta.app_label in entry['fields']['content_type'] and Group._meta.model_name in \
                    entry['fields']['content_type']:
                    entry['fields']['object_id'] = Group.objects.get(pk=entry['fields']['object_id']).natural_key()
