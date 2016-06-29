from molo.usermetadata import views

from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^persona/$', views.PersonaView.as_view(), name='persona'),
    url(
        r'^persona/skip/$',
        views.skip_persona, name='skip_persona'),
    url(
        r'^persona/(?P<persona_id>\d+)/$',
        views.set_persona, name='set_persona'),
)
