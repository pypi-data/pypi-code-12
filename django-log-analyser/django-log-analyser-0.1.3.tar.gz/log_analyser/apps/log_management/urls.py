from __future__ import absolute_import

from django.conf.urls import url

from log_analyser.apps.log_management.views import get_report


urlpatterns = [
    url(r'^get-report/(?P<log_report_obj_id>\d+)', get_report, name='get-report'),
]
