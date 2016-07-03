import hashlib, hmac
import time
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings

from . models import UserSecret


class CodeBehindAuthentication(authentication.BaseAuthentication):
	"""
	This will check if the Signature of the client is valid.
	
	Client Headers:
		X-Username: the requester username
		Timestamp: the request timestamp in unix format
		Signature: = HMAC(user.secret, SHA(PATH + Timestamp))

	author: Michael Henry Pantaleon
			me@iamkel.net
	"""
	# this will handle the authentication of every request
	def authenticate(self, request):

		# server is converting the header's - to _ 
		username = request.META.get('HTTP_X_USERNAME')

		if not username:
			print "use other authentication method if available"
			return None

		path = request.META.get('PATH_INFO')
		client_timestamp = request.META.get('HTTP_TIMESTAMP')
		client_timestamp = int(client_timestamp) if client_timestamp else 0
		client_signature = request.META.get('HTTP_SIGNATURE')

		if not client_signature:
			print "maybe it is a basic authentication"

		if not username:
			raise exceptions.AuthenticationFailed('no username!')
			return None

		try:
			user = User.objects.get(username=username)
			print "valid user is %s" % username

			# this will generate raw message for signature
			message = "%s %s %d" % (request.method, path,client_timestamp)
			print "message is %s " % message

			# create an hmac signature base on user.secret
			hmac_obj = hmac.new(str(user.secret.key), message,hashlib.sha256)
			computed_signature = hmac_obj.hexdigest()

			server_time_unix = int(time.time())

			if settings.DEBUG:
				print "user name is %s " % username
				print "Client computed hmac is %s WITH hash256( %s , %s )" % (client_signature, path , client_timestamp)
				print "Server computed hmac is %s for user.secret = %s WITH hash256( %s , %s )" % (computed_signature, user.secret.key ,path , client_timestamp)
				print "server time = %d |-| client time = %d" % (server_time_unix,client_timestamp)

			#check for server time if client time stamp is still valid
			if not settings.DEBUG:
				if((server_time_unix - client_timestamp) > 60 * 2):
					raise exceptions.AuthenticationFailed('expired signature!')
					return None

			if not computed_signature == client_signature:
				raise exceptions.AuthenticationFailed('invalid authentication signature!')
				return None

		except User.DoesNotExist:
			raise exceptions.AuthenticationFailed('invalid user!')
		return (user, None)


