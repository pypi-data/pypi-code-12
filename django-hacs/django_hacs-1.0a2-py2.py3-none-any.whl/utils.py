# -*- coding: utf-8 -*-
# ++ This file `utils.py` is generated at 3/5/16 10:02 AM ++
import os
import re
import copy
import glob
import json
import datetime
import warnings
import importlib
import collections
from django.apps import apps
from django.utils import six
from django.conf import settings
from django.utils import timezone
from django.utils._os import safe_join
from django.utils.encoding import smart_bytes
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.module_loading import module_has_submodule

from .models import SiteRoutingTable
from .globals import HACS_SITE_CACHE
from .defaults import HACS_FALLBACK_URLCONF
from .defaults import HACS_GENERATED_URLCONF_DIR
from .globals import HACS_GENERATED_FILENAME_PREFIX

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

UserModel = get_user_model()

urlconf_template = """# -*- coding: utf-8 -*-
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

admin.autodiscover()
urlpatterns = [
{urlpatterns}
]

{handlers}
"""


def set_site_urlconf(site):
    """
    :param site:
    :return:
    """
    try:
        site_route = SiteRoutingTable.objects.get(site=site)
    except SiteRoutingTable.DoesNotExist:
        warnings.warn(
                '%s has not assigned any route yet!' % site.domain
        )
        try:
            HACS_SITE_CACHE[site.domain].update(
                {'urlconf': getattr(settings, 'HACS_FALLBACK_URLCONF', HACS_FALLBACK_URLCONF)}
            )
        except KeyError:
            HACS_SITE_CACHE[site.domain] = \
                {'urlconf': getattr(settings, 'HACS_FALLBACK_URLCONF', HACS_FALLBACK_URLCONF)}
    else:
        # we are checking if file need to be created
        generate_urlconf_file_on_demand(site_route.route)
        generated_urlconf_module = get_generated_urlconf_module(get_generated_urlconf_file(site_route.route.route_name))

        try:
            HACS_SITE_CACHE[site.domain].update({'urlconf': generated_urlconf_module})
        except KeyError:
            HACS_SITE_CACHE[site.domain] = {'urlconf': generated_urlconf_module}


def get_site_urlconf(site):
    """
    @Linked to `lru_wrapped`
    :param site
    """
    try:
        # serve from cache
        return HACS_SITE_CACHE[site.domain]['urlconf']

    except KeyError:
        set_site_urlconf(site)
        return HACS_SITE_CACHE[site.domain]['urlconf']


def get_group_key(request, group, prefix='hacl', suffix=None):
    """
    @Linked to `lru_wrapped`
    :param request:
    :param group:
    :param prefix:
    :param suffix:
    :return:
    """
    if suffix is None:
        suffix = ''
    return "{prefix}:site_{site_id}:group_{group_id}{suffix}".\
        format(prefix=prefix, site_id=request.site.id, group_id=group.id, suffix=suffix)


def get_user_key(request, prefix='hacl', suffix=None):
    """
    @Linked to `lru_wrapped`
    :param request:
    :param prefix:
    :param suffix:
    :return:
    """
    if suffix is None:
        suffix = ''
    return "{prefix}:site_{site_id}:user_{user_id}{suffix}".\
        format(prefix=prefix, site_id=request.site.id, user_id=request.user.is_authenticated() and request.user.id or 0,
               suffix=suffix)


def get_generated_urlconf_file(route_name, prefix=None):
    """
    @Linked to `lru_wrapped`
    :param route_name
    :param prefix
    :return:
    """
    route_name = sanitize_filename(route_name)
    if prefix:
        prefix = sanitize_filename(prefix)
    else:
        prefix = HACS_GENERATED_FILENAME_PREFIX

    return safe_join(getattr(settings, 'HACS_GENERATED_URLCONF_DIR', HACS_GENERATED_URLCONF_DIR), "%s_%s_urls.py" %
                     (prefix, route_name))


def get_generated_urlconf_module(filename, validation=True):
    """
    @Linked to `lru_wrapped`
    :param filename:
    :param validation:
    :return:
    """
    if validation and not os.path.exists(filename):
        raise OSError("Specified file: %s does't exists!" % filename)

    return filename.split('/')[-1].split('.')[0]


def generate_urlconf_file_on_demand(route):
    """
    """
    generated_urlconf_file = get_generated_urlconf_file(route.route_name)
    route_updated_on = route.updated_on

    if route_updated_on:
        # Making Native datetime from offset-aware datetime.
        # See http://goo.gl/eHOIe2
        route_updated_on = route_updated_on.astimezone(timezone.utc).replace(tzinfo=None)

    # we are checking if file need to be created
    if not os.path.exists(generated_urlconf_file) or \
        (os.path.exists(generated_urlconf_file) and route_updated_on and
                 datetime.datetime.utcfromtimestamp(
                     os.path.getmtime(generated_urlconf_file)) < route_updated_on):
        # OK: we need to generate the file
        generate_urlconf_file(generated_urlconf_file, route)


