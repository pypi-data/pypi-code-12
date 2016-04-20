import requests
import datetime
import time
from django.core.management.base import NoArgsCommand, CommandError
from django.contrib.sites.models import Site
from django.conf import settings
from ...models import URLStatusLog

#  Check one site every TIME_PER_SITE seconds
try:
    TIME_PER_SITE = datetime.timedelta(seconds=settings.TIME_PER_SITE)
except AttributeError:
    raise CommandError('TIME_PER_SITE not defined in settings.py')

try:
    SITES_TO_CHECK = settings.HEALTHCHECK_SITES
except AttributeError:
    raise CommandError('HEALTHCHECK_SITES not defined in settings.py')

class Command(NoArgsCommand):

    help = ('This command goes through all of the URLs for every site and '
            'returns the status code of each URL')

    def handle(self, *args, **options):
        while True:
            for site_id in SITES_TO_CHECK:
                start_time = datetime.datetime.now()
                try:
                    site = Site.objects.get(pk=int(site_id))
                except Site.DoesNotExist:
                    raise CommandError('Site with pk={} does not exist'.format(
                        site_id))

                self.check_url(site)
                self.stdout.write("Checked urls for '{}'".format(site))
                elapsed_time = datetime.datetime.now() - start_time
                remaining_time = (TIME_PER_SITE - elapsed_time).total_seconds()
                if remaining_time > 0:
                    time.sleep(remaining_time)



    def check_url(self, site):
        response = requests.get("http://{}".format(site.domain))
        if response.status_code == 200:
            site_is_up = True
        else:
            site_is_up = False

        current_time = datetime.datetime.now()

        try:
            log_entry = URLStatusLog.objects.get(site=site, url=site.domain)
            log_entry.site_is_up = site_is_up
            log_entry.latest_update=current_time
            log_entry.save()
        except URLStatusLog.DoesNotExist:
            URLStatusLog.objects.create(site=site, url=site.domain,
                                        site_is_up=site_is_up, latest_update=current_time)