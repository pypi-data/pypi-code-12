"""URLs for the server_guardian app."""
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$',
        views.GuardianDashboardView.as_view(),
        name='server_guardian_dashboard'),
    url(r'^reload/$',
        views.GuardianReloadView.as_view(),
        name='server_guardian_reload'),
]
