import os
import shutil
import subprocess
from splinter import Browser
from operator import itemgetter
from nose.plugins.skip import Skip, SkipTest

import utils.authentication as auth
import utils.configuration as config
import utils.catalog as cat
import utils.user as usr



def setup_module():
	global _mu
	global _tu

	global endpoints

	_tu = cat.ThreddsUtils()
	endpoints = _tu.get_endpoints()

	_mu = auth.MyProxyUtils()
	_mu.get_trustroots()
	_mu.get_credentials()

def teardown_module():
	_mu.delete_credentials()
	_mu.delete_trustroots()


class TestDownload(object):
	@classmethod
	def setup_class(self):
		self.config = config.read_config()
		self.data_node = self.config['nodes']['data_node']
		self.idp_node = self.config['nodes']['idp_node']
		self.username = self.config['account']['username']
		self.password = self.config['account']['password']

	def get_endpoint_path(self, service):
                if not endpoints:
                        raise SkipTest("No available endpoints at {1}".format(service, self.data_node))
                else:
                        service_endpoints = [i for i in endpoints if service in i[2]] #Sort by service
                        if not service_endpoints:
                                raise SkipTest("No available {0} endpoints at {1}".format(service, self.data_node))
                        else:
                                path = min(service_endpoints,key=itemgetter(1))[0] #Pick smallest dataset 
                                return path

	def test_0_http_browser_download(self):
		path = self.get_endpoint_path('HTTPServer')
		url = "http://{0}/thredds/fileServer/{1}".format(self.data_node, path)
	
		OpenID = "https://{0}/esgf-idp/openid/{1}".format(self.idp_node, self.username)

	        pf={'browser.helperApps.neverAsk.saveToDisk':'application/x-netcdf, application/netcdf'}

		browser = Browser('firefox', profile_preferences=pf)
		browser.visit(url)

		if browser.status_code.is_success() is True:
			browser.quit()
			return

		browser.find_by_css('input.custom-combobox-input').fill(OpenID)
 		browser.find_by_value('GO').click()

		browser.find_by_id('password').fill(self.password)
		browser.find_by_value('SUBMIT').click()
		
		# To Do only if user is not enrolled in a group
		if browser.is_text_present('Group Registration Request'):
			# Chosing First Registration Group
			browser.find_by_id('button_1').click()
		
			# Accepting License Agreement
			browser.execute_script('myForm.submit();')

			# Clicking on 'Download data button'
			browser.find_by_id('goButton').click()

		browser.quit()

	def test_1_globus_url_copy(self):
		path = self.get_endpoint_path('GridFTP')
		url = "gsiftp://{0}:2811//{1}".format(self.data_node, path)
		os.environ['X509_USER_PROXY'] = os.path.expanduser("~/.esg/credentials.pem")
		os.environ['X509_CERT_DIR'] = os.path.expanduser("~/.esg/certificates")
		command = ['globus-url-copy', '-b', url, '/tmp/dest_file.nc']
		process = subprocess.Popen(command)
		process.wait()
		assert process.returncode == 0

	@classmethod
	def teardown_class(self):
                # Delete downloaded file
                if os.path.exists("/tmp/dest_file.nc"):
                        os.remove("/tmp/dest_file.nc")	
