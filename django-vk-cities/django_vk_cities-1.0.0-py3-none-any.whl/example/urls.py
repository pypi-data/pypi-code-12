# coding=utf-8

from django.contrib import admin
from django.conf.urls import url, include

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls))
]
