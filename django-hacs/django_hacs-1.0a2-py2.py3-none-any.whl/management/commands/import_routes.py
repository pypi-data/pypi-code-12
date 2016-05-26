# -*- coding: utf-8 -*-
# ++ This file `import_routes.py` is generated at 4/9/16 6:11 AM ++
import os
import glob
import json
import tempfile
from django.utils import six
from django.apps import apps
from django.conf import settings
from django.core import serializers
from django.contrib.auth.models import Group
from django.utils.encoding import smart_text
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from hacs.models import RoutingTable
from hacs.models import SiteRoutingTable
from hacs.models import ContentTypeRoutingTable
from hacs.defaults import HACS_SERIALIZED_ROUTING_DIR
from hacs.defaults import HACS_USER_OBJECT_QUERY_CALLABLE
from hacs.globals import HACS_SERIALIZED_ROUTE_DIR_NAME

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

UserModel = get_user_model()


class Command(BaseCommand):
    """"""
    help = "HACS: Command tool for importing"
    can_import_settings = True

    def add_arguments(self, parser):
        """
        :param parser:
        :return:
        """
        # Add option for source file
        parser.add_argument(
            '-S',
            '--source',
            action='store',
            dest='source',
            help='Importable source file location, could be absolute path or app prefix path(prefix '
                 'should be separated by :). If source is provided all other arguments except verbose will be ignored'
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
        # Add walking to app directory discover option
        parser.add_argument(
            '--omit-app-dir-walking',
            action='store_true',
            default=False,
            dest="omit_app_dir_walking",
            help="By this tool walking over all installed apps to discover importable file, "
                 "so you omit this by using this option"
        )

    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """
        self._validate(*args, **options)
        importable_files = self._get_importable_files(*args, **options)

        for serialized_file in importable_files:
            # we will normalized natural keys to PK those are not supported by django by default
            # For example User, Site and object id of contenttype relationship.
            # Right now normalization is applied for json file only
            if os.path.splitext(serialized_file)[1][1:].lower() == 'json':
                _temp_file = tempfile.mktemp(suffix='.json')
                with open(serialized_file, 'r') as f:
                    objects = json.load(f)
                    self._normalize_unwanted_natural_keys(objects)
                    with open(_temp_file, 'w') as t_f:
                        json.dump(objects, t_f)
                file_like_obj = open(_temp_file, 'r')
                os.unlink(_temp_file)
            else:
                file_like_obj = open(serialized_file, 'r')

            with file_like_obj:
                deserialized_objects = serializers.deserialize(os.path.splitext(serialized_file)[1][1:], file_like_obj)
                for deserialized_obj in deserialized_objects:
                    if not self._object_validate(deserialized_obj.object, *args, **options):
                        continue
                    deserialized_obj.save()

    def _object_validate(self, obj, *args, **kwargs):
        """
        :param obj
        :param args:
        :param kwargs:
        :return:
        """
        if not isinstance(obj, (RoutingTable, SiteRoutingTable, ContentTypeRoutingTable, )):
            return False

        exclude_apps = kwargs['exclude_apps']
        if exclude_apps is not None and isinstance(exclude_apps, six.string_types):
            exclude_apps = (exclude_apps, )
            # We are not doing with excluding apps right now.
            pass

        exclude_sites = kwargs['exclude_sites']
        if exclude_sites is not None and isinstance(exclude_sites, six.string_types):
            exclude_sites = [exclude_sites, ]

        if exclude_sites and not isinstance(obj, RoutingTable):
            if obj.site.domain in exclude_sites:
                return False

        exclude_groups = kwargs['exclude_groups']
        if exclude_groups is not None and isinstance(exclude_groups, six.string_types):
            exclude_groups = (exclude_groups, )

        if exclude_groups and isinstance(obj, ContentTypeRoutingTable):
            content_type = ContentType.objects.get_for_model(Group)
            if obj.content_type == content_type and Group.objects.get(pk=obj.object_id).name in exclude_groups:
                return False

        exclude_users = kwargs['exclude_users']
        if exclude_users is not None and isinstance(exclude_users, six.string_types):
            exclude_users = (exclude_users, )

        if exclude_users and isinstance(obj, ContentTypeRoutingTable):

            content_type = ContentType.objects.get_for_model(UserModel)
            if obj.content_type == content_type and \
                    getattr(UserModel.objects.get(pk=obj.object_id), UserModel.USERNAME_FIELD) in exclude_users:
                return False

        return True

    def _validate(self, *args, **kwargs):
        """
        :return:
        """
        if not kwargs['source'] and not getattr(settings, 'HACS_SERIALIZED_ROUTING_DIR',HACS_SERIALIZED_ROUTING_DIR) \
            and kwargs['omit_app_dir_walking']:

            raise CommandError("Required value is missing! you have to either provide source file or define "
                               "routing directory name or enable app discovering")

        exclude_apps = kwargs['exclude_apps']
        if exclude_apps is not None and isinstance(exclude_apps, six.string_types):
            exclude_apps = (exclude_apps, )
        if exclude_apps:
            for app_label in exclude_apps:
                try:
                    apps.get_app_config(app_label)
                except LookupError as err:
                    raise CommandError(smart_text("Invalid app: ") + smart_text(err))

        exclude_sites = kwargs['exclude_sites']
        if exclude_sites is not None and isinstance(exclude_sites, six.string_types):
            exclude_sites = (exclude_sites, )

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

    def _get_importable_files(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        importable_files = []
        if kwargs['source']:

            _temp = kwargs['source']
            if os.path.exists(_temp):
                importable_files.append(_temp)

            elif not os.path.exists(_temp) and \
                getattr(settings, 'HACS_SERIALIZED_ROUTING_DIR', HACS_SERIALIZED_ROUTING_DIR):
                if os.path.exists(os.path.join(getattr(settings, 'HACS_SERIALIZED_ROUTING_DIR',
                                                       HACS_SERIALIZED_ROUTING_DIR), _temp)):
                    importable_files.append(os.path.join(getattr(settings, 'HACS_SERIALIZED_ROUTING_DIR',
                                                 HACS_SERIALIZED_ROUTING_DIR), _temp))
            else:

                if 2 == len(_temp.split(':')):

                    try:
                        app = apps.get_app_config(_temp.split(':')[0])
                    except LookupError as err:
                        raise CommandError('Invalid app path pattern: ' + smart_text(err) + '. Provided path is %s' % _temp)
                    else:
                        if os.path.exists(os.path.join(app.path, _temp.split(':')[1])):
                            importable_files.append(os.path.join(app.path, _temp.split(':')[1]))

            if not importable_files:
                raise CommandError('Invalid source path specified!. You can supply as absolute path or app bounded path '
                                   '(app-label:relative path to app)')
            # We ignore further file traversing
        else:

            if getattr(settings, 'HACS_SERIALIZED_ROUTING_DIR', HACS_SERIALIZED_ROUTING_DIR):

                importable_files = glob.glob(os.path.join(
                    getattr(settings, 'HACS_SERIALIZED_ROUTING_DIR', HACS_SERIALIZED_ROUTING_DIR),
                    r'*.json')) + glob.glob(os.path.join(
                    getattr(settings, 'HACS_SERIALIZED_ROUTING_DIR', HACS_SERIALIZED_ROUTING_DIR),
                    r'*.xml'))
            if not kwargs['omit_app_dir_walking']:

                for app in apps.get_app_configs():

                    if os.path.exists(os.path.join(app.path, HACS_SERIALIZED_ROUTE_DIR_NAME)):

                        importable_files += glob.glob(os.path.join(app.path, HACS_SERIALIZED_ROUTE_DIR_NAME,
                                                                   r'*.json'))
                        importable_files += glob.glob(os.path.join(app.path, HACS_SERIALIZED_ROUTE_DIR_NAME,
                                                                   r'*.xml'))

        return importable_files

    def _normalize_unwanted_natural_keys(self, entries):
        """ """
        _allowed_models = (
            "%s.%s" % (SiteRoutingTable._meta.app_label, SiteRoutingTable._meta.model_name),
            "%s.%s" % (ContentTypeRoutingTable._meta.app_label, ContentTypeRoutingTable._meta.model_name),
        )
        for entry in entries:
            if entry['model'].lower() in _allowed_models:

                if isinstance(entry['fields']['site'], (list, tuple, )):
                    entry['fields']['site'] = Site.objects.get(domain=entry['fields']['site'][0]).pk

                if entry['model'].lower() == _allowed_models[1]:
                    if isinstance(entry['fields']['object_id'], (list, tuple)):
                        # Check if for Auth User Model
                        if UserModel._meta.app_label in entry['fields']['content_type'] and \
                                UserModel._meta.model_name in entry['fields']['content_type']:
                            entry['fields']['object_id'] = import_string(getattr(settings,
                                                                               'HACS_USER_OBJECT_QUERY_CALLABLE',
                                                                               HACS_USER_OBJECT_QUERY_CALLABLE)
                                                                       )(*entry['fields']['object_id']).pk

                        elif Group._meta.app_label in entry['fields']['content_type'] and Group._meta.model_name in \
                            entry['fields']['content_type']:
                            entry['fields']['object_id'] = \
                                Group.objects.get_by_natural_key(*entry['fields']['object_id']).pk




