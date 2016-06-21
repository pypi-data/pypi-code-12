import unittest
from flask import Flask
from authbone import Authorizator, Authenticator, CapabilityMissingException
from authbone.auth_data_getters import form_data_getter


users = {'admin': 'admin',
         'test': 'test'}


def authenticate(auth_data):
    try:
        if auth_data['password'] == users[auth_data['username']]:
            return auth_data
    except KeyError:
        return None
    return None


def check_capability(identity, capability):
    return identity['username'] == 'admin'


authenticator = Authenticator(form_data_getter, authenticate)
authorizator = Authorizator(check_capability, authenticator)

app = Flask(__name__)
app.config['TESTING'] = True


@app.route('/', methods=['POST'])
@authorizator.requires_capability(None)
def root():
    return 'ok'


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.tc = app.test_client()

    def tearDown(self):
        pass

    def test_authorized(self):
        rs = self.tc.post('/', data={'username': 'admin',
                                     'password': 'admin'})
        assert(rs.status_code == 200)

    def test_capability_missing(self):
        with self.assertRaises(CapabilityMissingException):
            self.tc.post('/', data={'username': 'test',
                                    'password': 'test'})

if __name__ == '__main__':
    unittest.main()
