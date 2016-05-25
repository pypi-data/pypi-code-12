"""
urls for ip registry (iprir) project
"""

from django.conf.urls import include, url
from django.contrib import admin

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ip/(?P<address>\d+\.\d+.\d+.\d+)/$', views.json_by_ip, name='json_by_ip'),
    url(r'^dict/(?P<address>\d+\.\d+.\d+.\d+)/$', views.dict_by_ip, name='dict_by_ip'),
    url(r'^registry/(?P<registry_id>\d+)/$', views.registry_by_id, name='registry_by_id'),
    url(r'^registry/(?P<registry_desc>\w+)/$', views.registry_by_desc, name='registry_by_desc'),
    url(r'^tld/(?P<tld_domain>\w{2})/$', views.tld_by_domain, name='tld_by_domain'),
    url(r'^admin/', include(admin.site.urls)),
]
