import json
import shutil
import tempfile
import textwrap

import click
import requests
import responses
from click.testing import CliRunner
from requests.exceptions import HTTPError, SSLError

from hatcher.core.auth import BroodBearerTokenAuth
from hatcher.core.brood_client import BroodClient as RealBroodClient
from hatcher.core.url_templates import URLS
from hatcher.testing import unittest, make_testing_egg
from hatcher.tests.common import MainTestingMixin
from hatcher.cli import main
from hatcher.cli import team_actions
from hatcher.cli import utils


class TestingException(Exception):
    pass


class TestBasic(MainTestingMixin, unittest.TestCase):
    def _get_brood_client_proxy(self, args=()):
        # Given
        out = []

        @main.hatcher.command('get-ctx', api_versions=[0, 1])
        @click.pass_context
        def get_ctx(ctx):
            """A testing command.
            """
            out.append(ctx.obj)

        # When
        CliRunner().invoke(
            main.hatcher,
            args=['-u', 'http://brood-dev'] + list(args) + ['get-ctx'],
        )

        self.assertEqual(len(out), 1)
        proxy, = out
        return proxy

    def test_help_short_option(self):
        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'http://brood-dev', '-h'],
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.output.startswith('Usage: hatcher'))

    def test_help_long_option(self):
        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'http://brood-dev', '--help'],
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.output.startswith('Usage: hatcher'))

    def test_all_commands_provide_help(self):
        """
        Generate all possible commands for hatcher and run that command
        with the ``--help`` option.  Regression test for #170.

        """
        # Given
        def _walk_commands(top_level, args_list=None):
            if args_list is None:
                args_list = ['--debug']
            yield args_list[:] + ['--help']
            if not isinstance(top_level, click.Group):
                return
            for api_version, commands in top_level.commands.items():
                for command_name, command in commands.items():
                    sub_args_list = args_list[:] + [command_name]
                    for item in _walk_commands(
                            command, args_list=sub_args_list[:]):
                        yield ['--api-version', str(api_version)] + item

        for args in _walk_commands(main.hatcher):
            # When
            result = CliRunner().invoke(main.hatcher, args=args)

            # Then
            self.assertIsNone(result.exception)
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(result.output.startswith('Usage: hatcher'))

    def test_brood_client_proxy(self):
        # Given
        proxy = self._get_brood_client_proxy()

        # Then
        self.assertIsInstance(proxy, utils.BroodClientProxy)
        self.assertTrue(proxy.verify_ssl)
        # realize brood_client
        proxy.organization
        brood_client = proxy.brood_client
        self.assertIsInstance(brood_client, RealBroodClient)
        url_handler = brood_client._url_handler
        self.assertTrue(url_handler._session.verify)

    def test_insecure_option(self):
        # Given
        proxy = self._get_brood_client_proxy(['--insecure'])

        # Then
        self.assertIsInstance(proxy, utils.BroodClientProxy)
        self.assertFalse(proxy.verify_ssl)
        # realize brood_client
        proxy.organization
        brood_client = proxy.brood_client
        self.assertIsInstance(brood_client, RealBroodClient)
        url_handler = brood_client._url_handler
        self.assertFalse(url_handler._session.verify)

    def test_print_command_tree(self):
        # When
        result = CliRunner().invoke(main.hatcher, args=['--command-tree'])

        # Then
        self.assertTrue(result.output.startswith('hatcher'))
        self.assertIn('[OPTIONS]', result.output)
        self.assertEqual(result.exit_code, 0)

    def test_url_required(self):
        # Given
        args = ['teams', 'list', 'enthought']

        # When
        result = CliRunner().invoke(main.hatcher, args=args)

        # Then
        self.assertRegexpMatches(result.output, r'Missing option.*?--url')
        self.assertEqual(result.exit_code, 2)

    def test_help_without_url_argument(self):
        # Given
        args = ['teams', 'list', 'enthought', '--help']

        # When
        result = CliRunner().invoke(main.hatcher, args=args)

        # Then
        self.assertRegexpMatches(
            result.output, team_actions.list_teams.help.strip())
        self.assertEqual(result.exit_code, 0)

    def test_no_auth(self):
        # Given
        self.auth = object()

        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher, args=['-u', 'brood-dev', 'dummy'])

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.auth, None)

    def test_auth_username_password(self):
        # Given
        username = 'user'
        password = 'password'

        self.auth = None

        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-U', username, '-p', password, 'dummy'])

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.auth, (username, password))

    def test_auth_username_no_password(self):
        # Given
        username = 'user'
        password = 'password'

        self.auth = None

        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-U', username, 'dummy'],
            input=password,
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.auth, (username, password))

    def test_auth_token(self):
        # Given
        token = 'token'

        self.auth = None

        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-t', token, 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertIsInstance(self.auth, BroodBearerTokenAuth)
        self.assertEqual(self.auth.token, token)

    def test_auth_token_and_password(self):
        # Given
        password = 'password'

        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            pass

        # When
        result = CliRunner().invoke(
            main.hatcher, args=['-u', 'brood-dev', '-p', password,
                                '-t', 'token', 'dummy'])

        # Then
        self.assertEqual(result.exit_code, 2)
        self.assertRegexpMatches(
            result.output, r'.*?Password provided with no username$')

    def test_auth_token_and_username(self):
        # Given
        username = 'user'
        password = 'password'

        self.auth = None

        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-U', username, '-t', 'token', 'dummy'],
            input=password,
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.auth, (username, password))

    def test_auth_password_no_username(self):
        # Given
        password = 'password'

        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            pass

        # When
        result = CliRunner().invoke(
            main.hatcher, args=['-u', 'brood-dev', '-p', password, 'dummy'])

        # Then
        self.assertEqual(result.exit_code, 2)
        self.assertRegexpMatches(
            result.output, r'.*?Password provided with no username$')

    def test_debug_flag_unset(self):
        # Given
        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            raise TestingException()

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-U', 'username', '-p', 'none',
                  '-t', 'token', 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertRegexpMatches(result.output, 'Unexpected error')
        self.assertIsInstance(result.exception, SystemExit)

    def test_debug_flag_set(self):
        # Given
        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            raise TestingException()

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '--debug', '-U', 'username', '-p', 'none',
                  '-t', 'token', 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, TestingException)

    @responses.activate
    def test_ssl_error(self):
        # Given
        host = 'https://brood-dev'
        url = '{host}{uri}'.format(
            host=host,
            uri=URLS.v0.indices.apps.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )

        def ssl_callback(request):
            raise SSLError(None, request=request)

        responses.add_callback(responses.GET, url,
                               callback=ssl_callback)

        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            raise requests.get(url)

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', host, '-U', 'username', '-p', 'none',
                  '-t', 'token', 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, -1)
        expected = ('To connect to {0} insecurely, pass the '
                    '`--insecure` flag'.format(host))
        self.assertRegexpMatches(result.output, expected)
        self.assertIsInstance(result.exception, SystemExit)

    @responses.activate
    def test_ssl_error_debug(self):
        # Given
        host = 'https://brood-dev'
        url = '{host}{uri}'.format(
            host=host,
            uri=URLS.v0.indices.apps.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )

        def ssl_callback(request):
            raise SSLError(None, request=request)

        responses.add_callback(responses.GET, url,
                               callback=ssl_callback)

        @main.hatcher.command(api_versions=[0, 1])
        @utils.pass_brood_client
        def dummy(brood_client):
            raise requests.get(url)

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['--debug', '-u', host, '-U', 'username', '-p', 'none',
                  '-t', 'token', 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.output, '')
        self.assertIsInstance(result.exception, SSLError)


