from django.conf.urls import patterns, url
from .views import multihealthview


urlpatterns = patterns('multi_health.views',
                       url(r'^$', multihealthview,
                           name="multihealth"),
                       )