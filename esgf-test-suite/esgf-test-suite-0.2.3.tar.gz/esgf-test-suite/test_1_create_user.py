import nose
from nose.plugins.skip import Skip, SkipTest

import utils.user as usr



def setup_module():
	global	_usr

	_usr = usr.UserUtils()
	_usr.check_user_exists()

def teardown_module():
	_usr.exit_browser()

class TestCreateUser(object):
	def test_create_user(self):
		if(_usr.user_exists):
                	raise SkipTest("User already exists")
		# Create user
		_usr.create_user()
		# Test output from create_user and eventually print error message
                assert(isinstance(_usr.response, list))
		assert(_usr.response[0] == "SUCCESS"), _usr.response
