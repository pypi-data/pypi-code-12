# -*- coding: utf-8 -*-

"""
Created on 2016-06-15
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from kotti.resources import File
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('kotti_site_settings')


def kotti_configure(settings):
    """ Add a line like this to you .ini file::

            kotti.configurators =
                kotti_site_settings.kotti_configure

        to enable the ``kotti_site_settings`` add-on.

    :param settings: Kotti configuration dictionary.
    :type settings: dict
    """

    settings['pyramid.includes'] += ' kotti_site_settings'
    settings['kotti.alembic_dirs'] += ' kotti_site_settings:alembic'
    settings['kotti.available_types'] += (
        ' kotti_site_settings.resources.AppSettingsPage'
    )
    settings['kotti.fanstatic.view_needed'] += (
        ' kotti_site_settings.fanstatic.css_and_js'
    )


def includeme(config):
    """ Don't add this to your ``pyramid_includes``, but add the
    ``kotti_configure`` above to your ``kotti.configurators`` instead.

    :param config: Pyramid configurator object.
    :type config: :class:`pyramid.config.Configurator`
    """

    config.add_translation_dirs('kotti_site_settings:locale')
    config.add_static_view('static-kotti_site_settings', 'kotti_site_settings:static')

    config.scan(__name__)
