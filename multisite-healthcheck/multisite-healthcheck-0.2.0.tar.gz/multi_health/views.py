import datetime

from django.shortcuts import render
from django.conf import settings
from django.db.models import Q

from .models import URLStatusLog

#  Check one site every TIME_PER_SITE seconds
try:
    TIME_PER_SITE_INT = settings.TIME_PER_SITE
except AttributeError:
    raise CommandError('TIME_PER_SITE no defined in settings.py')

try:
    SITES_TO_CHECK = settings.HEALTHCHECK_SITES
except AttributeError:
    raise CommandError('HEALTHCHECK_SITES not defined in settings.py')


def multihealthview(request):
    template = "multi_health/results_table.html"
    queryset = URLStatusLog.objects.all()
    number_of_sites = len(SITES_TO_CHECK)
    # We're checking one site per x seconds, so we expect the oldest update for a site
    # to be at n*x seconds, where n is the number of sites.
    # We're adding x seconds at the end just in case.
    site_cutoff_seconds = number_of_sites * TIME_PER_SITE_INT + TIME_PER_SITE_INT
    site_cutoff_time = datetime.datetime.now() - datetime.timedelta(seconds=site_cutoff_seconds)


    # Return 500 if one of our sites isn't up or if the data is considered stale (too old).
    status_code = 500 if queryset.filter(Q(site_is_up=False) | Q(latest_update__lt=site_cutoff_time)).count() else 200
    return render(request, template, {'qs': queryset}, status=status_code)