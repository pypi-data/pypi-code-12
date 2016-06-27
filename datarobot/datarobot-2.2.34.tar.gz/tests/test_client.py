import mock
import os
import six
import responses
import tempfile
from tempfile import NamedTemporaryFile
import unittest

import datarobot as dr
from datarobot.rest import RESTClientObject
from datarobot.client import (set_client, get_client, Client, _get_credentials_from_file,
                              _get_endpoint_from_file, _get_config_file)
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

    def test_instantiation(self):
        """
        Basic client installation.
        """
        with mock.patch(
            'os.environ',
                {'DATAROBOT_ENDPOINT': 'https://host_name.com'}):

            client = Client(token='t-token')
        assert get_client() is client
        for model in ('Featurelist', 'Model', 'ModelJob', 'Project', 'PredictJob'):
            model = getattr(dr, model)
            assert model._client is model({})._client is client

    @mock.patch('datarobot.client._file_exists', return_value=False)
    def test_instantiation_without_env(self, mock_file_args):
        """
        Basic client installation by get_client without configuration.
        """
        with mock.patch(
            'os.environ',
                {'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
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

    @mock.patch('datarobot.client._file_exists')
    def test_no_endpoint_fails(self, mock_file_exists):
        mock_file_exists.return_value = False
        with mock.patch('os.environ', {}):
            with self.assertRaises(ValueError):
                Client(token='NOTATOKEN')

    def test_token_and_endpoint_is_okay(self):
        Client(token='token', endpoint='https://need_an_endpoint.com')

    def test_re_instantiation(self):
        """
        Client re installation.
        """
        with mock.patch('os.environ',
                        {'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            previous = Client(token='t-****')
            old_client = set_client(RESTClientObject(auth=('u-**********', 'p-******'),
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

    @mock.patch('datarobot.client._file_exists', return_value=False)
    def test_instantiation_from_env(self, mock_file_exists):
        """
        Test instantiation with creds from virtual environment
        """
        with patch.dict(
            'os.environ',
            {'DATAROBOT_API_TOKEN': 'venv_token',
             'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            rest_client = get_client()
            self.assertEqual(rest_client.token, 'venv_token')
            self.assertEqual(rest_client.endpoint, 'https://host_name.com')

        set_client(None)

        with patch.dict(
            'os.environ',
            {'DATAROBOT_API_TOKEN': 'venv_token',
             'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            rest_client = get_client()
            self.assertEqual(rest_client.token, 'venv_token')

    def test_instantiation_from_ini_file_with_env_path(self):
        raw_data = ("[datarobot]\n"
                    "token=file_token")
        with tempfile.NamedTemporaryFile() as test_file:
            test_file.write(str(raw_data).encode('utf-8'))
            test_file.seek(0)
            with patch('datarobot.client.os.environ',
                       {'DATAROBOT_CONFIG_FILE': test_file.name,
                        'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
                rest_client = get_client()
        self.assertEqual(rest_client.token, 'file_token')

    def test_instantiation_from_yaml_file_with_env_path(self):
        raw_data = "token: file_token\n"
        with tempfile.NamedTemporaryFile(suffix=".yaml") as test_file:
            test_file.write(str(raw_data).encode('utf-8'))
            test_file.seek(0)
            with patch('datarobot.client.os.environ',
                       {'DATAROBOT_CONFIG_FILE': test_file.name,
                        'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
                rest_client = get_client()
        self.assertEqual(rest_client.token, 'file_token')

    def test_instantiation_from_file_with_wrong_path(self):
        with patch.dict('os.environ', {'DATAROBOT_CONFIG_FILE': './tests/fixtures/.datarobotrc'}):
            with self.assertRaises(ValueError):
                get_client()

    def test_instantiation_from_ini_file_api_token(self):
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
            self.assertEqual(rest_client.token, 'fake_token')
            self.assertEqual(rest_client.endpoint, 'https://host_name.com')
        finally:
            os.remove(config_file.name)

    def test_instantiation_from_yaml_file_api_token(self):
        file_data = ('token: fake_token\n'
                     'endpoint: https://host_name.com')
        config_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        try:
            with open(config_file.name, mode='w') as config:
                config.write(file_data)
            fake_environ = {'DATAROBOT_CONFIG_FILE': config_file.name}
            with patch('os.environ', fake_environ):
                rest_client = get_client()
            self.assertEqual(rest_client.token, 'fake_token')
            self.assertEqual(rest_client.endpoint, 'https://host_name.com')
        finally:
            os.remove(config_file.name)

    @mock.patch('datarobot.client._get_config_file')
    def test_instantiation_from_ini_file_default_path(self, mock_get_config_file):
        CONFIG_FILE = '.datarobotrc'
        mock_get_config_file.return_value = CONFIG_FILE
        raw_data = ("[datarobot]\n"
                    "token=file_token\n"
                    "endpoint=https://host_name.com")
        with mock.patch('os.environ', {}):
                if os.path.isfile(CONFIG_FILE):
                    # move existing config file out of test's way
                    os.rename(CONFIG_FILE, CONFIG_FILE + '.user')
                try:
                    with open(CONFIG_FILE, 'w+') as test_file:
                        test_file.write(raw_data)
                    self.assertTrue(test_file.closed)

                    rest_client = get_client()
                    self.assertEqual(rest_client.token, 'file_token')
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

    def test_client_from_codeline(self):
        Client(token='some_token',
               endpoint='https://endpoint.com')
        c = get_client()
        self.assertEqual(c.token, 'some_token')
        self.assertEqual(c.endpoint, 'https://endpoint.com')


class TestGetCredentials(unittest.TestCase):

    def setUp(self):
        os_patch = patch('datarobot.client.os')
        self.os_mock = os_patch.start()
        self.addCleanup(os_patch.stop)

        file_exists_patch = patch('datarobot.client._file_exists')
        self.exists_mock = file_exists_patch.start()
        self.addCleanup(file_exists_patch.stop)

        self.uname = 'user@domain.com'
        self.passwd = 'secrets'
        self.token = 'api-token'

    def test_token_ignored_when_uname_provided(self):
        self.os_mock.environ = dict(DATAROBOT_USERNAME=self.uname,
                                    DATAROBOT_PASSWORD=self.passwd,
                                    DATAROBOT_API_TOKEN=self.token)

        uname, passwd, token = dr.client.get_credentials_from_out()
        self.assertEqual(uname, self.uname)
        self.assertEqual(passwd, self.passwd)
        self.assertIsNone(token)

    def test_password_missing_from_env_results_in_none(self):
        self.os_mock.environ = dict(DATAROBOT_USERNAME=self.uname)
        uname, passwd, token = dr.client.get_credentials_from_out()
        self.assertEqual(uname, self.uname)
        self.assertIsNone(passwd)
        self.assertIsNone(token)

    def test_api_token_in_env_leaves_uname_passwd_blank(self):
        self.os_mock.environ = dict(DATAROBOT_API_TOKEN=self.token)
        uname, passwd, token = dr.client.get_credentials_from_out()
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
            client.get('projects/404')

        self.assertEqual(str(app_error.exception),
                         '404 client error: Not Found')

    @responses.activate
    def test_404_json(self):
        """
        Bad request with datarobot reason in json
        """
        raw = """
        {"message": "Not Found"}
        """

        responses.add(responses.GET, 'https://host_name.com/projects/404',
                      body=raw, status=404, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get('projects/404')

        exception_message = str(app_error.exception)
        self.assertIn('404 client error', exception_message)
        self.assertIn('Not Found', exception_message)

    @responses.activate
    def test_500_json(self):
        """
        Bad request with datarobot reason in json
        """
        raw = """
        {"message": "Not Found"}
        """

        responses.add(responses.GET, 'https://host_name.com/projects/500',
                      body=raw, status=500, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get('projects/500')

        exception_message = str(app_error.exception)
        self.assertIn('500 server error', exception_message)
        self.assertIn('Not Found', exception_message)

    @responses.activate
    def test_other_errors(self):
        """
        Other errors
        """
        raw = """
        {"message": "Bad response"}
        """

        responses.add(responses.GET,
                      'https://host_name.com/projects/500',
                      body=raw, status=500, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get('projects/500')
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
                       'Job',
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
                       'Feature',
                       'helpers',
                       'RandomCV',
                       'StratifiedCV',
                       'GroupCV',
                       'UserCV',
                       'RandomTVH',
                       'UserTVH',
                       'StratifiedTVH',
                       'GroupTVH',
                       'partitioning_methods',
                       'RecommenderSettings',  # TODO: Too many attrs
                       'AdvancedOptions',
                       'VERBOSITY_LEVEL',
                       'enums'
                       }

        found_names = {name for name in dir(dr)
                       if not (name.startswith('__') and name.endswith('__'))}
        assert found_names == known_names


class TestProcessConfigFile(unittest.TestCase):

    @patch('datarobot.client._file_exists')
    @patch('datarobot.client.os', autospec=True)
    def test_get_config_file_from_environ(self, mock_os, mock_file_exists):
        mock_os.environ = {'DATAROBOT_CONFIG_FILE': 'fake_config_file'}
        mock_file_exists.return_value = True
        config_file = _get_config_file()
        self.assertEqual(config_file, 'fake_config_file')

    @patch('datarobot.client._file_exists')
    @patch('datarobot.client.os', autospec=True)
    def test_get_config_file_from_environ_dne(self, mock_os, mock_file_exists):
        mock_os.environ = {'DATAROBOT_CONFIG_FILE': 'fake_config_file'}
        mock_file_exists.return_value = False
        with self.assertRaises(ValueError):
            _get_config_file()

    @patch('datarobot.client._file_exists')
    @patch('datarobot.client.os.environ')
    def test_get_config_file_deprecated_exists(self, mock_os_environ, mock_file_exists):
        mock_os_environ.data = {}
        deprecated_config_path = os.path.join(os.path.expanduser('~'), '.datarobotrc')
        mock_file_exists.side_effect = \
            lambda path: True if path == deprecated_config_path else False
        self.assertEqual(_get_config_file(), deprecated_config_path)

    @patch('datarobot.client._file_exists')
    @patch('datarobot.client.os.environ')
    def test_get_config_file_both_exist(self, mock_os_environ, mock_file_exists):
        first_choice_config_path = os.path.expanduser('~/.config/datarobot/drconfig.yaml')
        mock_os_environ.data = {}
        mock_file_exists.return_value = True
        self.assertEqual(_get_config_file(), first_choice_config_path)

    @patch('datarobot.client._file_exists')
    @patch('datarobot.client.os', autospec=True)
    def test_get_default_config_file_dne(self, mock_os, mock_file_exists):
        mock_os.environ = {}
        mock_file_exists.return_value = False
        mock_os.path.join.return_value = '/i/dont/exist'
        self.assertIsNone(_get_config_file())

    def test_get_credentials_from_ini_file_present(self):
        file_content = ('[datarobot]\n'
                        'username=user@email.domain\n'
                        'password=file_password\n'
                        'token=fake_token')
        fake_config_file = NamedTemporaryFile(delete=False)
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
            username, password, token = _get_credentials_from_file(fake_config_file.name)
            self.assertEqual(username, 'user@email.domain')
            self.assertEqual(password, 'file_password')
            self.assertEqual(token, 'fake_token')
        finally:
            os.remove(fake_config_file.name)

    def test_get_credentials_from_yaml_file_present(self):
        file_content = ('username: user@email.domain\n'
                        'password: file_password\n'
                        'token: fake_token')
        fake_config_file = NamedTemporaryFile(delete=False, suffix='.yaml')
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
            username, password, token = _get_credentials_from_file(fake_config_file.name)
            self.assertEqual(username, 'user@email.domain')
            self.assertEqual(password, 'file_password')
            self.assertEqual(token, 'fake_token')
        finally:
            os.remove(fake_config_file.name)

    def test_get_credentials_from_file_file_dne(self):
        fake_config_file = NamedTemporaryFile()
        fake_config_file.close()
        self.assertFalse(os.path.exists(fake_config_file.name))
        username, password, token = _get_credentials_from_file(fake_config_file.name)
        self.assertIsNone(username)
        self.assertIsNone(password)
        self.assertIsNone(token)

    def test_get_credentials_from_file_partial_cred(self):
        file_content = ('[datarobot]\n'
                        'token=fake_token')
        fake_config_file = NamedTemporaryFile(delete=False)
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
            username, password, token = _get_credentials_from_file(fake_config_file.name)
            self.assertIsNone(username)
            self.assertIsNone(password)
            self.assertEqual(token, 'fake_token')
        finally:
            os.remove(fake_config_file.name)

    def test_get_endpoint_from_ini_file_succeess(self):
        file_content = ('[datarobot]\n'
                        'endpoint=http://host_name.com')
        fake_config_file = NamedTemporaryFile(delete=False)
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
        finally:
            os.remove(fake_config_file.name)

    def test_get_endpoint_from_yaml_file_succeess(self):
        file_content = ('endpoint: http://host_name.com')
        fake_config_file = NamedTemporaryFile(delete=False, suffix='.yaml')
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
        finally:
            os.remove(fake_config_file.name)

    def test_get_endpoint_from_file_file_dne(self):
        fake_config_file = NamedTemporaryFile()
        fake_config_file.close()
        self.assertFalse(os.path.exists(fake_config_file.name))
        self.assertIsNone(_get_endpoint_from_file(fake_config_file.name))

    def test_get_endpoint_from_file_missing(self):
        file_content = ('[datarobot]\n'
                        'token=fake_token')
        fake_config_file = NamedTemporaryFile(delete=False)
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
            self.assertIsNone(_get_endpoint_from_file(fake_config_file.name))
        finally:
            os.remove(fake_config_file.name)
