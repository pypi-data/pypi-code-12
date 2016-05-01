from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models

class PiwikConfiguration(models.Model):
	site = models.OneToOneField(Site, related_name='piwik_configuration')

	piwik_url = models.URLField(default=getattr(settings, 'PIWIK_URL', ''))
	piwik_site_id = models.PositiveSmallIntegerField()
	piwik_token_auth = models.CharField(max_length=250, null=True, blank=True)