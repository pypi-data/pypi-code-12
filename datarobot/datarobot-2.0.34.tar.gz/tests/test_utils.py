import os
import datetime
import unittest
from tempfile import NamedTemporaryFile

import pandas as pd
from mock import patch
import responses

from datarobot.client import Client, set_client
from datarobot.utils import (dataframe_to_buffer, parse_time, get_id_from_response,
                             from_api, get_config_file, get_creds_from_file,
                             get_endpoint_from_file, deprecation,
                             recognize_sourcedata, is_urlsource)
from .test_helpers import fixture_file_path
from .utils import warns


class TestDataframeSerialization(unittest.TestCase):
    def test_no_index_please(self):
        df = pd.DataFrame({'a': range(100), 'b': range(100)})
        buff = dataframe_to_buffer(df)
        readback = pd.read_csv(buff)
        self.assertEqual(readback.columns.tolist(), ['a', 'b'])

    def test_parse_time(self):
        self.assertEqual('BAD TIME', parse_time('BAD TIME'))  # returns value
        test_string_time = datetime.datetime.now().isoformat()
        self.assertIsInstance(test_string_time, str)
        self.assertIsInstance(parse_time(test_string_time), datetime.datetime)

    @responses.activate
    def test_get_id_from_response_location_header(self):
        responses.add(responses.POST,
                      'http://nothing/',
                      body='',
                      adding_headers={'Location': 'http://nothing/f-id/'})
        client = set_client(Client(token='no_matter',
                                   endpoint='http://nothing'))
        resp = client.post('')
        self.assertEqual(get_id_from_response(resp), 'f-id')


class TestFromAPI(unittest.TestCase):
    def test_nested_list_of_objects_all_changed(self):
        source = {
            'oneFish': [
                {'twoFish': 'redFish'},
                {'blueFish': 'noFish'}
            ]
        }
        result = from_api(source)
        inner = result['one_fish']
        self.assertEqual(inner[0]['two_fish'], 'redFish')
        self.assertEqual(inner[1]['blue_fish'], 'noFish')

    def test_nested_objects_all_changed(self):
        source = {
            'oneFish': {
                'twoFish': 'redFish'
            }
        }

        result = from_api(source)
        self.assertEqual(result['one_fish']['two_fish'], 'redFish')


class TestProcessConfigFile(unittest.TestCase):
    @patch('datarobot.utils.file_exists')
    @patch('datarobot.utils.os', autospec=True)
    def test_get_config_file_from_environ(self, mock_os, mock_file_exists):
        mock_os.environ = {'DATAROBOT_CONFIG_FILE': 'fake_config_file'}
        mock_file_exists.return_value = True
        config_file = get_config_file()
        self.assertEqual(config_file, 'fake_config_file')

    @patch('datarobot.utils.file_exists')
    @patch('datarobot.utils.os', autospec=True)
    def test_get_config_file_from_environ_dne(self, mock_os, mock_file_exists):
        mock_os.environ = {'DATAROBOT_CONFIG_FILE': 'fake_config_file'}
        mock_file_exists.return_value = False
        with self.assertRaises(ValueError):
            get_config_file()

    @patch('datarobot.utils.file_exists')
    @patch('datarobot.utils.os', autospec=True)
    def test_get_default_config_file_exists(self, mock_os, mock_file_exists):
        mock_os.environ = {}
        mock_file_exists.return_value = True
        fake_config_file = '/fake/config/file/path'
        mock_os.path.join.return_value = fake_config_file
        self.assertEqual(get_config_file(), fake_config_file)

    @patch('datarobot.utils.file_exists')
    @patch('datarobot.utils.os', autospec=True)
    def test_get_default_config_file_dne(self, mock_os, mock_file_exists):
        mock_os.environ = {}
        mock_file_exists.return_value = False
        mock_os.path.join.return_value = '/i/dont/exist'
        self.assertIsNone(get_config_file())

    def test_get_creds_from_file_present(self):
        file_content = ('[datarobot]\n'
                        'username=user@email.domain\n'
                        'password=file_password\n'
                        'token=fake_token')
        fake_config_file = NamedTemporaryFile(delete=False)
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
            username, password, token = get_creds_from_file(fake_config_file.name)
            self.assertEqual(username, 'user@email.domain')
            self.assertEqual(password, 'file_password')
            self.assertEqual(token, 'fake_token')
        finally:
            os.remove(fake_config_file.name)

    def test_get_creds_from_file_file_dne(self):
        fake_config_file = NamedTemporaryFile()
        fake_config_file.close()
        self.assertFalse(os.path.exists(fake_config_file.name))
        username, password, token = get_creds_from_file(fake_config_file.name)
        self.assertIsNone(username)
        self.assertIsNone(password)
        self.assertIsNone(token)

    def test_get_creds_from_file_partial_cred(self):
        file_content = ('[datarobot]\n'
                        'token=fake_token')
        fake_config_file = NamedTemporaryFile(delete=False)
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
            username, password, token = get_creds_from_file(fake_config_file.name)
            self.assertIsNone(username)
            self.assertIsNone(password)
            self.assertEqual(token, 'fake_token')
        finally:
            os.remove(fake_config_file.name)

    def test_get_endpoint_from_file_succeess(self):
        file_content = ('[datarobot]\n'
                        'endpoint=http://host_name.com')
        fake_config_file = NamedTemporaryFile(delete=False)
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
        finally:
            os.remove(fake_config_file.name)

    def test_get_endpoint_from_file_file_dne(self):
        fake_config_file = NamedTemporaryFile()
        fake_config_file.close()
        self.assertFalse(os.path.exists(fake_config_file.name))
        self.assertIsNone(get_endpoint_from_file(fake_config_file.name))

    def test_get_endpoint_from_file_missing(self):
        file_content = ('[datarobot]\n'
                        'token=fake_token')
        fake_config_file = NamedTemporaryFile(delete=False)
        try:
            with open(fake_config_file.name, mode='w') as config_file:
                config_file.write(file_content)
            self.assertIsNone(get_endpoint_from_file(fake_config_file.name))
        finally:
            os.remove(fake_config_file.name)


