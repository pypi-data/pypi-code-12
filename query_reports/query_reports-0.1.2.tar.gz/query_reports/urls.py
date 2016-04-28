from django.conf.urls import *
from .views import ShowReportView

defaultpatterns = patterns('', url(r'^qreports/', include('query_reports.urls')))

urlpatterns = patterns('query_reports.views',
    url(r'^$', 'report_index', name='qreports-report-index'),
    url(r'^(?P<slug>[\w-]+)/$', ShowReportView.as_view(), name='qreports-show-report'),
)
