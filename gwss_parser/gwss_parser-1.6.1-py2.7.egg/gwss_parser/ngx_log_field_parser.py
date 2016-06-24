"""
This file contains parsing method to be applied
on respective variables extracted variables in a request
line log

***IMPORTANT***
There are 2 special variables used by GWSS, domain & server_ip,
these variables should not be added as it can break the whole
system
***************

In general, this file is used to:
- Shorten/trim variables (such as request)
- To skip certain requests (http status code)

NOTE: 
- If a variable is not found in here, it will be
left as it is by default (no change)
- Variable is lower-case
- Some log files do NOT log some of these variables
- Since this is python, please declare function before calling

Below are common variables (See nginx access log for detail),
those with asterisk are more important
- remote_addr
- remote_user
- time_local*
- request*
- status*
- body_bytes_sent
- http_referer
- http_user_agent
- http_x_forwarded_for

Format: 'variable_name' : 'function'
- There should be ONE string parameter which is value of variable
- Should return ONE parsed output or None

TODO: Add example, test parser
"""

import datetime
import time

def parse_time(str):
	"""
	Make sure the script runs on the same machine as access log
	as it doesn't not track timezone

	Convert the time in nginx time_local format to unix timestampt
	"""
	dt = datetime.datetime.strptime(str.split()[0],'%d/%b/%Y:%H:%M:%S')
	return int(time.mktime(dt.timetuple()))

def parse_time_iso8601(str):
	"""
	Make sure the script runs on the same machine as access log
	as it doesn't not track timezone

	Convert the time in nginx time_iso8601 format to unix timestampt
	"""
	dt = datetime.datetime.strptime(str.split('+')[0], '%Y-%m-%dT%H:%M:%S')
	return int(time.mktime(dt.timetuple()))

def parse_status(str):
	"""
	Ignore irrelevant request status
	Default: Only parse request with 200 http code

	Can be changed to set/dict for improved efficiency
	"""

	HTTP_RESPONSE_CODE_WHITELIST = ['200']

	if str in HTTP_RESPONSE_CODE_WHITELIST:
		return str

	return None

def parse_request(str):
	"""

	Example input: 
		"GET /query?data=xxxx" -> "/query"
		"GET /point/" -> "/point"
	"""

	try:
		res = str.split()[1].split('?')[0]
		# if the last character is slash, REMOVE it
		if res[-1] == '/':
			res = res[:-1]

		return res
	except IndexError:
		return None


PARSER_LIST = {
	'time_local': parse_time,
	'request': parse_request,
	'status': parse_status,
	'time_iso8601': parse_time_iso8601,
}
