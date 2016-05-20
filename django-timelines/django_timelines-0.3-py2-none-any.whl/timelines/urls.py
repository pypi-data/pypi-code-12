# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .views import TimelineDetailView


urlpatterns = patterns('',
    url(r'^preview/(?P<slug>[-\w]*)/$',
        TimelineDetailView.as_view(),
        {'preview': True},
        name='timeline-detail-preview'),
    url(r'^preview/(?P<slug>[-\w]*)\.(?P<format>json)$',
        TimelineDetailView.as_view(),
        {'preview': True},
        name='timeline-detail-json-preview'),

    url(r'^(?P<slug>[-\w]*)/$',
        TimelineDetailView.as_view(),
        name='timeline-detail'),
    url(r'^(?P<slug>[-\w]*)\.(?P<format>json)$',
        TimelineDetailView.as_view(),
        name='timeline-detail-json'),
)
