from __future__ import unicode_literals

import os
import sys

from wenlincms.conf import settings


def has_site_permission(user):
    """
    Checks if a staff user has staff-level access for the current site.
    The actual permission lookup occurs in ``SitePermissionMiddleware``
    which then marks the request with the ``has_site_permission`` flag,
    so that we only query the db once per request, so this function
    serves as the entry point for everything else to check access. We
    also fall back to an ``is_staff`` check if the middleware is not
    installed, to ease migration.
    """
    mw = "wenlincms.core.middleware.SitePermissionMiddleware"
    if mw not in settings.MIDDLEWARE_CLASSES:
        from warnings import warn
        warn(mw + " missing from settings.MIDDLEWARE_CLASSES - per site"
                  "permissions not applied")
        return user.is_staff and user.is_active
    return getattr(user, "has_site_permission", False)


def host_theme_path(request):
    """
    Returns the directory of the theme associated with the given host.
    """
    for (host, theme) in settings.HOST_THEMES:
        if host.lower() == request.get_host().split(":")[0].lower():
            try:
                __import__(theme)
                module = sys.modules[theme]
            except ImportError:
                pass
            else:
                return os.path.dirname(os.path.abspath(module.__file__))
    return ""


def templates_for_host(request, templates):
    """
    Given a template name (or list of them), returns the template names
    as a list, with each name prefixed with the device directory
    inserted into the front of the list.
    """
    if not isinstance(templates, (list, tuple)):
        templates = [templates]
    theme_dir = host_theme_path(request)
    host_templates = []
    if theme_dir:
        for template in templates:
            host_templates.append("%s/templates/%s" % (theme_dir, template))
            host_templates.append(template)
        return host_templates
    return templates
