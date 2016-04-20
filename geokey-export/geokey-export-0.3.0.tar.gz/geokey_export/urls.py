from django.conf.urls import include, url

from rest_framework.urlpatterns import format_suffix_patterns

from views import (
    IndexPage,
    ExportOverview,
    ExportCreate,
    ExportDelete,
    ExportToRenderer,
    ExportGetExportContributions,
    ExportGetProjectCategories,
    ExportGetProjectCategoryContributions
)


datapatterns = [
    url(
        r'^admin/export/(?P<urlhash>[\w-]+)$',
        ExportToRenderer.as_view(),
        name='export_to_renderer')
]
datapatterns = format_suffix_patterns(datapatterns, allowed=['json', 'kml'])


urlpatterns = [
    url(
        r'^admin/export/$',
        IndexPage.as_view(),
        name='index'),
    url(
        r'^admin/export/(?P<export_id>[0-9]+)/$',
        ExportOverview.as_view(),
        name='export_overview'),
    url(
        r'^admin/export/(?P<export_id>[0-9]+)/contributions/$',
        ExportGetExportContributions.as_view(),
        name='export_get_export_contributions'),
    url(
        r'^admin/export/(?P<export_id>[0-9]+)/delete/$',
        ExportDelete.as_view(),
        name='export_delete'),
    url(
        r'^admin/export/create/$',
        ExportCreate.as_view(),
        name='export_create'),
    url(
        r'^admin/export/projects/(?P<project_id>[0-9]+)/categories/$',
        ExportGetProjectCategories.as_view(),
        name='export_get_project_categories'),
    url(
        r'^admin/export/projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/contributions/$',
        ExportGetProjectCategoryContributions.as_view(),
        name='export_get_project_category_contributions'),
    url(
        r'^', include(datapatterns))
]
