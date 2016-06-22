# -*- coding: utf-8 -*-

import copy
import logging.config
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

LOGGING_CONFIG_ERROR_MSG = """You must first disable Django's default logging by
                           setting LOGGING_CONFIG = None before using this config
                           helper"""

# By default, log to the console (stream) with 'simple' formatting and a catch-
# all logger for WARNING or higher messages.
DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s\t%(asctime)s.%(msecs)03dZ\t%(name)s:%(lineno)s\t%(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s\t%(name)s:%(lineno)s\t%(message)s',
        }
    },
    'handlers': {
        'default': {
            'level': logging.DEBUG,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    # This is the default logger for any apps or libraries that use the logger
    # package, but are not represented in the `loggers` dict below.  A level
    # must be set and handlers defined.  Setting this logger is equivalent to
    # setting an empty string logger in the loggers dict below, but the
    # separation here is a bit more explicit.  See link for more details:
    # https://docs.python.org/2.7/library/logging.config.html#dictionary-schema-details
    'root': {
        'level': logging.WARNING,
        'handlers': ['default'],
    },
}


def _normalize_apps(apps_list):
    """ Given a list of dotted application package paths and/or app config
    classes, return a set of the top level app package names. The resulting
    set will be used to generate the log handlers for this project. """
    return {app.split('.')[0] for app in apps_list}


def build_normalized_app_loggers(log_level, apps_list, handlers=None):
    """ Return a logger dict for app packages with the given log level and no
    propogation since the apps list is parsed/normalized to be the set of top-
    level apps.  The optional handlers argument is provided so that this pattern
    of app loggers can be used independently of the configure_logger method
    below, if desired.
    """
    apps = _normalize_apps(apps_list)

    # Use 'default' handler provided by DEFAULT_LOGGING config if
    # not supplied.
    if handlers is None:
        handlers = ['default']

    # The log config expects the handlers value to be a list, so let's
    # make sure of that here.
    if not isinstance(handlers, list):
        handlers = list(handlers)

    app_loggers = {}
    for app in apps:
        app_loggers[app] = {
            'level': log_level,
            'handlers': handlers,
            'propagate': False,
        }

    return app_loggers


def _build_config(level, apps_list, verbose, filename=None):
    """ Return a copy of the DEFAULT_LOGGING config with installed application
    loggers at the given log level.  The 'default' handler is kept as a
    console/stream writer unless a filename is passed in, which swaps the stream
    handler out for a file handler.  The 'verbose' formatter is used if
    verbosity is enabled. """
    config = copy.deepcopy(DEFAULT_LOGGING)

    # Swap out default stream handler for a file handler, if
    # a filename is given
    if filename:
        config['handlers']['default'].update(
            {
                'class': 'logging.handlers.WatchedFileHandler',
                'filename': filename,
            }
        )

    if verbose:
        config['handlers']['default']['formatter'] = 'verbose'

    config['loggers'] = build_normalized_app_loggers(
        level, apps_list)

    return config


def configure_installed_apps_logger(level, verbose=False, filename=None):
    """Builds and enables a logger with a logger list of the top-level list of
    installed app modules (based on package name).  The logger will write either
    to the console or to a file based on the presence of the filename parameter.
    Check that the LOGGING_CONFIG setting is None before we configure the logger
    in order to prevent maintaining Django's list of log handlers."""
    if settings.LOGGING_CONFIG:
        raise ImproperlyConfigured(LOGGING_CONFIG_ERROR_MSG)

    config = _build_config(
        level, settings.INSTALLED_APPS, verbose, filename)

    logging.config.dictConfig(config)
