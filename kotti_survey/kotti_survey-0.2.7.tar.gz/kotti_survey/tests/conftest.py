# -*- coding: utf-8 -*-

"""
Created on 2016-06-15
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from pytest import fixture


pytest_plugins = "kotti"


@fixture(scope='session')
def custom_settings():
    import kotti_survey.resources
    kotti_survey.resources  # make pyflakes happy
    return {
        'kotti.configurators': 'kotti_tinymce.kotti_configure '
                               'kotti_survey.kotti_configure'}
