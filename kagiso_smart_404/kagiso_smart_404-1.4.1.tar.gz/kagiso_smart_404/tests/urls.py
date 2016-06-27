from django.conf.urls import include, url
from wagtail.wagtailcore import urls as wagtail_urls


urlpatterns = [
    url(r'', include(wagtail_urls)),
]

handler404 = 'kagiso_smart_404.views.not_found'
