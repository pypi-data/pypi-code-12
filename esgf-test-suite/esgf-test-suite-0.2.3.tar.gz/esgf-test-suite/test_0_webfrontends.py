import requests

import utils.configuration as config



_services = {'idp_node'		: ['esgf-idp'],
	     'index_node'	: [''],
	     'compute_node'	: ['las'],
	     'data_node'	: ['esg-orp',
                         	   #'esgf-desktop',
                         	   'thredds']}

def setup_module():
	global _conf
	_conf = config.read_config()
	requests.packages.urllib3.disable_warnings()

def teardown_module():
	pass


class TestWebFrontEnds(object):
	def check_frontend_availability(self, URL):
		r = requests.get(URL, verify=False, timeout=5)
		assert r.status_code == 200

	def test_frontends_availability(self):
		for node_type in _services:
			node_name = _conf['nodes'][node_type]
			for service in _services[node_type]:
				URL = "https://" + node_name + "/" + service
				yield self.check_frontend_availability, URL
