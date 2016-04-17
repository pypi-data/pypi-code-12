import urllib.parse

import requests
import pmxbot
from pmxbot.core import command


def _request_friendly(auth):
	"""
	Requests does strict type checking on the auth. If it's not a tuple, it
	tries to call it.
	"""
	if auth is not None:
		return tuple(auth)


@command()
def paste(client, event, channel, nick, rest):
	"Drop a link to your latest paste"
	path = '/last/{nick}'.format(**locals())
	paste_root = pmxbot.config.get('librarypaste', 'http://paste.jaraco.com')
	url = urllib.parse.urljoin(paste_root, path)
	auth = pmxbot.config.get('librarypaste auth')
	resp = requests.head(url, auth=_request_friendly(auth))
	if not resp.ok:
		return "I couldn't resolve a recent paste of yours. Maybe try " + url
	return resp.headers['location']
