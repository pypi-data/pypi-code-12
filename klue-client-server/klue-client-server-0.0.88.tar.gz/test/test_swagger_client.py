import imp
import os
import pprint
import responses
from httplib import HTTPResponse
from mock import patch, MagicMock
from klue.swagger.client import _format_flask_url
from klue.exceptions import KlueException, ValidationError


utils = imp.load_source('common', os.path.join(os.path.dirname(__file__), 'utils.py'))


class Test(utils.KlueTest):


    def setUp(self):
        super(Test, self).setUp()


    @responses.activate
    def test_client_with_query_param(self):
        handler, _ = self.generate_client_and_spec(self.yaml_query_param)

        responses.add(responses.GET, "http://some.server.com:80/v1/some/path",
                      body='{"foo": "a", "bar": "b"}', status=200,
                      content_type="application/json")

        res = handler(arg1='this', arg2='that').call()

        print("response: " + pprint.pformat(res))
        self.assertEqual(type(res).__name__, 'Result')
        self.assertEqual(res.foo, 'a')
        self.assertEqual(res.bar, 'b')


    @patch('klue.swagger.client.grequests')
    def test_requests_parameters_with_query_param(self, grequests):
        grequests.get = MagicMock()
        handler, _ = self.generate_client_and_spec(self.yaml_query_param)

        with self.assertRaises(AssertionError) as e:
            handler(arg1='this', arg2='that').call()
        self.assertEqual("Expected 1 caller, got 0", str(e.exception))

        grequests.get.assert_called_once_with('http://some.server.com:80/v1/some/path',
                                              data=None,
                                              headers={'Content-Type': 'application/json'},
                                              params={'arg1': 'this', 'arg2': 'that'},
                                              timeout=(10, 10))



    @responses.activate
    def test_client_with_body_param(self):
        handler, spec = self.generate_client_and_spec(self.yaml_body_param)

        responses.add(responses.POST, "http://some.server.com:80/v1/some/path",
                      body='{"foo": "a", "bar": "b"}', status=200,
                      content_type="application/json")

        # Only 1 parameter expected
        with self.assertRaises(ValidationError) as e:
            res = handler()
        with self.assertRaises(ValidationError) as e:
            res = handler(1, 2)

        # Send a valid parameter object
        model_class = spec.definitions['Param']
        param = model_class(arg1='a', arg2='b')

        res = handler(param).call()
        self.assertEqual(type(res).__name__, 'Result')
        self.assertEqual(res.foo, 'a')
        self.assertEqual(res.bar, 'b')


    @patch('klue.swagger.client.grequests')
    def test_requests_parameters_with_body_param(self, grequests):
        handler, spec = self.generate_client_and_spec(self.yaml_body_param)
        model_class = spec.definitions['Param']
        param = model_class(arg1='a', arg2='b')

        with self.assertRaises(AssertionError) as e:
            handler(param).call()
        self.assertEqual("Expected 1 caller, got 0", str(e.exception))

        grequests.post.assert_called_once_with('http://some.server.com:80/v1/some/path',
                                               data='{"arg1": "a", "arg2": "b"}',
                                               headers={'Content-Type': 'application/json'},
                                               params=None,
                                               timeout=(10, 10))


