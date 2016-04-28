from django.conf.urls import patterns, url

from .views import page_detail

urlpatterns = patterns(
    '',
    url(r'(.*)', page_detail)
)
