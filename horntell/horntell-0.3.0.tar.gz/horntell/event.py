import horntell
import sys, urllib2, json, urlparse

class Event:

	#
	# return decoded payload from event
	#
	def fromWebhook(self):
		payload = sys.stdin.read()
		decodedPayload = urllib2.unquote(payload)
		return json.loads(urlparse.parse_qs(decodedPayload)['horntell_event'][0]);