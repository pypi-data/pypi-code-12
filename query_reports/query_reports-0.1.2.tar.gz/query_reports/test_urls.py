from distutils.version import LooseVersion

from django.conf.urls import include, patterns, url
from django.contrib import admin
import django

from .urls import defaultpatterns


if LooseVersion(django.get_version()) <= LooseVersion("1.7.0"):
    admin.autodiscover()

urlpatterns = defaultpatterns + patterns(
    '',
    url(r'^admin/', include(admin.site.urls))
)
