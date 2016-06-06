# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url, include

from .views import ModelsDoc, ViewsDoc, PyDoc, Index


urlpatterns = patterns(
    '',
    url(r"^$", Index.as_view(),
        name='xray.index'),
    url(r"^models/", include(ModelsDoc.get_urls()),
        name='xray.models'),
    url(r"^views/", include(ViewsDoc.get_urls()),
        name='xray.views'),
    url(r"^pydoc/", include(PyDoc.get_urls()),
        name='xray.pydoc'),
)
