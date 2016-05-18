"""URLs for the eckerd-django-google-sso app."""
from django.conf.urls import include, url
from . import views
import social.apps.django_app.urls


urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'', include(social.apps.django_app.urls, namespace='social'))
]
