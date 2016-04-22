# -*- coding: utf-8 -*-
"""
    module.name
    ~~~~~~~~~~~~~~~
    Preamble...
"""
from __future__ import absolute_import, print_function, unicode_literals
from django.conf.urls import patterns, url

from ghostly.tests.django.testapp.views import ParameterisedTitleView

urlpatterns = [
    url(r'^test1/$', ParameterisedTitleView.as_view(template_name='testapp/test1.html'), name='test1'),
]
