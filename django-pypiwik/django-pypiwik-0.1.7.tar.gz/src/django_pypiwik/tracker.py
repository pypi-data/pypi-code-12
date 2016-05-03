# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from django_pypiwik.models import PiwikConfiguration
from pypiwik.tracker import PiwikTracker


class DjangoPiwikTracker(PiwikTracker):

	def __init__(self, *args, **kwargs):
		d = getattr(settings, 'PIWIK_PARAMS', {})
		d.update(kwargs.get('values', {}))
		kwargs['values'] = d
		super(DjangoPiwikTracker, self).__init__(*args, **kwargs)

	@staticmethod
	def for_current_site(*args, **kwargs):
		try:
			config = PiwikConfiguration.objects.get(site=Site.objects.get_current())
			if config.piwik_token_auth:
				kwargs.setdefault('token_auth', config.piwik_token_auth)
			return DjangoPiwikTracker(config.piwik_url, config.piwik_site_id, *args, **kwargs)
		except PiwikConfiguration.DoesNotExist:
			token_auth = getattr(settings, 'PIWIK_TOKEN_AUTH', None)
			if token_auth:
				kwargs.setdefault('token_auth', token_auth)
			return DjangoPiwikTracker(settings.PIWIK_URL, settings.PIWIK_SITE_ID, *args, **kwargs)

	def track_page_view(self, **kwargs):
		if settings.DEBUG and not getattr(settings, 'PIWIK_ALLOW_DEBUG', False):
			logging.info("track_page_view() intercepted because settings.DEBUG = True and not overriden with settings.PIWIK_ALLOW_DEBUG = True")
		else:
			return super(DjangoPiwikTracker, self).track_page_view(**kwargs)

	def tracking_code(self):
		if settings.DEBUG and not getattr(settings, 'PIWIK_ALLOW_DEBUG', False):
			return mark_safe("""<!-- Piwik tracking code not generated because settings.DEBUG = True and not overridden with settings.PIWIK_ALLOW_DEBUG = True -->""")
		else:
			return mark_safe(super(DjangoPiwikTracker, self).tracking_code())
