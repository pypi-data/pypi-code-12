from django.conf.urls import include, patterns, url
from wagtail.wagtailcore import urls as wagtail_urls

from .. import urls as kagiso_search_urls


urlpatterns = patterns(
    '',
    url(r'', include(wagtail_urls)),
    url(r'', include(kagiso_search_urls)),
)