def generate_urlconf_file(filename, route):
    """
    :param filename:
    :param route:
    :return:
    """
    with open(filename, 'w') as f:

        urlpatterns = ""

        for url in route.urls:
            url_module = url['url_module']
            if url.get('app_name'):
                if isinstance(url_module, six.string_types):
                    url_module = (url_module, url.get('app_name'))
                elif isinstance(url_module, (tuple, list, set)) and len(url_module) == 1:
                    url_module = tuple(url_module) + (url.get('app_name'))

            if not isinstance(url_module, six.string_types):
                if isinstance(url_module, (list, set)):
                    url_module = tuple(url_module)
                if isinstance(url_module, tuple):
                    if len(url_module) > 2:
                        url_module = url_module[0:2]
                        if not url.get('namespace'):
                            url['namespace'] = url_module[2]

                url_module = smart_bytes(url_module)
            else:
                # `admin.site.urls` is kind of special case, i. admin autodiscover
                if url_module != 'admin.site.urls':
                    url_module = "'%s'" % url_module

            urlpatterns += "\turl(r'{prefix}', include({url_module}{namespace})),\n".\
                format(prefix=url.get('prefix') + '/' if url.get('prefix', None) else '^', url_module=url_module,
                       namespace=url.get('namespace') and ", namespace='%s'" % url.get('namespace', None) or '')

        error_handlers = ''
        if route.handlers:
            for name, handler in route.handlers.items() or {}.items():
                error_handlers += "%s=\"%s\"\n" % (name, handler)

        f.write(copy.copy(urlconf_template).format(urlpatterns=urlpatterns, handlers=error_handlers))


def sanitize_filename(filename):
    """
    :param filename:
    :return:
    """
    filename = re.sub(r'[^A-Za-z0-9\-_]+', '', filename)

    return filename.replace('-', '_')


def get_installed_apps_urlconf(pattern=r'*urls.py', to_json=False, exclude=()):
    """
    @Linked to `lru_wrapped`
    :param pattern:
    :param to_json:
    :param exclude: apps those should be excluded
    :return:
    """
    result = collections.deque()
    handlers = (
        "handler400",
        "handler403",
        "handler404",
        "handler500",
    )
    if exclude and isinstance(exclude, six.string_types):
        exclude = (exclude, )

    for app in apps.get_app_configs():

        if app.label in exclude:
            continue

        # First try to files
        urlconf_modules = map(lambda x: '.'.join((app.name, x.replace(app.path, '').lstrip('/').split('.')[0]),),
                              glob.glob(os.path.join(app.path, pattern)))

        urlconf_dir = os.path.join(app.path, 'urls')

        if os.path.exists(urlconf_dir) and module_has_submodule(app.module, 'urls'):
            # we will try from urls module
            urls_module = importlib.import_module('.'.join((app.name, 'urls', )))
            if hasattr(urls_module, 'urlpatterns'):
                urlconf_modules += ['.'.join((app.name, 'urls', )), ]

            urlconf_modules += map(
                lambda x: '.'.join((app.name, 'urls', x.replace(app.path, '').lstrip('/').split('.')[0]), ),
                glob.glob(os.path.join(urlconf_dir, pattern)))

        if not urlconf_modules:
            continue

        for urlconf in urlconf_modules:

            urlconf_module = importlib.import_module(urlconf)
            if not hasattr(urlconf_module, 'urlpatterns'):
                continue

            error_handlers = collections.defaultdict(dict)
            for handler in handlers:
                if hasattr(urlconf_module, handler):
                    error_handlers[handler] = getattr(urlconf_module, handler)

            item = collections.namedtuple('app_' + app.name.replace('.', '_'), ['module', 'app_label', 'prefix', 'error_handlers'])
            result.append(item(module=urlconf, app_label=app.label, error_handlers=error_handlers, prefix=None))

    if to_json:
        return json.dumps(list(result), cls=DjangoJSONEncoder)
    else:
        return tuple(result)


def get_user_object(username_or_email_or_mobile, silent=True):
    """
    :param
    :param username_or_email_or_mobile:
    :param silent:
    :return:
    """
    try:
        return UserModel.objects.get(**{UserModel.USERNAME_FIELD: username_or_email_or_mobile})
    except UserModel.DoesNotExist:
        if not silent:
            raise
        return None

__all__ = (
    "set_site_urlconf",
    "get_site_urlconf",
    "get_group_key",
    "get_user_key",
    "get_generated_urlconf_file",
    "get_generated_urlconf_module",
    "generate_urlconf_file",
    "generate_urlconf_file_on_demand",
    "sanitize_filename",
    "get_installed_apps_urlconf",
    "get_user_object",
)

