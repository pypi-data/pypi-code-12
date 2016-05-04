# -*- coding: utf-8 -*-

from pypiwik.tracker import PARAMETERS as PIWIK_PARAMETERS
from django_pypiwik.tracker import DjangoPiwikTracker


class PiwikMixin(object):

	def get_context_data(self, **kwargs):
		context = super(PiwikMixin, self).get_context_data(**kwargs)
		context['piwik_tracker'] = self.piwik_tracker
		return context

	@property
	def piwik_tracker(self):
		if not hasattr(self, '_piwik_tracker'):
			self._piwik_tracker = DjangoPiwikTracker.for_current_site(self.request)

		self._piwik_tracker.update(self._get_piwik_params())
		return self._piwik_tracker

	def _get_piwik_params(self):
		params = {}

		for param_name in PIWIK_PARAMETERS.keys():
			my_attr = getattr(self, 'piwik_%s' % param_name, None)

			if not my_attr:
				continue

			value = my_attr() if callable(my_attr) else my_attr

			if value:
				params[param_name] = value

		return params