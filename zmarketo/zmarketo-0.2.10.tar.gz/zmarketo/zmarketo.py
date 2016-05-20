import json
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# TODO:
# Better api return values (raw funcs, and formatted funcs)
	# Mostly just:
	# {skipped: }
	# And single vs. bulk funcs.
# Docstrings and generate docs.
# Add all the Marketo rest functions
# Tests for each method
# More elegant handling of the marketo api check decorator. (Magic mock.)
# Handle unicode better (import unicode literal?)
# Possible future settings:
# Optional:
# isDev: bool (False)
# shouldCache: bool (False)
# Fix naming convention of error classes.
# Fix tests so they have their versions locked in. (virtualenv? requirements.txt?)

class MarketoInvalidInputException(Exception):
	def _make_response_str(self, message):
		return u"Marketo Api has invalid input: {}: ".format(message)

	def __init__(self, message):
		super(MarketoInvalidInputException, self).__init__(self._make_response_str(message))
		self.message = message

	def __str__(self):
		return self._make_response_str(self.message)

class BadRequest(Exception):
	def _make_response_str(self, code, body):
		return u"Request was bad. Response code: {}, Response body {}".format(code, body)

	def __init__(self, response_code, response_body):
		super(BadRequest, self).__init__(self._make_response_str(response_code, response_body))
		self.code = response_code
		self.body = response_body

	def __str__(self):
		return self._make_response_str(self.code, self.body)

class MarketoApiError(Exception):
	ERROR_CODES = {
		'413': 'Payload exceeded 1MB limit.',
		'414': ('URI of the request exceeded 8k. The request should be retried as a POST with param _method=GET in the URL,'
					' and the rest of the querystring in the body of the request.'),
		'601': 'An Access Token parameter was included in the request, but the value was not a valid access token.',
		'602': 'The Access Token included in the call is no longer valid due to expiration.',
		'603': ('Authentication is successful but user doesn\'t have sufficient permission to call this API. '
					'Additional permissions may need to be assigned to the user role.'),
		'604': 'The request was running for too long, or exceeded the time-out period specified in the header of the call.',
		'605': 'GET is not supported for syncLead, POST must be used.',
		'606': 'The number of calls in the past 20 seconds was greater than 100',
		'607': 'Number of calls today exceeded the subscription\'s quota.  The default subscription quota is 10,000/day.',
		'608': 'API Temporarily Unavailable',
		'609': 'The body included in the request is not valid JSON.',
		'610': 'The URI in the call did not match a REST API resource type.  This is often due to an incorrectly spelled or incorrectly formatted request URI',
		'611': 'All unhandled exceptions',
		'612': ('If you see this error, add a content type header specifying JSON format to your request. For example, try using "content type: application/json".'
					'Please see this (http://stackoverflow.com/questions/28181325/why-invalid-content-type) StackOverflow question for more details.'),
		'613': 'The multipart content of the POST was not formatted correctly',
		'701': 'The reported field must not be empty in the request',
		'702': 'No records matched the given search parameters',
		'703': 'A beta feature that has not been in enabled in a user\'s subscription',
		'704': 'A date was specified that was not in the correct format',
		'709': 'The call cannot be fulfilled because it violates a requirement to create up update an asset, e.g. trying to create an email without a template.',
		'710': 'The specified parent folder could not be found',
		'711': 'The specified folder was not of the correct type to fulfill the request',
		'1001': 'Error is generated whenever parameter value has type mismatch. For example string value specified for integer parameter.',
		'1002': 'Error is generated when required parameter is missing from the request',
		'1003': 'Ex: When proper action (createOnly, createOrUpdate ..etc) not specified.',
		'1004': 'For syncLead, when action is "updateOnly" and if lead is not found',
		'1005': 'For syncLead, when action is "createOnly" and if lead already exists',
		'1006': 'An included field in the call is not a valid field.',
		'1007': 'Multiple leads match the lookup criteria.  Updates can only be performed when the key matches a single record',
		'1008': 'The user for the custom service does not have access to a workspace with the partition where the record exists.',
		'1010': 'The specified record already exists in a separate lead partition.',
		'1011': 'When lookup field or filterType specified with unsupported standard fields (ex: firstName, lastName ..etc)',
		'1013': 'Get object (list, campaign ..etc) by id will return this error code',
		'1014': 'Failed to create Object (list, ..etc)',
		'1015': 'The designated lead is not a member of the target list',
		'1016': 'There are too many imports queued.  A maximum of 10 is allowed',
		'1017': 'Creation failed because the record already exists',
		'1018': 'The action could not be carried out, because the instance has a native CRM integration enabled.',
		'1019': 'The target list is already being imported to',
		'1020': 'The subscription has reached the alotted uses of cloneToProgramName in Schedule Program for the day',
		'1021': 'Company update not allowed during syncLead',
		'1022': 'Delete is not allowed when an object is in use by another object',
	}

	def make_response_str(self, errors, request_args):
		response_str = u"Marketo API Error for {}.".format(request_args if request_args else '()')
		for error in errors:
			error_code = error.get('code')
			description = self.ERROR_CODES.get(error_code, 'No description for this code')
			response_str += u"\nError code: {}. message: {}. Error description: {}\n".format(error_code, error.get('message'), description)

		return response_str

	def __init__(self, errors, request_args):
		super(MarketoApiError, self).__init__(self.make_response_str(errors, request_args))
		self.errors = errors
		self.request_args = request_args

	def __str__(self):
		return repr(self.make_response_str(self.errors, self.request_args))


