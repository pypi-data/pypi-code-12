import horntell
from horntell.http import request

class Campaign:

	def __init__(self):
		self.request = request.Request()

	#
	# Trigger campaign for a profile
	#
	def to_profile(self, uid, campaign_id, meta = None):
		data = {'meta': meta}

		return self.request.request(
			'post', '/profiles/' + uid + '/campaigns/' + campaign_id, data)

	#
	# Trigger campaign to multiple profiles
	#
	def to_profiles(self, profiles, campaign_id, meta = None):
		data = {'profile_uids': profiles, 'meta': meta}

		return self.request.request(
			'post', '/profiles/campaigns/' + campaign_id, data)


	#
	# Trigger campaign for a channel
	#
	def to_channel(self, uid, campaign_id, meta = None):
		data = {'meta': meta}

		return self.request.request(
			'post', '/channels/' + uid + '/campaigns/' + campaign_id, data)

	#
	# Trigger campaign to multiple channels
	#
	def to_channels(self, channels, campaign_id, meta = None):
		data = {'channel_uids': channels, 'meta': meta}

		return self.request.request(
			'post', '/channels/campaigns/' + campaign_id, data)
