"""Ingresse cliente for Ingresse's API
"""

import json
import requests
import datetime
import base64
import hmac
from hashlib import sha1

API_URL = 'https://api.ingresse.com'

class Client(object):

	public_key = None
	private_key = None

	def __init__(self, api_url=API_URL, public_key=None, private_key=None):
		"""Initialize the client

		:param string api_url: API base endpoint. Default is api production url. Default is 'https://api.ingresse.com/'.
		"""

		if not isinstance(api_url, str) or len(api_url.strip()) == 0:
			raise ApiException('api_url must be a string')

		if (public_key is None or private_key is None
			or not isinstance(public_key, str) or len(public_key.strip()) == 0
			or not isinstance(private_key, str) or len(private_key.strip()) == 0):
			raise ApiException('Please, provide your public and private API keys.')
		else:
			self.public_key = public_key
			self.private_key = private_key

		self.url = api_url

	def ingresseSignature(self):

		currentTimestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
		data1 = self.public_key + currentTimestamp
		data2 = hmac.new(self.private_key, data1, sha1).digest()
		signature = base64.b64encode(data2)

		return signature

	def callApi(self, properties=None, method=None, path=None, params=None):
		"""Sends an API call to Ingresse.

		:param dict properties: A dict of parameters to be sent through request body. Default is None.
		:param string method: API HTTP method to be used. Options: get, post.
		:param string path: API after base url. Ex.: events/234/session. Default is None.
		:param dict params: A dict of additional api method query. Optional.
		"""

		if params is None or not isinstance(params, dict):
			params = {}

		params.update({
			'publickey': self.public_key,
			'signature': self.ingresseSignature(),
			'timestamp': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
		})

		if not isinstance(properties, dict) and not properties is None:
			raise ApiException('Parameter \'properties\' must be a dictionay.')

		complete_url = API_URL + path

		if method == 'get':

			try:
				response = requests.get(complete_url,params=params)
				return Response(response)
			except requests.exceptions.RequestException as e:
				raise ApiException(str(e))

		elif method == 'post':

			try:
				response = requests.post(complete_url,params=params, data=properties)
				return Response(response)
			except requests.exceptions.RequestException as e:
				raise ApiException(str(e))

		else:
			raise ApiException('Parameter \'method\' not defined or invalid. Use \'get\' or \'post\'.')


	def getEvent(self, event_id):
		"""Retrieve a specific event Json object from Ingresse.

		:param int event_id: event id number
		"""

		response = self.callApi(
			method='get',
			path= '/event/' + str(event_id)
		)

		if response.is_ok():
			return str(response)
		else:
			return response.api_error_message

class Response(object):

	HTTP_CODES_WITHOUT_BODY = [204, 304]

	def __init__(self, http_response):
		"""Treat Ingresse API calls responses and return ApiException in case of a non valid JSON return or non 2xx HTTP status code.
		"""

		# Set Defaults
		self.body = None
		self.api_status = None
		self.api_error_code = None
		self.api_error_message = None
		self.api_error_category = None
		self.http_status_code = http_response.status_code
		self.http_request_url = http_response.url

		if self.http_status_code not in self.HTTP_CODES_WITHOUT_BODY:

			try:
				self.body = http_response.json()
				self.api_status = self.body['responseStatus']

				# Complete error information if responseError has attributes
				if 'message' in self.body.keys():
					self.api_error_message = self.body['responseError']['message']
					self.api_error_category = self.body['responseError']['category']
					self.api_error_code = self.body['responseError']['code']

			except ValueError:
				not_json_warning = "Failed to parse JSON response from {}. HTTP status code: {}".format(self.http_request_url, self.http_status_code)
				raise ApiException(not_json_warning)
			finally:
				if int(self.http_status_code) < 200 or int(self.http_status_code) >= 300:
					non_2xx_warning = "Failed to call {}. Returned non-2xx http status code: {}.".format(self.http_request_url, self.http_response_code)
					raise ApiException(non_2xx_warning)

	def __str__(self):
		return ('' if self.body is None else ('"body": ' + json.dumps(self.body) + ', ') + '{ "http_status_code": '+ str(self.http_status_code) + '}, { "http_request_url": '+ str(self.http_request_url) + '}')

	def is_ok(self):
		"""Verify API call response to define it has an error return or not.
		"""
		
		return (self.http_status_code is 200 and self.api_error_code is None)

class ApiException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)