class TestHttpErrors(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.temp_dir = tempfile.mkdtemp(prefix='hatcher-')

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        MainTestingMixin.tearDown(self)

    @responses.activate
    def test_http_error_debug_flag(self):
        # Given
        python_tag = 'pp27'
        host = 'http://brood-dev'
        error = 'Authentication failed'
        body = {'error': error}
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.indices.eggs.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                    python_tag=python_tag,
                ),
            ),
            status=401,
            body=json.dumps(body),
            content_type='application/json'
        )

        # When
        args = ['--debug', '-u', host, 'eggs', 'list', self.organization,
                self.repository, self.platform, python_tag]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(result.exit_code, -1)

    @responses.activate
    def test_json_formatted_error_on_download(self):
        # Given
        python_tag = 'pp27'
        host = 'http://brood-dev'
        error = 'Authentication failed'
        body = {'error': error}
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.indices.eggs.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                    python_tag=python_tag,
                ),
            ),
            status=401,
            body=json.dumps(body),
            content_type='application/json'
        )

        # When
        args = ['-u', host, 'eggs', 'list', self.organization, self.repository,
                self.platform, python_tag]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.output.strip(), error)

    @responses.activate
    def test_bad_json_formatted_error_on_download(self):
        # Given
        python_tag = 'cp27'
        host = 'http://brood-dev'
        error = 'Authentication failed'
        body = {'key': error}
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.indices.eggs.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                    python_tag=python_tag,
                ),
            ),
            status=401,
            body=json.dumps(body),
            content_type='application/json'
        )

        # When
        args = ['-u', host, 'eggs', 'list', self.organization, self.repository,
                self.platform, python_tag]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(abs(result.exit_code), 1)

    @responses.activate
    def test_non_json_error_on_download(self):
        # Given
        host = 'http://brood-dev'
        error = 'Some error'
        python_tag = 'ip27'
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.indices.eggs.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                    python_tag=python_tag,
                ),
            ),
            status=404,
            body=error,
            content_type='text/plain'
        )

        # When/Then
        args = ['-u', host, 'eggs', 'list', self.organization, self.repository,
                self.platform, python_tag]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(abs(result.exit_code), 1)

    @responses.activate
    def test_non_json_authentication_error_on_upload(self):
        # Given
        numpy = make_testing_egg(
            self.temp_dir, name='numpy', version='1.8.0', build=1)
        host = 'http://brood-dev'
        error = 'Some error'
        responses.add(
            responses.POST,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.data.eggs.upload.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                ),
            ),
            status=401,
            body=error,
            content_type='text/plain'
        )

        # When/Then
        args = ['-u', host, 'eggs', 'upload', self.organization,
                self.repository, self.platform, numpy.path]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, -1)
        self.assertTrue(
            result.output.strip().endswith('Authentication failed'))

    @responses.activate
    def test_debug_flag_on_upload(self):
        # Given
        numpy = make_testing_egg(
            self.temp_dir, name='numpy', version='1.8.0', build=1)

        host = 'http://brood-dev'
        error = 'Some error'
        responses.add(
            responses.POST,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.data.eggs.upload.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                ),
            ),
            status=401,
            body=error,
            content_type='text/plain'
        )

        # When/Then
        args = ['--debug', '-u', host, 'eggs', 'upload', self.organization,
                self.repository, self.platform, numpy.path]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(result.exit_code, -1)

    @responses.activate
    def test_non_json_not_found_error_on_upload(self):
        # Given
        numpy = make_testing_egg(
            self.temp_dir, name='numpy', version='1.8.0', build=1)
        host = 'http://brood-dev'
        error = 'Some error'
        responses.add(
            responses.POST,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.data.eggs.upload.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                ),
            ),
            status=404,
            body=error,
            content_type='text/plain'
        )

        # When/Then
        args = ['-u', host, 'eggs', 'upload', self.organization,
                self.repository, self.platform, numpy.path]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        expected_error = "No such repository: '{0}/{1}'".format(
            self.organization, self.repository)
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, -1)
        self.assertTrue(
            result.output.strip().endswith(expected_error))


