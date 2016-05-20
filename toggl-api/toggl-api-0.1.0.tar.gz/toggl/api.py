__authors__ = (
	"Mosab Ahmad <mosab.ahmad@gmail.com>",
	"Colin von Heuring <colin@von.heuri.ng>",
)

from urllib import urlencode

import requests
from requests.auth import HTTPBasicAuth


class TogglAPI(object):
	"""A wrapper for Toggl Api"""

	def __init__(self, api_token):
		self.api_token = api_token
		# self.timezone = timezone

	def _make_url(self, section='time_entries', params={}):
		"""
		Constructs and returns an api url to call with the section of the API
		to be called and parameters defined by key/pair values in the params
		dict.  Default section is "time_entries" which evaluates to
		"time_entries.json"

		>>> t = TogglAPI('_SECRET_TOGGLE_API_TOKEN_')
		>>> t._make_url(section='time_entries', params = {})
		'https://www.toggl.com/api/v8/time_entries'

		>>> t = TogglAPI('_SECRET_TOGGLE_API_TOKEN_')
		>>> params = {'start_date': '2010-02-05T15:42:46+02:00', 'end_date': '2010-02-12T15:42:46+02:00'}
		>>> t._make_url(section='time_entries', params=params)
		'https://www.toggl.com/api/v8/time_entries?start_date=2010-02-05T15%3A42%3A46%2B02%3A00%2B02%3A00&end_date=2010-02-12T15%3A42%3A46%2B02%3A00%2B02%3A00'
		"""

		url = 'https://www.toggl.com/api/v8/{}'.format(section)
		if len(params) > 0:
			url = url + '?{}'.format(urlencode(params))
		return url

	def _query(self, url, method):
		"""Performs the actual call to Toggl API"""

		url = url
		headers = {'content-type': 'application/json'}

		auth = HTTPBasicAuth(self.api_token, 'api_token')
		if method == 'GET':
			return requests.get(url, headers=headers, auth=auth)
		elif method == 'POST':
			return requests.post(url, headers=headers, auth=auth)
		else:
			raise ValueError('Unimplemented HTTP method "{}"'.format(method))

	def get_time_entries(self, start_date='', end_date=''):
		start_date = start_date.isoformat()
		end_date = end_date.isoformat()

		url = self._make_url(
			section='time_entries',
			params={'start_date': start_date, 'end_date': end_date},
		)
		r = self._query(url=url, method='GET')
		try:
			return r.json()
		except ValueError:
			raise ValueError(r.text)

	def get_hours_tracked(self, **kwargs):
		"""
		Count the total tracked hours excluding any RUNNING real time tracked
		time entries
		"""
		time_entries = self.get_time_entries(**kwargs)

		if time_entries is None:
			return 0

		total_seconds_tracked = sum(entry['duration'] for entry in time_entries)

		return total_seconds_tracked / 60.0 / 60.0


if __name__ == '__main__':
	import doctest
	doctest.testmod()
