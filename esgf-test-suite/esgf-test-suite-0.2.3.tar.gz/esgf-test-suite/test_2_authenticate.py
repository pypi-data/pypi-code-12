import nose
from OpenSSL import crypto

import utils.authentication as auth



def setup_module():
	global	_mu

	_mu = auth.MyProxyUtils()
	_mu.get_trustroots()
	_mu.get_credentials()

def teardown_module():
	_mu.delete_credentials()
	_mu.delete_trustroots()


class TestMyProxy(object):
	def test_get_trustroots(self):
                # Test output from get_trustroots
                assert(isinstance(_mu.trustRoots, dict))
                for fileName, fileContents in _mu.trustRoots.items():
                        if fileName.endswith('.0'):
                                # test parsing certificate 
                                cert = crypto.load_certificate(crypto.FILETYPE_PEM,
                                                               fileContents)
                                assert(isinstance(cert, crypto.X509))
                                subj = cert.get_subject()
                                assert(subj)

	def test_get_credentials(self):
		# Test output from get_trustroots
		assert(isinstance(_mu.credentials, tuple))
		cert = crypto.load_certificate(crypto.FILETYPE_PEM,
					       _mu.credentials[0])
		key = crypto.load_privatekey(crypto.FILETYPE_PEM,
					     _mu.credentials[1])
		assert(isinstance(cert, crypto.X509))
		assert(isinstance(key, crypto.PKey))
