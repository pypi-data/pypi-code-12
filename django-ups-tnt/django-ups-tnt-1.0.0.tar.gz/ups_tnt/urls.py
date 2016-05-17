from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import TimeInTransitView


urlpatterns = patterns('',
    url(r'^tnt/$', TimeInTransitView.as_view(), name='time-in-transit'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