# Seperate the retry and the processing of results.
def handle_rest_response(requestMethod):
	def response_handler(*args, **kwargs):
		self = args[0]
		def handle_response(retry_count=0):
			logger.info("Marketo Rest API returned called with args {} and kwargs {}".format(
				args, kwargs))
			resp = requestMethod(*args, **kwargs)
			response_data = resp.json()

			if resp.status_code != 200:
				raise BadRequest(resp.status_code, response_data)
			elif not response_data['success']:
				errors = response_data["errors"]

				for error in errors:
					logger.info("Marketo Rest API returned error {} with args {} and kwargs {}".format(
						error.get('code'), args, kwargs))
					if error.get('code') in ['601', '602'] and retry_count < 2:
						self.token_params = {'access_token': self._get_marketo_access_token()}
						retry_count += 1
						return handle_response(retry_count=retry_count)

				raise MarketoApiError(errors, args)
			else:
				logger.info("Marketo Rest API returned success response {} with args {} and kwargs {}".format(
					response_data, args, kwargs))
				return response_data

		return handle_response()
	return response_handler

def listToCommaStr(l):
	return ','.join(map(str, l))

class MarketoRest(object):
	URL_ENDPOINT = "https://180-gfh-982.mktorest.com"
	IDENTITY = "https://180-GFH-982.mktorest.com/identity"

	def __init__(self, client_id, client_secret, session=None):
		if not session:
			session = requests.Session()

		self.client_id = client_id
		self.client_secret = client_secret

		session.headers.update({'content-type': 'application/json;charset=UTF-8'})
		self.request_session = session

		self.token_params = {'access_token': self._get_marketo_access_token()}

	@handle_rest_response
	def get_with_handler(self, url, params={}):
		params.update(self.token_params)
		return self.request_session.get(url, params=params)

	@handle_rest_response
	def post_with_handler(self, url, data={}, params={}):
		params.update(self.token_params)
		return self.request_session.post(url, data=data, params=params)

	def _get_marketo_access_token(self):
		"""
		Marketo Docs for getting access code
		http://developers.marketo.com/documentation/rest/authentication/
		"""

		auth_query = {
			'grant_type': 'client_credentials',
			'client_id': self.client_id,
			'client_secret': self.client_secret,
		}

		marketo_auth_url = '{0}{1}'.format(self.URL_ENDPOINT, '/identity/oauth/token')
		auth_response = self.request_session.get(marketo_auth_url, params=auth_query)
		token = auth_response.json().get('access_token')

		if auth_response.status_code != 200 or not token:
			raise BadRequest(auth_response.status_code, auth_response.content)

		return token

	def get_lead_by_id(self, leadId, fields=None):
		"""
		Docs at http://developers.marketo.com/documentation/rest/get-lead-by-id/
		"""
		url = u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/lead/{}.json'.format(leadId))

		params = {}

		if fields:
			params.update({'fields': listToCommaStr(fields)})

		resp = self.get_with_handler(url, params=params)

		return resp['result']

	def get_leads_by_filter_type(self, filter_type, filter_values, fields=None, batch_size=300, next_page_token=None):
		"""
		Docs at http://developers.marketo.com/documentation/rest/get-multiple-leads-by-filter-type
		"""

		get_lead_endpoint = '/rest/v1/leads.json'
		url_params = {'filterType': filter_type, 'batchSize': batch_size}

		if fields:
			url_params['fields'] = listToCommaStr(fields)

		if next_page_token:
			url_params['nextPageToken'] = next_page_token

		if type(filter_values) == list:
			url_params['filterValues'] = listToCommaStr(filter_values)
		else:
			url_params['filterValues'] = filter_values

		resp = self.get_with_handler('{0}{1}'.format(self.URL_ENDPOINT, get_lead_endpoint), params=url_params)

		return resp['result']

	def get_multiple_leads_by_list_id(self, listId, batch_size=300, next_page_token=None, fields=None):
		url = u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/list/{}/leads.json'.format(listId))
		params = {'batchSize': batch_size}

		if next_page_token:
			params.update({'nextPageToken': next_page_token})

		if fields:
			params.update({'fields': listToCommaStr(fields)})

		resp = self.get_with_handler('{0}{1}'.format(self.URL_ENDPOINT, url), params=params)

		return resp['result']


	def get_pagination_api_token(self, date=None):
		get_pagination_api_token_endpoint = '/rest/v1/activities/pagingtoken.json'

		if not date:
			date = datetime.utcnow() - timedelta(minutes=30)

		request_data = {'sinceDatetime': date.strftime("%Y-%m-%dT%H:%M-%S:00")}
		resp = self.get_with_handler('{0}{1}'.format(self.URL_ENDPOINT, get_pagination_api_token_endpoint), params=request_data)

		return resp['nextPageToken']

	def describe(self):
		"""
		Marketo Docs for describing leads:
		http://developers.marketo.com/documentation/rest/describe/
		"""

		url = u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/leads/describe.json')
		resp = self.get_with_handler(url)

		return resp['result']

	def create_or_update_leads(self, leads, lookup_field='email', action='createOrUpdate', async_processing=False, partition_name=None):
		"""
		Marketo Docs for creating/updating leads http://developers.marketo.com/documentation/rest/createupdate-leads/
		"""
		post_data = {
			'lookupField': lookup_field,
			'input': leads,
			'action': action,
			'asyncProcessing': async_processing
		}

		if partition_name:
			post_data.update({'partitionName': partition_name})

		resp = self.post_with_handler(
			'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/leads.json'),
			data=json.dumps(post_data)
		)

		return resp['result']

	def associate_lead(self, lead_id, cookie):
		url = '/rest/v1/leads/{}/associate.json'.format(lead_id)

		post_params = {'cookie': cookie}

		self.post_with_handler('{0}{1}'.format(self.URL_ENDPOINT, url), params=post_params)

		# Will throw exception if it does not succeed
		return True

	def merge_lead(self, winning_lead_id, losing_lead_ids, merge_in_crm=False):
		url = '/rest/v1/leads/{id}/merge.json'.format(winning_lead_id)

		post_data = {'mergeInCRM': merge_in_crm}

		if len(losing_lead_ids) == 1:
			post_data.update({'leadId': losing_lead_ids[0]})
		else:
			post_data.update({'leadIds': listToCommaStr(losing_lead_ids)})

		self.post_with_handler('{0}{1}'.format(self.URL_ENDPOINT, url), data=json.dumps(post_data))

		return True

	def get_lead_partitions(self):
		return self.get_with_handler(u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/leads/partitions.json'))['result']


	def get_list_by_id(self, list_id):
		url = '/rest/v1/lists/{}.json'.format(list_id)
		return self.get_with_handler(u'{0}{1}'.format(self.URL_ENDPOINT, url))['result']

	def remove_leads_from_list(self, list_id, lead_ids):
		post_data = {'input': listToCommaStr(lead_ids), '_method': 'POST'}
		url = '/rest/v1/lists/{}/leads.json'.format(list_id)

		resp = self.post_with_handler('{0}{1}'.format(self.URL_ENDPOINT, url), data=json.dumps(post_data))

		return resp['result']

	def get_campaign_by_id(self, campaign_id):
		return self.get_with_handler(u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/campaigns/{}.json'.format(campaign_id)))['result']

	def get_lead_activities(self, activity_type_ids, next_page_token, batch_size=300, list_id=None):
		params = {'activityTypeIds': activity_type_ids, 'nextPageToken': next_page_token, 'batchSize': batch_size}

		if list_id:
			params.update(list_id)

		resp = self.get_with_handler(
			u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/activities.json'),
			params=params
		)

		return resp.get('result', []), resp.get('nextPageToken', None), resp.get('moreResult')

	# TODO
	# def member_of_list(self):
	# 	pass

	# def get_multiple_lists(self):
	# 	pass

	# def get_multiple_campaigns(self):
	# 	pass

	# def schedule_campaign(self, campaign_id, run_at=None, clone_to_program_name=None, tokens=None):
	# 	pass

	# def request_campaign(self):
	# 	pass

	# def import_lead(self):
	# 	pass

	# def get_import_failure_file(self):
	# 	pass

	# def get_import_warning_file(self):
		# pass

	# def delete_lead(self):
	# 	pass

	def get_import_lead_status(self, batch_id):
		return self.get_with_handler(
			u'{0}{1}'.format(self.URL_ENDPOINT, '/bulk/v1/leads/batch/{}.json'.format(batch_id))
		)['result']

	def get_activity_types(self):
		return self.get_with_handler(
			u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/activities/types.json')
		)['result']

	def get_daily_usage(self):
		return self.get_with_handler(
			u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/stats/usage.json')
		)['result']

	def get_weekly_usage(self):
		return self.get_with_handler(
			u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/stats/usage/last7days.json')
		)['result']

	def get_daily_errors(self):
		return self.get_with_handler(
			u'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/stats/errors.json')
		)['result']

	def add_leads_to_list(self, lead_ids, list_id):
		"""
		Lead Ids is expected to be [{'id': ...}, ...]
		Marketo Docs for adding leads to list http://developers.marketo.com/documentation/rest/add-leads-to-list/
		"""
		resp = self.post_with_handler(
			'{0}{1}'.format(self.URL_ENDPOINT, '/rest/v1/lists/{0}/leads.json'.format(list_id)),
			data=json.dumps({'input': lead_ids})
		)

		return resp['result']

	##################################################################################
	# Convenience Functions. Not in api but used for common operations.              #
	##################################################################################

	def create_or_update_lead(self, lead, lookup_field='email', action='createOrUpdate', async_processing=False, partition_name=None):
		"""
		Creates or updates a single lead.
		"""
		results = self.create_or_update_leads([lead], lookup_field, action, async_processing, partition_name)

		if not results:
			raise MarketoInvalidInputException("uploaded lead's should not be empty.")

		return results[0]

	def add_lead_to_list(self, lead_id, list_id):
		"""
		Takes single lead id and adds it to the list.
		"""
		results = self.add_leads_to_list([{'id': lead_id}], list_id)

		if not results:
			raise MarketoInvalidInputException("uploaded lead's should not be empty.")

		return results[0]

	def f_create_or_update_leads(self, leads, lookup_field='email', action='createOrUpdate', async_processing=False, partition_name=None):
		"""
		Formats the leads into buckets for status. Attaches the lookup fielf to identify them.
		Ex. Response:
			{'created': [{'id': 50, 'email': 'joram@gmail.com'}], 'skipped': [], 'updated': []}
		"""
		response = {'created': [], 'skipped': [], 'updated': []}
		results = self.create_or_update_leads(leads, lookup_field, action, async_processing, partition_name)

		for idx, result in enumerate(results):
			status = result['status']
			result[lookup_field] = leads[idx][lookup_field]
			del result['status']
			response[status].append(result)

		return response

	def f_add_leads_to_list(self, identity_key, lead_ids, list_id):
		response = {'skipped': [], 'added': []}
		clean_lead_ids = []
		for lead_id in lead_ids:
			clean_lead_ids.append({'id': lead_id['id']})

		results = self.add_leads_to_list(clean_lead_ids, list_id)

		for idx, result in enumerate(results):
			status = result['status']
			result[identity_key] = lead_ids[idx][identity_key]
			del result['status']
			response[status].append(result)

		return response

	def display_rest_names(self, display_name=None):
		"""
		Displays fields on leads in a human readable format. Can filter on display name to get the field name.
		"""

		rest_names = []
		for lead in self.describe():
			if 'rest' in lead:
				rest_names.append((lead['displayName'], lead['rest']['name'], lead['dataType'], lead.get('length', 'N/A')))

		if display_name:
			rest_names = [lead for lead in rest_names if lead[0] == display_name]

		for name,  api_name, data_type, length in rest_names:
			print u"Display: {}, API: {}, Data Type: {} Length: {}".format(name,  api_name, data_type, length)
