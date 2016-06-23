from django.conf.urls import include, patterns, url
from .views import SupportLogView

urlpatterns = patterns('',
    url(r'^log/', SupportLogView.as_view(), name="support-log"),
)
