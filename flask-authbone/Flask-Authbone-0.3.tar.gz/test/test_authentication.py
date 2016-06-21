import unittest
from flask import Flask
from authbone import Authenticator, AuthDataDecodingException, NotAuthenticatedException
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

authenticator = Authenticator(form_data_getter, authenticate)

app = Flask(__name__)
app.config['TESTING'] = True


@app.route('/', methods=['POST'])
@authenticator.requires_authentication
def root():
    return authenticator.currIdentity['username']


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.tc = app.test_client()

    def tearDown(self):
        pass

    def test_no_auth_data(self):
        '''no authentication data should raise exception'''
        with self.assertRaises(AuthDataDecodingException):
            self.tc.post('/')

    def test_not_authenticated(self):
        '''bad authentication credentials should raise exception'''
        with self.assertRaises(NotAuthenticatedException):
            self.tc.post('/', data={'username': 'unknown',
                                    'password': 'wrong'})

    def test_authenticated(self):
        r = self.tc.post('/', data={'username': 'test',
                                    'password': 'test'})
        self.assertEqual(r.status_code, 200)

if __name__ == '__main__':
    unittest.main()