# def test_client_with_auth_required():
#     pass


    def test__format_flask_url(self):
        ref = {
            'item_id': '1234',
            'path': 'abcd',
        }

        data = ref.copy()
        u = _format_flask_url(
            "/v1/seller/<item_id>/<path>/foo",
            data
        )
        self.assertEqual(u, "/v1/seller/1234/abcd/foo", u)
        self.assertEqual(len(data.keys()), 0)

        data = ref.copy()
        u = _format_flask_url(
            "/v1/seller/<item_id>/<path>/foo/<item_id>",
            data,
        )
        self.assertEqual(u, "/v1/seller/1234/abcd/foo/1234", u)
        self.assertEqual(len(data.keys()), 0)

        data = ref.copy()
        u = _format_flask_url(
            "/v1/seller/<item_id>/foo",
            data,
        )
        self.assertEqual(u, "/v1/seller/1234/foo", u)
        self.assertEqual(len(data.keys()), 1)
        self.assertEqual(data['path'], 'abcd')



    @responses.activate
    def test_client_with_path_param(self):
        handler, spec = self.generate_client_and_spec(self.yaml_path_param)

        responses.add(responses.GET,
                      "http://some.server.com:80/v1/some/123/path/456",
                      body='{"foo": "a", "bar": "b"}',
                      status=200,
                      content_type="application/json")

        # Make a valid call
        res = handler(foo=123, bar=456).call()
        self.assertEqual(type(res).__name__, 'Result')
        self.assertEqual(res.foo, 'a')
        self.assertEqual(res.bar, 'b')


    @patch('klue.swagger.client.grequests')
    def test_requests_parameters_with_path_params(self, grequests):
        handler, spec = self.generate_client_and_spec(self.yaml_path_param)

        with self.assertRaises(AssertionError) as e:
            handler(foo=123, bar=456).call()

        grequests.get.assert_called_once_with(
            'http://some.server.com:80/v1/some/123/path/456',
            data=None,
            headers={'Content-Type': 'application/json'},
            params=None,
            timeout=(10, 10))


    @patch('klue.swagger.client.grequests')
    def test_handler_extra_parameters(self, grequests):
        handler, spec = self.generate_client_and_spec(self.yaml_path_param)

        with self.assertRaises(AssertionError) as e:
            handler(
                foo=123,
                bar=456,
                max_attempts=2,
                read_timeout=6,
                connect_timeout=8
            ).call()

        grequests.get.assert_called_once_with(
            'http://some.server.com:80/v1/some/123/path/456',
            data=None,
            headers={'Content-Type': 'application/json'},
            params=None,
            timeout=(8, 6))


    @responses.activate
    def test_client_with_path_query_param(self):
        handler, spec = self.generate_client_and_spec(self.yaml_path_query_param)

        responses.add(responses.GET,
                      "http://some.server.com:80/v1/some/123/path",
                      body='{"foo": "a", "bar": "b"}',
                      status=200,
                      content_type="application/json")

        # Make a valid call
        res = handler(foo=123, bar=456).call()
        self.assertEqual(type(res).__name__, 'Result')
        self.assertEqual(res.foo, 'a')
        self.assertEqual(res.bar, 'b')


    @patch('klue.swagger.client.grequests')
    def test_requests_parameters_with_path_query_params(self, grequests):
        handler, spec = self.generate_client_and_spec(self.yaml_path_query_param)

        with self.assertRaises(AssertionError) as e:
            handler(foo=123, bar=456).call()

        grequests.get.assert_called_once_with(
            'http://some.server.com:80/v1/some/123/path',
            data=None,
            headers={'Content-Type': 'application/json'},
            params={'bar': 456},
            timeout=(10, 10))



    @responses.activate
    def test_client_with_path_body_param(self):
        handler, spec = self.generate_client_and_spec(self.yaml_path_body_param)

        responses.add(responses.GET,
                      "http://some.server.com:80/v1/some/123/path",
                      body='{"foo": "a", "bar": "b"}',
                      status=200,
                      content_type="application/json")

        # Send a valid parameter object
        model_class = spec.definitions['Param']
        param = model_class(arg1='a', arg2='b')

        res = handler(param, foo=123).call()
        self.assertEqual(type(res).__name__, 'Result')
        self.assertEqual(res.foo, 'a')
        self.assertEqual(res.bar, 'b')

        # Only 1 parameter expected
        with self.assertRaises(ValidationError) as e:
            res = handler(foo=123)
        self.assertTrue('expects exactly' in str(e.exception))

        with self.assertRaises(ValidationError) as e:
            res = handler(1, 2, foo=123)
        self.assertTrue('expects exactly' in str(e.exception))

        with self.assertRaises(ValidationError) as e:
            res = handler(param)
        self.assertTrue('Missing some arguments' in str(e.exception))


    @patch('klue.swagger.client.grequests')
    def test_requests_parameters_with_path_body_params(self, grequests):
        handler, spec = self.generate_client_and_spec(self.yaml_path_body_param)

        model_class = spec.definitions['Param']
        param = model_class(arg1='a', arg2='b')

        with self.assertRaises(AssertionError) as e:
            handler(param, foo=123).call()

        grequests.get.assert_called_once_with(
            'http://some.server.com:80/v1/some/123/path',
            data='{"arg1": "a", "arg2": "b"}',
            headers={'Content-Type': 'application/json'},
            params=None,
            timeout=(10, 10))


    @responses.activate
    def test_client_unknown_method(self):
        y = self.yaml_query_param
        y = y.replace('get:', 'foobar:')

        with self.assertRaises(KlueException) as e:
            handler, spec = self.generate_client_and_spec(y)
        self.assertTrue('BUG: method FOOBAR for /v1/some/path is not supported' in str(e.exception))


    @patch('klue.swagger.client.grequests')
    def test_requests_client_override_read_timeout(self, grequests):
        handler, spec = self.generate_client_and_spec(self.yaml_path_query_param)

        with self.assertRaises(AssertionError) as e:
            handler(read_timeout=50, foo='123', bar='456').call()

        grequests.get.assert_called_once_with(
            'http://some.server.com:80/v1/some/123/path',
            data=None,
            headers={'Content-Type': 'application/json'},
            params={'bar': '456'},
            timeout=(10, 50))


    @patch('klue.swagger.client.grequests')
    def test_requests_client_override_connect_timeout(self, grequests):
        handler, spec = self.generate_client_and_spec(self.yaml_path_query_param)

        with self.assertRaises(AssertionError) as e:
            handler(connect_timeout=50, foo='123', bar='456').call()

        grequests.get.assert_called_once_with(
            'http://some.server.com:80/v1/some/123/path',
            data=None,
            headers={'Content-Type': 'application/json'},
            params={'bar': '456'},
            timeout=(50, 10))


    @responses.activate
    def test_client_error_callback_return_dict(self):

        def callback(e):
            return {'error': str(e)}

        handler, spec = self.generate_client_and_spec(
            self.yaml_path_body_param,
            callback=callback,
        )

        responses.add(responses.GET,
                      "http://some.server.com:80/v1/some/123/path",
                      body='{"foo": "a", "bar": "b"}',
                      status=200,
                      content_type="application/json")

        # Send a valid parameter object
        model_class = spec.definitions['Param']
        param = model_class(arg1='a', arg2='b')

        res = handler(param).call()
        self.assertDictEqual(
            res,
            {
                'error': 'Missing some arguments to format url: http://some.server.com:80/v1/some/<foo>/path'
            }
        )


# TODO: test max_attempts?