@deprecation.deprecated(deprecated_since_version='v0.1.2',
                        will_remove_version='v1.2.3')
def bar(arg1, arg2):
    """
    A dummy function to use for testing the deprecation mechanisms

    Parameters
    ----------
    arg1 : int
    arg2 : int

    Returns
    -------
    total : int
        arg1 + arg2

    """
    return arg1 + arg2


@deprecation.deprecated(deprecated_since_version='v0.1.2',
                        will_remove_version='v1.2.3',
                        message='Use of `bar` is recommended instead.')
def foo(arg1, arg2):
    """
    A dummy function to use for testing the deprecation mechanisms

    Parameters
    ----------
    arg1 : int
    arg2 : int

    Returns
    -------
    total : int
        foo + bar

    """
    return arg1 + arg2


class TestDeprecation(unittest.TestCase):
    def test_deprecation_with_message(self):
        with warns(DeprecationWarning) as messages:
            foo(1, 2)
        assert str(messages[-1].message) == \
            '`foo` has been deprecated in `v0.1.2`, will be removed ' \
            'in `v1.2.3`. Use of `bar` is recommended instead.'

    def test_deprecation_message(self):
        with warns(DeprecationWarning):
            bar(1, 2)


class TestSourcedataUtils(unittest.TestCase):
    def setUp(self):
        self.default_fname = 'predict.csv'

    def test_recognize_sourcedata_passed_dataframe(self):
        df = pd.DataFrame({'a': range(100), 'b': range(100)})
        kwargs = recognize_sourcedata(df, self.default_fname)
        self.assertTrue('filelike' in kwargs)
        self.assertEqual(kwargs.get('fname'), self.default_fname)
        buff = kwargs['filelike']
        readback = pd.read_csv(buff)
        self.assertEqual(readback.columns.tolist(), ['a', 'b'])

    def test_recognize_sourcedata_passed_filelike(self):
        path = fixture_file_path('synthetic-100.csv')
        with open(path, 'rb') as fd:
            kwargs = recognize_sourcedata(fd, self.default_fname)
            self.assertTrue(kwargs.get('filelike') is fd)
            self.assertEqual(kwargs.get('fname'), self.default_fname)

    def test_recognize_sourcedata_passed_filepath(self):
        file_path = fixture_file_path('synthetic-100.csv')
        kwargs = recognize_sourcedata(file_path, self.default_fname)
        self.assertEqual(kwargs.get('file_path'), file_path)
        self.assertEqual(kwargs.get('fname'), 'synthetic-100.csv')

    def test_recognize_sourcedata_passed_content(self):
        content = b'abc'
        kwargs = recognize_sourcedata(content, self.default_fname)
        self.assertEqual(kwargs.get('content'), content)
        self.assertEqual(kwargs.get('fname'), self.default_fname)

    def test_is_urlsource_passed_true(self):
        result = is_urlsource('http://path_to_urlsource')
        self.assertTrue(result)

    def test_is_urlsource_passed_false(self):
        result = is_urlsource('not_a_path_to_urlsource')
        self.assertFalse(result)


def test_resource():
    """Python 3 ResourceWarning of implicitly closed files."""
    with warns():
        open(__file__)
