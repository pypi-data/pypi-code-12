from datetime import datetime
import hashlib
import json
import os
import textwrap

from mock import patch
import pytz
import responses
from six.moves.urllib import parse

from hatcher.core.url_templates import URLS
from hatcher.errors import ChecksumMismatchError
from hatcher.testing import unittest
from hatcher.tests.common import MainTestingMixin, patch_repository
from hatcher.cli import main, utils


class TestRuntimeMetadataMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.initial_args = ['--api-version', '0',
                             '--url', 'brood-dev.invalid', 'runtimes',
                             'metadata']
        self.final_args = [self.organization, self.repository, 'rh5-64',
                           'cp27', '2.7.3-1']

    @patch_repository
    def test_runtime_metadata(self, Repository):
        # Given
        expected = {
            'language': 'python',
            'version': '2.7.3',
            'build': 1,
        }
        repository, platform_repo = self._mock_repository_class(Repository)
        runtime_metadata = platform_repo.runtime_metadata
        runtime_metadata.return_value = expected

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args,
        )

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        runtime_metadata.assert_called_once_with('cp27', '2.7.3-1')
        self.assertEqual(json.loads(result.output), expected)
        self.assertEqual(result.exit_code, 0)


class TestUploadRuntimeMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.host = host = 'http://brood-dev.invalid'
        self.initial_args = ['--api-version', '0',
                             '--url', host, 'runtimes', 'upload']
        self.final_args = [self.organization, self.repository]

    def _upload_runtime(self, filename=None, data=None, force=False,
                        verify=False, debug=False):
        if data is None:
            data = 'data'
        if filename is None:
            filename = 'python_runtime_2.7.3_2.0.0_rh5-64_1.zip'
        initial_args = self.initial_args
        if force:
            initial_args = initial_args + ['--force']
        if verify:
            initial_args = initial_args + ['--verify']
        if debug:
            initial_args = ['--debug'] + initial_args
        with self.runner.isolated_filesystem() as tempdir:
            filename = os.path.join(tempdir, filename)
            with open(filename, 'w') as fh:
                fh.write(data)

            result = self.runner.invoke(
                main.hatcher,
                args=initial_args + self.final_args + [filename],
            )

        return filename, result

    @responses.activate
    def test_without_force(self):
        # Given
        upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.v0.data.runtimes.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )
        responses.add(
            responses.POST,
            upload_url,
            status=204,
        )

        # When
        with patch.object(
                utils, 'get_localtime') as get_localtime:
            now = datetime(2016, 2, 9, 10, 29, 7, tzinfo=pytz.utc)
            get_localtime.return_value = now.astimezone(
                pytz.timezone('Europe/Helsinki'))
            filename, result = self._upload_runtime(force=False)

        # Given
        expected_output = textwrap.dedent("""\
        Runtime upload  {filename}
        Server          {server}
        Repository      {organization}/{repository}
        Time            {time}
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
            uri=URLS.v0.data.runtimes.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )
        responses.add(
            responses.POST,
            upload_url,
            status=204,
        )

        # When
        with patch.object(
                utils, 'get_localtime') as get_localtime:
            now = datetime(2016, 2, 9, 10, 29, 7, tzinfo=pytz.utc)
            get_localtime.return_value = now.astimezone(
                pytz.timezone('Europe/Helsinki'))
            filename, result = self._upload_runtime(force=True)

        # Given
        expected_output = textwrap.dedent("""\
        Runtime upload  {filename}
        Server          {server}
        Repository      {organization}/{repository}
        Time            {time}
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

    @responses.activate
    def test_upload_no_verify(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'

        upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.v0.data.runtimes.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )
        responses.add(
            responses.POST,
            upload_url,
            status=204,
        )

        # When
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 1)
        upload_request, = responses.calls

        parsed = parse.urlsplit(upload_request.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, upload_url)

    @responses.activate
    def test_upload_verify_no_upstream(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.v0.metadata.artefacts.runtimes.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                version='2.7.6-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            status=404,
        )

        upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.v0.data.runtimes.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )
        responses.add(
            responses.POST,
            upload_url,
            status=200,
        )

        # When
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data, verify=True)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 2)
        metadata_request, upload_request = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)

        parsed = parse.urlsplit(upload_request.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, upload_url)

    @responses.activate
    def test_upload_verify_valid(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'
        sha256 = hashlib.sha256(data.encode('ascii')).hexdigest()
        server_metadata = {
            'sha256': sha256,
        }

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.v0.metadata.artefacts.runtimes.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                version='2.7.6-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            content_type='application/json',
            status=200,
            body=json.dumps(server_metadata),
        )

        # When
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data, verify=True)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 1)
        metadata_request, = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)

    @responses.activate
    def test_upload_verify_checksum_failure(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'
        server_metadata = {
            'sha256': 'invalid sha256',
        }

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.v0.metadata.artefacts.runtimes.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                version='2.7.6-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            content_type='application/json',
            status=200,
            body=json.dumps(server_metadata),
        )

        # When
        ## Use --debug so that we can assert on the actual exception
        ## raised rather than a SystemExit from the Exception handler
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data, verify=True, debug=True)

        # Then
        self.assertIsInstance(result.exception, ChecksumMismatchError)
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(len(responses.calls), 1)
        metadata_request, = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)

    @responses.activate
    def test_upload_verify_error(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'
        error = 'An error'

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.v0.metadata.artefacts.runtimes.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                version='2.7.6-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            content_type='application/json',
            status=400,
            body=json.dumps({'error': error})
        )

        # When
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data, verify=True)

        # Then
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, -1)
        self.assertTrue(result.output.strip().endswith(error))
        self.assertEqual(len(responses.calls), 1)
        metadata_request, = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)


class TestDownloadRuntimeMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.initial_args = ['--api-version', '0',
                             '--url', 'brood-dev.invalid', 'runtimes',
                             'download']
        self.final_args = [self.organization, self.repository, self.platform]

    @patch_repository
    def test_download(self, Repository):
        # Given
        args = ['cp27', '2.7.3-1', 'destination']
        repository, platform_repo = self._mock_repository_class(Repository)
        iter_download_runtime = platform_repo.iter_download_runtime
        iter_download_runtime.return_value = 0, []

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args + args,
        )

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        iter_download_runtime.assert_called_once_with(*args)
        self.assertEqual(result.exit_code, 0)


class TestListRuntimesMain(MainTestingMixin, unittest.TestCase):

    @responses.activate
    def test_list_runtimes(self):
        # Given
        host = host = 'http://brood-dev.invalid'

        filename_2_7_3_1 = 'python_runtime_2.7.3_2.0.0_rh5-64_1.zip'
        filename_2_7_3_2 = 'python_runtime_2.7.3_2.0.0_rh5-64_2.zip'
        filename_2_7_9_1 = 'python_runtime_2.7.9_2.0.0_rh5-64_1.zip'
        response = {
            'python': {
                '2.7.3': {
                    '1': {
                        'filename': filename_2_7_3_1,
                    },
                    '2': {
                        'filename': filename_2_7_3_2,
                    },
                },
                '2.7.9': {
                    '1': {
                        'filename': filename_2_7_9_1,
                    },
                },
            },
        }
        runtimes = ['runtime2', 'runtime1']
        expected = '{0}\n'.format('\n'.join(sorted(runtimes)))

        expected = textwrap.dedent("""\
        Runtime    Version    Python Tag
        ---------  ---------  ------------
        python     2.7.3-1    cp27
        python     2.7.3-2    cp27
        python     2.7.9-1    cp27
        """)

        metadata_url = '{host}{uri}'.format(
            host=host,
            uri=URLS.v0.indices.runtimes.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            content_type='application/json',
            status=200,
            body=json.dumps(response)
        )

        args = ['--api-version', '0',
                '--url', 'brood-dev.invalid', 'runtimes', 'list',
                self.organization, self.repository, self.platform]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)
