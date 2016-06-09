import mock
import os
import unittest
import six
import responses
import tempfile
import json
import datarobot.client as client_sdk
from datarobot.rest import RESTClientObject
from datarobot.client import set_client, get_client, Client
from datarobot.errors import AppPlatformError
from .utils import SDKTestcase
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


class ClientTest(unittest.TestCase):

    def setUp(self):
        set_client(None)

    def tearDown(self):
        set_client(None)

    @responses.activate
    def test_instantiation(self):
        """
        Basic client installation.
        """
        raw = """{"api_token": "some_token"}"""
        with mock.patch(
            'os.environ',
                {'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            responses.add(responses.POST,
                          'https://host_name.com/api_token/',
                          body=raw,
                          status=201,
                          content_type='application/json')

            client = Client(username='u-user', password='p-password')

            restored_client = get_client()
            self.assertIs(client, restored_client)

    def test_instantiation_without_env(self):
        """
        Basic client installation by get_client without configuration.
        """
        with mock.patch(
            'os.environ',
                {'DATAROBOT_ENDPOINT': 'https://host_name.com',
                 'DATAROBOT_USERNAME': '',
                 'DATAROBOT_PASSWORD': ''}):
            with self.assertRaises(ValueError):
                get_client()

    def test_username_without_password_fails(self):
        with mock.patch(
            'os.environ',
                {'DATAROBOT_ENDPOINT': 'https://host_name.com',
                 'DATAROBOT_USERNAME': '',
                 'DATAROBOT_PASSWORD': ''}):
            with self.assertRaises(ValueError):
                Client(username='username')

    def test_password_without_username_fails(self):
        with mock.patch(
            'os.environ',
                {'DATAROBOT_ENDPOINT': 'https://host_name.com',
                 'DATAROBOT_USERNAME': '',
                 'DATAROBOT_PASSWORD': ''}):
            with self.assertRaises(ValueError):
                Client(password='password')

    def test_no_auth_fails(self):
        with mock.patch(
            'os.environ',
                {'DATAROBOT_ENDPOINT': 'https://host_name.com',
                 'DATAROBOT_USERNAME': '',
                 'DATAROBOT_PASSWORD': ''}):
            with self.assertRaises(ValueError):
                Client()

    def test_token_alone_is_okay(self):
        Client(token='token')

    @responses.activate
    def test_re_instantiation(self):
        """
        Client re installation.
        """
        raw = """{"api_token": "some_token"}"""
        responses.add(responses.POST,
                      'https://host_name.com/api_token/',
                      body=raw,
                      status=201,
                      content_type='application/json')
        with mock.patch('os.environ',
                        {'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            previous = Client('u-**********', 'p-******')
            old_client = set_client(
                RESTClientObject(auth=('u-**********', 'p-******'),
                                 endpoint='https://host_name.com'))
            self.assertIs(previous, old_client)

    @responses.activate
    def test_recognizing_domain_on_instance(self):
        raw = """{"api_token": "some_token"}"""
        responses.add(responses.POST,
                      'https://host_name.com/api/v2/api_token/',
                      body=raw,
                      status=201,
                      content_type='application/json')
        set_client(RESTClientObject(auth=('u-**********', 'p-******'),
                                    endpoint='https://host_name.com/api/v2'))

        restored_client = get_client()
        self.assertEqual(restored_client.domain, 'https://host_name.com')

    @responses.activate
    def test_instantiation_from_env(self):
        """
        Test instantiation with creds from virtual environment
        """
        with patch.dict(
            'os.environ',
            {'DATAROBOT_USERNAME': 'venv_username',
             'DATAROBOT_PASSWORD': 'venv_password',
             'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            raw = """{"api_token": "some_token"}"""
            responses.add(responses.POST,
                          'https://host_name.com/api_token/',
                          body=raw,
                          status=201,
                          content_type='application/json')
            rest_client = get_client()
            self.assertEqual(rest_client.auth, ('venv_username',
                                                'venv_password'))

        set_client(None)

        with patch.dict(
            'os.environ',
            {'DATAROBOT_API_TOKEN': 'venv_token',
             'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            rest_client = get_client()
            self.assertEqual(rest_client.auth, 'venv_token')

    @responses.activate
    def test_instantiation_from_file_with_env_path(self):
        raw_data = """[datarobot]
username=file_username
password=file_password"""
        with tempfile.NamedTemporaryFile() as test_file:
            test_file.write(str(raw_data).encode('utf-8'))
            test_file.seek(0)
            with patch('datarobot.client.os.environ',
                       {'DATAROBOT_CONFIG_FILE': test_file.name,
                        'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
                raw = """{"api_token": "some_token"}"""
                responses.add(responses.POST,
                              'https://host_name.com/api_token/',
                              body=raw,
                              status=201,
                              content_type='application/json')
                rest_client = get_client()
        self.assertEqual(rest_client.auth, ('file_username',
                                            'file_password'))

    def test_instantiation_from_file_with_wrong_path(self):
        with patch.dict('os.environ', {'DATAROBOT_CONFIG_FILE': './tests/fixtures/.datarobotrc'}):
            with self.assertRaises(ValueError):
                get_client()

    def test_instantiation_from_file_api_token(self):
        file_data = ('[datarobot]\n'
                     'token=fake_token\n'
                     'endpoint=https://host_name.com')
        config_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            with open(config_file.name, mode='w') as config:
                config.write(file_data)
            fake_environ = {'DATAROBOT_CONFIG_FILE': config_file.name}
            with patch('os.environ', fake_environ):
                rest_client = get_client()
            self.assertEqual(rest_client.auth, 'fake_token')
            self.assertEqual(rest_client.endpoint, 'https://host_name.com')
        finally:
            os.remove(config_file.name)

    @patch('datarobot.client.get_config_file')
    @patch('datarobot.utils.get_config_file')
    @responses.activate
    def test_instantiation_from_file_default_path(self, mock_get_config_file, other_mock_get_file):
        CONFIG_FILE = '.datarobotrc'
        mock_get_config_file.return_value = CONFIG_FILE
        other_mock_get_file.return_value = CONFIG_FILE
        raw_data = """[datarobot]
username=file_username
password=file_password
endpoint=https://host_name.com"""
        with mock.patch('os.environ', {}):
                if os.path.isfile(CONFIG_FILE):
                    # move existing config file out of test's way
                    os.rename(CONFIG_FILE, CONFIG_FILE + '.user')
                try:
                    with open(CONFIG_FILE, 'w+') as test_file:
                        test_file.write(raw_data)
                    self.assertTrue(test_file.closed)

                    raw = """{"api_token": "some_token"}"""
                    responses.add(responses.POST,
                                  'https://host_name.com/api_token/',
                                  body=raw,
                                  status=201,
                                  content_type='application/json')

                    rest_client = get_client()
                    self.assertEqual(rest_client.auth, ('file_username',
                                                        'file_password'))
                    self.assertEqual(rest_client.endpoint,
                                     'https://host_name.com')
                finally:
                    try:
                        os.remove(CONFIG_FILE)
                    except OSError:
                        pass
                    # may be bring user's config back
                    if os.path.isfile(CONFIG_FILE + ".user"):
                        os.rename(CONFIG_FILE + '.user', CONFIG_FILE)

    def test_client_with_unicode_token(self):
        Client(token=u'ThisIsUnicode', endpoint='https://endpoint.com')
        c = get_client()
        assert c.token == u'ThisIsUnicode'

    @responses.activate
    def test_client_from_codeline(self):
        responses.add(responses.POST,
                      'https://endpoint.com/api_token/',
                      body=json.dumps({'apiToken': 'some_token'}))
        Client(username='username',
               password='password',
               endpoint='https://endpoint.com')
        c = get_client()
        self.assertEqual(c.auth[0], 'username')
        self.assertEqual(c.auth[1], 'password')
        self.assertEqual(c.token, 'some_token')
        self.assertEqual(c.endpoint, 'https://endpoint.com')

    @responses.activate
    def test_build_request_context(self):
        responses.add(responses.POST,
                      'https://endpoint.com/api_token/',
                      body=json.dumps({'api_token': 'some_token'}))
        responses.add(responses.POST,
                      'https://endpoint.com/test',
                      body='')
        c = Client(username='username',
                   password='password',
                   endpoint='https://endpoint.com')
        context = c.build_request_context('post',
                                          'test')
        response = context.send_request()
        self.assertEqual(response.status_code, 200)


class TestGetCredentials(unittest.TestCase):

    def setUp(self):
        os_patch = patch('datarobot.client.os')
        self.os_mock = os_patch.start()
        self.addCleanup(os_patch.stop)

        file_exists_patch = patch('datarobot.utils.file_exists')
        self.exists_mock = file_exists_patch.start()
        self.addCleanup(file_exists_patch.stop)

        self.uname = 'user@domain.com'
        self.passwd = 'secrets'
        self.token = 'api-token'

    def test_token_ignored_when_uname_provided(self):
        self.os_mock.environ = dict(DATAROBOT_USERNAME=self.uname,
                                    DATAROBOT_PASSWORD=self.passwd,
                                    DATAROBOT_API_TOKEN=self.token)

        uname, passwd, token = client_sdk.get_credentials_from_out()
        self.assertEqual(uname, self.uname)
        self.assertEqual(passwd, self.passwd)
        self.assertIsNone(token)

    def test_password_missing_from_env_results_in_none(self):
        self.os_mock.environ = dict(DATAROBOT_USERNAME=self.uname)
        uname, passwd, token = client_sdk.get_credentials_from_out()
        self.assertEqual(uname, self.uname)
        self.assertIsNone(passwd)
        self.assertIsNone(token)

    def test_api_token_in_env_leaves_uname_passwd_blank(self):
        self.os_mock.environ = dict(DATAROBOT_API_TOKEN=self.token)
        uname, passwd, token = client_sdk.get_credentials_from_out()
        self.assertIsNone(uname)
        self.assertIsNone(passwd)
        self.assertEqual(token, self.token)


class RestErrors(SDKTestcase):

    @responses.activate
    def test_404_plain_text(self):
        """
        Bad request in plain text
        """
        raw = "Not Found"

        responses.add(responses.GET, 'https://host_name.com/projects/404',
                      body=raw, status=404, content_type='text/plain')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.build_request('get', 'projects/404')

        self.assertEqual(str(app_error.exception),
                         '404 client error: Not Found')

    @responses.activate
    def test_404_json(self):
        """
        Bad request with datarobot reason in json
        """
        raw = """
        {"Error": "Not Found"}
        """

        responses.add(responses.GET, 'https://host_name.com/projects/404',
                      body=raw, status=404, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.build_request('get', 'projects/404')

        self.assertEqual(str(app_error.exception),
                         '404 client error: Not Found')

    @responses.activate
    def test_500_json(self):
        """
        Bad request with datarobot reason in json
        """
        raw = """
        {"Error": "Not Found"}
        """

        responses.add(responses.GET, 'https://host_name.com/projects/500',
                      body=raw, status=500, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.build_request('get', 'projects/500')

        self.assertEqual(str(app_error.exception),
                         '500 server error: Not Found')

    @responses.activate
    def test_other_errors(self):
        """
        Other errors
        """
        raw = """
        {"Error": "Bad response"}
        """

        responses.add(responses.GET,
                      'https://host_name.com/projects/not-500',
                      body=raw, status=500, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.build_request('get', 'projects/500')
            self.assertEqual(str(app_error.exception),
                             'Connection refused: '
                             'https://host_name.com/projects/500')


class TestClientAttributes(unittest.TestCase):

    def test_main_useful_things_under_datarobot(self):
        """To lower the intimidation factor, let's try to limit the objects
        that show up at the root of datarobot

        This way, when they are in IPython and do tab-completion they get a
        sense for what is available to tinker with at the top level
        """
        known_names = {'Project',
                       'Model',
                       'Blueprint',
                       'ModelJob',
                       'PredictJob',
                       'QUEUE_STATUS',
                       'Client',
                       'AUTOPILOT_MODE',
                       'AppPlatformError',
                       'utils',
                       'errors',
                       'models',
                       'client',
                       'rest',
                       'SCORING_TYPE',
                       'Featurelist',
                       'helpers',
                       'RandomCV',
                       'StratifiedCV',
                       'GroupCV',
                       'UserCV',
                       'RandomTVH',
                       'UserTVH',
                       'DateTVH',
                       'StratifiedTVH',
                       'GroupTVH',
                       'partitioning_methods',
                       'RecommenderSettings',  # TODO: Too many attrs
                       'AdvancedOptions',
                       }

        import datarobot
        found_names = [name for name in dir(datarobot)
                       if not (name.startswith('__') and name.endswith('__'))]
        self.assertEqual(set(found_names), known_names)
