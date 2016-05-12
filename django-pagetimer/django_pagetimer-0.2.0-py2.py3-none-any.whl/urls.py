from django.conf.urls import url
from django.contrib.auth.decorators import user_passes_test

import pagetimer.views as views

urlpatterns = [
    url('^$', user_passes_test(lambda x: x.is_superuser)(
        views.DashboardView.as_view(
            paginate_by=100,
        )), name='pagetimer-dashboard'),
    url('^filter/$', user_passes_test(lambda x: x.is_superuser)(
        views.FilterView.as_view(
            paginate_by=100,
        )), name='pagetimer-filter'),
    url('^csv/$', user_passes_test(lambda x: x.is_superuser)(
        views.CSVView.as_view()), name='pagetimer-csv'),
    url('^purge/$', user_passes_test(lambda x: x.is_superuser)(
        views.PurgeView.as_view()), name='pagetimer-purge'),
    url('^endpoint/$', views.PageTimerEndpointView.as_view(),
        name='pagetimer-endpoint')
]