class TestServerActionsMain(MainTestingMixin, unittest.TestCase):

    @responses.activate
    def test_list_platforms(self):
        # Given
        host = 'http://brood-dev'
        platforms = [
            'osx-x86',
            'osx-x86_64',
            'rh5-x86',
            'rh5-x86_64',
        ]
        expected = textwrap.dedent("""\
        Platforms
        -----------
        {0}
        """).format('\n'.join(sorted(platforms)))
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.metadata.platforms.format(),
            ),
            status=200,
            body=json.dumps({'platforms': platforms}),
            content_type='application/json',
        )

        # When
        args = ['-u', host, 'platforms', 'list']
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertEqual(result.output, expected)

    @responses.activate
    def test_list_top_level_python_tags(self):
        # Given
        host = 'http://brood-dev'
        python_tags = [
            'cp27',
            'pp27',
            'cp34'
        ]
        expected = textwrap.dedent("""\
        Python Tag
        ------------
        {0}
        """).format('\n'.join(sorted(python_tags)))

        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.metadata.python_tags.format(),
            ),
            status=200,
            body=json.dumps({'python_tags': python_tags}),
            content_type='application/json',
        )

        # When
        args = ['-u', host, 'python-tags', 'list']
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertEqual(result.output, expected)

    @responses.activate
    def test_list_all_python_tags(self):
        # Given
        host = 'http://brood-dev'
        python_tags = [
            'cp27',
            'pp27',
            'cp34',
            'py2',
            'ip2',
        ]
        expected = textwrap.dedent("""\
        Python Tag
        ------------
        {0}
        """).format('\n'.join(sorted(python_tags)))

        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.v0.metadata.python_tags.all.format(),
            ),
            status=200,
            body=json.dumps({'python_tags': python_tags}),
            content_type='application/json',
        )

        # When
        args = ['-u', host, 'python-tags', 'list', '--all']
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertEqual(result.output, expected)
