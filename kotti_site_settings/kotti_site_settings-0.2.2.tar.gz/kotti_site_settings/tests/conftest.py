# -*- coding: utf-8 -*-

"""
Created on 2016-06-15
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

pytest_plugins = "kotti"

from pytest import fixture


@fixture(scope='session')
def custom_settings():
    import kotti_site_settings.resources
    kotti_site_settings.resources  # make pyflakes happy
    return {
        'kotti.configurators': 'kotti_tinymce.kotti_configure '
                               'kotti_site_settings.kotti_configure'}
