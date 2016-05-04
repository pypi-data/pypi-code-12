# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

from django_pypiwik.tracker import DjangoPiwikTracker


class PiwikTrackingMiddleware(object):

	def process_response(self, request, response):
		exclude_admin = getattr(settings, 'PIWIK_TRACKING_MIDDLEWARE_EXCLUDE_ADMIN', True) == True

		try:
			admin_url = reverse('admin:index')
		except NoReverseMatch:
			admin_url = None

		if exclude_admin and admin_url and request.path.startswith(admin_url):
			return response

		tracker = DjangoPiwikTracker.for_current_site(request=request)
		tracker.track_page_view(**getattr(settings, 'PIWIK_TRACKING_MIDDLEWARE_PARAMS', {}))
		return response
