import os
import shutil

from myproxy.client import MyProxyClient
from OpenSSL import crypto

import configuration as config



class MyProxyUtils(object):
	def __init__(self):
		self.config = config.read_config()
		self.cacertdir = os.path.expanduser("~/.esg/certificates")
		self.credsfile = os.path.expanduser("~/.esg/credentials.pem")
		self.myproxy = MyProxyClient(hostname=self.config['nodes']['idp_node'])
		self.myproxy._setCACertDir(self.cacertdir)


	def get_trustroots(self):
		# Get trust roots
		self.trustRoots = self.myproxy.getTrustRoots(self.config['account']['username'],
							     	     self.config['account']['password'],
	         					     	     writeToCACertDir=True,
	  				       	             	     bootstrap=True)

	def get_credentials(self):
		# Get credentials (and trustroots)
                self.credentials = self.myproxy.logon(self.config['account']['username'],
                                                      	      self.config['account']['password'])
		# Write Credentials
		with open(self.credsfile, 'w') as f:
			f.write(self.credentials[0]+self.credentials[1])
            	os.chmod(self.credsfile, self.myproxy.PROXY_FILE_PERMISSIONS)
	

	def delete_credentials(self):
		# Delete credentials file
		if os.path.exists(self.credsfile):
			os.remove(self.credsfile)


	def delete_trustroots(self):
		# Delete trustroots and cacert directory
		if os.path.exists(self.cacertdir):
                        shutil.rmtree(self.cacertdir)
