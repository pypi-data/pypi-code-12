# -*- coding: utf-8 -*-

""" standard """
import ConfigParser
import json
import sys

""" custom """
from threatconnect import ThreatConnect
from threatconnect.Config.ResourceType import ResourceType
from threatconnect.RequestObject import RequestObject

# configuration file
config_file = "tc.conf"

# retrieve configuration file
config = ConfigParser.RawConfigParser()
config.read(config_file)

try:
    api_access_id = config.get('threatconnect', 'api_access_id')
    api_secret_key = config.get('threatconnect', 'api_secret_key')
    api_default_org = config.get('threatconnect', 'api_default_org')
    api_base_url = config.get('threatconnect', 'api_base_url')
    api_result_limit = int(config.get('threatconnect', 'api_result_limit'))
except ConfigParser.NoOptionError:
    print('Could not retrieve configuration file.')
    sys.exit(1)

tc = ThreatConnect(api_access_id, api_secret_key, api_default_org, api_base_url)
tc.set_api_result_limit(api_result_limit)
tc.report_enable()

#
# build DOCUMENT request object
#
ro = RequestObject()
ro.set_http_method('POST')
# body = {'count': 1,'dateObserved': '2015-12-20T14:26:45-06:00'}
body = {'count': 1,'dateObserved': '2016-03-30T09:14:10'}
ro.set_body(json.dumps(body))
ro.set_content_type('application/json')
ro.set_owner('SumX')
ro.set_owner_allowed(True)
ro.set_resource_pagination(False)
ro.set_request_uri('/v2/indicators/{0}/{1}/observations'.format('addresses', '10.121.82.247'))

# display request object parameters
print(ro)

#
# retrieve and display the results
#
results = tc.api_request(ro)
print('status_code', results.status_code)
