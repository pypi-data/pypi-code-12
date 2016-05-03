# -*- coding: utf-8 -*-
from django.conf import settings

from django_pypiwik.tracker import DjangoPiwikTracker


class PiwikTrackingMiddleware(object):

	def process_response(self, request, response):
		tracker = DjangoPiwikTracker.for_current_site(request=request)
		tracker.track_page_view(**getattr(settings, 'PIWIK_TRACKING_MIDDLEWARE_PARAMS', {}))
		return response
