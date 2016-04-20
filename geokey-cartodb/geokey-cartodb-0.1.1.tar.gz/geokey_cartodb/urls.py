from django.conf.urls import patterns, url

from views import (
    IndexPage, ProjectDataView
)

urlpatterns = patterns(
    '',
    url(
        r'^admin/cartodb/$',
        IndexPage.as_view(),
        name='index'),
    url(
        r'^api/cartodb/projects/(?P<project_id>[0-9]+)$',
        ProjectDataView.as_view(),
        name='project_data')
)
