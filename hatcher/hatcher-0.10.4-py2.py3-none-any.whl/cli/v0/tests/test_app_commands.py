from datetime import datetime
import json
import os
import textwrap

from mock import patch
from six.moves.urllib import parse
import responses
import pytz

from hatcher.core.url_templates import URLS
from hatcher.testing import unittest
from hatcher.tests.common import (
    MainTestingMixin,
    patch_repository,
)
from hatcher.cli import main, utils


class TestUploadAppMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.host = 'http://brood-dev.invalid'
        self.platform = 'rh5-x86_64'
        self.initial_args = ['--url', self.host, 'apps', 'upload']
        self.final_args = [self.organization, self.repository]

    def _upload_app(self, force=False):
        if force:
            initial_args = self.initial_args + ['--force']
        else:
            initial_args = self.initial_args
        with self.runner.isolated_filesystem() as tempdir:
            filename = os.path.join(tempdir, 'mayavi.app')
            with open(filename, 'wb') as fh:
                fh.write(
                    json.dumps({'platform': self.platform}).encode('utf-8'))

            result = self.runner.invoke(
                main.hatcher,
                args=initial_args + self.final_args + [filename],
                catch_exceptions=False
            )

        return filename, result

    @responses.activate
    def test_without_force(self):
        # Given
        upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.v0.data.apps.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            )
        )
        responses.add(
            responses.POST,
            upload_url,
            status=204,
            content_type='application/json'
        )

        # When
        with patch.object(
                utils, 'get_localtime') as get_localtime:
            now = datetime(2016, 2, 9, 10, 29, 7, tzinfo=pytz.utc)
            get_localtime.return_value = now.astimezone(
                pytz.timezone('Europe/Helsinki'))
            filename, result = self._upload_app(force=False)

        # Given
        expected_output = textwrap.dedent("""\
        App upload  {filename}
        Server      {server}
        Repository  {organization}/{repository}
        Time        {time}
        """).format(
            filename=filename,
            server=self.host,
            organization=self.organization,
            repository=self.repository,
            time='2016-02-09 12:29:07 EET (+0200)',
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_output)
        self.assertEqual(len(responses.calls), 1)
        upload_request, = responses.calls

        parsed = parse.urlsplit(upload_request.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, upload_url)
        self.assertEqual(parsed[3], 'overwrite=False')

    @responses.activate
    def test_with_force(self):
        # Given
        upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.v0.data.apps.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            )
        )
        responses.add(
            responses.POST,
            upload_url,
            status=204,
            content_type='application/json'
        )

        # When
        with patch.object(
                utils, 'get_localtime') as get_localtime:
            now = datetime(2016, 2, 9, 10, 29, 7, tzinfo=pytz.utc)
            get_localtime.return_value = now.astimezone(
                pytz.timezone('Europe/Helsinki'))
            filename, result = self._upload_app(force=True)

        # Given
        expected_output = textwrap.dedent("""\
        App upload  {filename}
        Server      {server}
        Repository  {organization}/{repository}
        Time        {time}
        """).format(
            filename=filename,
            server=self.host,
            organization=self.organization,
            repository=self.repository,
            time='2016-02-09 12:29:07 EET (+0200)',
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_output)
        self.assertEqual(len(responses.calls), 1)
        upload_request, = responses.calls

        parsed = parse.urlsplit(upload_request.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, upload_url)
        self.assertEqual(parsed[3], 'overwrite=True')


class TestAppsMetadataMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.app_name = 'mayavi'
        self.app_version = '2.2'
        self.app_build = '1'
        self.app_full_version = '{0}-{1}'.format(
            self.app_version, self.app_build)
        self.python_tag = 'cp27'
        self.initial_args = ['--url', 'brood-dev.invalid', 'apps', 'metadata']
        self.final_args = [
            self.organization, self.repository, self.platform, self.python_tag,
            self.app_name, self.app_full_version]

    def _upload_app(self):
        with self.runner.isolated_filesystem() as tempdir:
            filename = os.path.join(tempdir, 'mayavi.app')
            with open(filename, 'w') as fh:
                fh.write('data')

            result = self.runner.invoke(
                main.hatcher,
                args=self.initial_args + self.final_args + [filename],
            )

        return filename, result

    @patch_repository
    def test_app_metadata(self, Repository):
        # Given
        expected = {'id': 'mayavi',
                    'name': 'Mayavi',
                    'version': '2.2',
                    'build': 1,
                    'python_tag': 'cp27'}
        repository, platform_repo = self._mock_repository_class(Repository)
        app_metadata = platform_repo.app_metadata
        app_metadata.return_value = expected

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args,
        )

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        repository.platform.assert_called_once_with(self.platform)
        app_metadata.assert_called_once_with(
            self.python_tag, self.app_name, self.app_full_version)
        self.assertEqual(json.loads(result.output), expected)
        self.assertEqual(result.exit_code, 0)


class TestListAppsMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.host = 'http://brood-dev'
        self.app_name = 'mayavi'
        self.app_version = '2.2'
        self.app_build = '1'
        self.initial_args = ['--url', self.host, 'apps', 'list']
        self.final_args = [
            self.organization, self.repository, self.platform]

    @responses.activate
    def test_list_apps(self):
        # Given
        given_index = {
            'cp27': {
                'numpy.demo': {
                    '1.0': {
                        '1': {
                            'name': 'Numpy demo',
                            'description': 'Simple numpy demo',
                            'python_tag': 'cp27',
                        },
                    },
                },
                'mayavi.demo': {
                    '4.6.0': {
                        '1': {
                            'name': 'Mayavi demo',
                            'description': 'Simple mayavi demo',
                            'python_tag': 'cp27',
                        },
                    },
                },
            },
            'py2': {
                'purepython': {
                    '1.0.0': {
                        '2': {
                            'name': 'Pure Python',
                            'description': 'None',
                            'python_tag': 'py2',
                        },
                    },
                    '1.0.0.dev1': {
                        '2': {
                            'name': 'Pure Python',
                            'description': 'None',
                            'python_tag': 'py2',
                        },
                    },
                },
            },
        }
        expected = textwrap.dedent("""\
        App Name     Version       Python Tag
        -----------  ------------  ------------
        mayavi.demo  4.6.0-1       cp27
        numpy.demo   1.0-1         cp27
        purepython   1.0.0.dev1-2  py2
        purepython   1.0.0-2       py2
        """)

        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=self.host,
                uri=URLS.v0.indices.apps.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                )
            ),
            body=json.dumps(given_index),
            status=200,
            content_type='application/json'
        )

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args,
        )

        # Then
        self.assertEqual(result.output, expected)
        self.assertEqual(result.exit_code, 0)
