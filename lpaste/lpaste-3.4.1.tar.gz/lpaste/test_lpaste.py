from __future__ import absolute_import

import requests

from lpaste import lpaste


def test_user_agent():
	"""
	Ensure that passing the base headers doesn't break
	the request.
	"""
	requests.get('http://google.com', headers=lpaste.BASE_HEADERS)
