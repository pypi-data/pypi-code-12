from django.conf.urls import url

from views import Import

urlpatterns = [
    url(
        r'^api/geotagx/(?P<project_id>[0-9]+)/import/$',
        Import.as_view(),
        name='import'),
]
