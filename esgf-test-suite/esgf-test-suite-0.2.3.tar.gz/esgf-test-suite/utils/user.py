import requests
from splinter import Browser

import configuration as config

class UserUtils(object):
        def __init__(self):
                self.config = config.read_config()
		self.account = self.config['account']
                self.idp_server = self.config['nodes']['idp_node']
		
		# Abort test if esgf-web-fe is not reachable
		r = requests.get("https://{0}/user/add".format(self.idp_server), verify=False, timeout=1)
                assert r.status_code == 200

		self.browser = Browser('firefox')

		# Mapping user data to fit to web-fe user creation form 
                self.elements = {'first_name' : self.account['firstname'],
                                 'last_name'  : self.account['lastname'],
                                 'email'     : self.account['email'],
                                 'username'  : self.account['username'],
                                 'password' : self.account['password'],
                                 'confirm_password' : self.account['password'],
				 'institution' : self.account['institution'],
				 'city' : self.account['city'],
				 'country' : self.account['country']}


	def check_user_exists(self):
		URL = "https://{0}/login".format(self.idp_server)
		OpenID = "https://{0}/esgf-idp/openid/{1}".format(self.idp_server, self.account['username'])

		# Try to log in
		self.browser.visit(URL)
		self.browser.find_by_id('openid_identifier').fill(OpenID)
		self.browser.find_by_value('Login').click()

		# User does not exist if unable to resolve OpenID
		if(self.browser.is_text_present("OpenID Discovery Error: unrecognized by the Identity Provider.")):
			self.user_exists = False
		else:
			self.user_exists = True
		
        def create_user(self):
		URL = "https://{0}/user/add".format(self.idp_server)
        	self.browser.visit(URL)
	
		# Filling the form
		for element_name in self.elements:
			self.browser.find_by_name(element_name).fill(self.elements[element_name])

      		self.browser.find_by_value('Submit').click()

		# Parsing response
		self.response = []		
		if (self.browser.is_text_present("Thank you for creating an account. You can now login.") == True):
			self.response.append("SUCCESS")
		else:
			self.response.append("FAILURE")


        def exit_browser(self):
		self.browser.quit()


