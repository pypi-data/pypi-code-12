"""URLs to run the tests."""
from django.conf.urls import include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = [
    url(r'', include('server_guardian.urls')),
    url(r'^api/', include('server_guardian_api.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
