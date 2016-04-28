"""URLs to run the tests."""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()

urlpatterns = [
    url(r'^faq/', include('frequently.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('cms.urls')),
]

urlpatterns += staticfiles_urlpatterns()
