# -*- coding: utf-8 -*-
from functools import wraps
from django_pypiwik.tracker import DjangoPiwikTracker
from pypiwik.decorators import track_page_view as pp_track_page_view
from django.utils.decorators import available_attrs


def track_page_view(**tracker_kwargs):
	def decorator(func):
		@wraps(func, assigned=available_attrs(func))
		def inner(request, *args, **kwargs):
			@pp_track_page_view(tracker=DjangoPiwikTracker.for_current_site(request=request, **tracker_kwargs))
			def inner2():
				return func(request, *args, **kwargs)
			return inner2()
		return inner
	return decorator