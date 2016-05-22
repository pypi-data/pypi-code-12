import json
from unittest import TestCase
import falcon
from penelope.middleware.auth import BearerTokenAuth
from penelope.middleware.json import JSONRequest, JSONResponse
from penelope.utils.auth import generate_token


class Stub:

    def __init__(self):
        self.context = {}


class GoodStream:

    def read(t):
        return json.dumps({'this': 'that'}).encode('utf-8')


class BadStream:

    def read(t):
        return 'not json'.encode('utf-8')


class JSONMiddlewareTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.req = Stub()
        self.res = Stub()
        self.resource = Stub()

    def test_valid_json_request(self):
        middleware = JSONRequest()
        self.req.content_type = 'application/json; charset=utf-8'
        self.req.stream = GoodStream()
        middleware.process_request(req=self.req, res=self.res)
        self.assertEqual(self.req.context['data'], {'this': 'that'})

    def test_invalid_json_request(self):
        middleware = JSONRequest()
        self.req.content_type = 'application/json; charset=utf-8'
        self.req.stream = BadStream()
        with self.assertRaises(falcon.HTTPBadRequest):
            middleware.process_request(req=self.req, res=self.res)

    def test_json_response(self):
        middleware = JSONResponse()
        self.req.context['json_resp'] = {
            'ping': 'pong'
        }
        middleware.process_response(req=self.req, res=self.res, resource=self.resource)
        self.assertEqual(self.res.content_type, 'application/json')
        self.assertEqual(self.req.context['json_resp'], json.loads(self.res.body))

        # No body
        self.req.context = {}
        middleware.process_response(req=self.req, res=self.res, resource=self.resource)
        self.assertEqual(self.res.content_type, 'application/json')
        self.assertEqual(self.res.body, None)


class AuthMiddlewareTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.req = Stub()
        self.res = Stub()
        self.resource = Stub()

    def test_good_auth_token(self):
        user = {
            'id': 1,
            'email': 'what@ever.com'
        }
        token = generate_token(user_dict=user, secret_key='secret', expiration=86400)
        self.req.auth = 'Bearer {0}'.format(token)
        middleware = BearerTokenAuth(token_secret='secret')
        middleware.process_request(req=self.req, res=self.res)
        self.assertEqual(self.req.context['auth_user'], user)

    def test_bad_auth_token(self):
        self.req.auth = 'Bearer {0}'.format('thisisnotavalidtoken')
        middleware = BearerTokenAuth(token_secret='secret')
        middleware.process_request(req=self.req, res=self.res)
        self.assertEqual(self.req.context['auth_user'], None)
        self.req.auth = 'missingbearer'
        middleware.process_request(req=self.req, res=self.res)
        self.assertEqual(self.req.context['auth_user'], None)
        self.req.auth = 'missing bearer'
        middleware.process_request(req=self.req, res=self.res)
        self.assertEqual(self.req.context['auth_user'], None)
