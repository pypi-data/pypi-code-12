from django.conf.urls import patterns, url
from mint import views


urlpatterns = [
    url(r'^([a-z_]+)/([0-9]+)/([a-z_]+)/?$', views.with_id),
    url(r'^([a-z_]+)/([0-9]+)/?$', views.with_id),
    url(r'^([a-z_]+)/([a-z_]+)/?$', views.without_id),
    url(r'^([a-z_]+)/?$', views.without_id),
]