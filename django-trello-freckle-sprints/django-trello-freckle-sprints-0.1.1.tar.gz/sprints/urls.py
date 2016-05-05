"""URLs for the sprints app."""
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$',
        views.HomeView.as_view(),
        name='sprints_home'),
    url(r'^backlog/$',
        views.BacklogView.as_view(),
        name='sprints_backlog'),
    url(r'^sprint/$',
        views.SprintView.as_view(),
        name='sprints_sprint'),
]
