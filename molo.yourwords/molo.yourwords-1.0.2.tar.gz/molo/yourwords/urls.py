from molo.yourwords import views

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required


urlpatterns = patterns(
    '',
    url(
        r'^entry/(?P<slug>[\w-]+)/$',
        login_required(views.CompetitionEntry.as_view()),
        name='competition_entry'),

    url(
        r'^thankyou/(?P<slug>[\w-]+)/$',
        login_required(views.ThankYouView.as_view()),
        name='thank_you'),
)
