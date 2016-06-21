from flask import Flask, Response
from authbone import Authenticator, AuthDataDecodingException, NotAuthenticatedException
from authbone.auth_data_getters import basic_auth_getter
from werkzeug.datastructures import Headers
import unittest
from base64 import b64encode


class MyAuthenticator(Authenticator):

    def authenticate(self, auth_data):
        if auth_data.username == 'admin' and auth_data.password == 'admin':
            return {'username': auth_data.username, 'password': auth_data.password}
        return None


authenticator = MyAuthenticator(basic_auth_getter)

app = Flask(__name__)
app.config['TESTING'] = True


def send_401(message):
    """Sends a 401 response that enables basic auth"""
    return Response(message, 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.errorhandler(AuthDataDecodingException)
def bad_auth_data_callback(ex):
    return send_401('Missing credentials')


@app.errorhandler(NotAuthenticatedException)
def not_authenticated_callback(ex):
    return send_401('User not recognized')


@app.route('/')
@authenticator.requires_authentication
def auth():
    return authenticator.currIdentity['username']


class TestBasicAuth(unittest.TestCase):

    def setUp(self):
        self.tc = app.test_client()

    def tearDown(self):
        pass

    def make_basic_auth_header(self, username, password):
        basic_auth = b64encode('{}:{}'.format(username, password).replace('\n', '').encode())
        return Headers([('Authorization', 'Basic ' + basic_auth.decode('utf-8'))])

    def test_no_auth_data(self):
        '''no authentication data should raise exception'''
        r = self.tc.get('/')
        self.assertEqual(r.status_code, 401)
        self.assertTrue('WWW-Authenticate' in r.headers)
        self.assertTrue('Basic' in r.headers['WWW-Authenticate'])

    def test_authenticated(self):
        '''bad authentication credentials should raise exception'''
        r = self.tc.get('/', headers=self.make_basic_auth_header('admin', 'admin'))
        self.assertEqual(r.status_code, 200)


if __name__ == '__main__':
    app.run()
