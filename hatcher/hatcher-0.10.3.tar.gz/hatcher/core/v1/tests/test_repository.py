import hashlib
import json
import os
import re
import shutil
import tempfile

import responses

from hatcher.errors import ChecksumMismatchError, InvalidRuntime
from hatcher.testing import (
    unittest, runtime_from_metadata,
    RUNTIME_CPYTHON_2_7_10_RH5_X86_64_METADATA,
)
from ...brood_url_handler import BroodURLHandler
from ...model_registry import ModelRegistry
from ...tests.common import JsonSchemaTestMixin
from ...url_templates import URLS
from ..repository import Repository


BODY_FILENAME_RE = re.compile(
    r'Content-Disposition: form-data; name="file"; filename="(.*?)"')


class TestRepository(JsonSchemaTestMixin, unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix='hatcher-', suffix='-tmp')
        self.temp_dir2 = tempfile.mkdtemp(prefix='hatcher-', suffix='-tmp')
        self.url_handler = BroodURLHandler.from_auth('http://brood-dev')
        self.repository = Repository(
            'enthought', 'free', self.url_handler,
            model_registry=ModelRegistry(api_version=1))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.temp_dir2)

    @responses.activate
    def test_list_runtimes(self):
        # Given
        index = {
            "cpython": {
                "2.7.10+1": {
                    "abi": "gnu",
                    "filename": "cpython-2.7.10+1-rh5_x86_64-gnu.runtime",
                    "implementation": "cpython",
                    "language_version": "2.7.10",
                    "platform": "rh5-x86_64",
                    "sha256": "81ec4d15bd8b131c80eb72cb0f5222846e306bb3f1dd8ce572ffbe859ace1608",  # noqa
                    "version": "2.7.10+1",
                },
                "3.4.3+2": {
                    "abi": "gnu",
                    "filename": "cpython-3.4.3+2-rh5_x86_64-gnu.runtime",
                    "implementation": "cpython",
                    "language_version": "3.4.3",
                    "platform": "rh5-x86_64",
                    "sha256": "2846e306bb3f1dd8ce572ffbe859ace160881ec4d15bd8b131c80eb72cb0f522",  # noqa
                    "version": "3.4.3+2",
                },
            },
        }

        expected = [('cpython', '2.7.10+1',),
                    ('cpython', '3.4.3+2',)]
        platform_name = 'rh5-x86_64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.indices.runtimes.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                )
            ),
            body=json.dumps(index),
            status=200,
            content_type='application/json',
        )

        platform = self.repository.platform(platform_name)

        # When
        metadata = platform.list_runtimes()

        # Then
        self.assertEqual(list(sorted(metadata)), list(sorted(expected)))

    @responses.activate
    def test_runtime_index(self):
        # Given
        given_index = {
            "cpython": {
                "2.7.10+1": {
                    "abi": "gnu",
                    "filename": "cpython-2.7.10+1-rh5_x86_64-gnu.runtime",
                    "implementation": "cpython",
                    "language_version": "2.7.10",
                    "platform": "rh5-x86_64",
                    "sha256": "81ec4d15bd8b131c80eb72cb0f5222846e306bb3f1dd8ce572ffbe859ace1608",  # noqa
                    "version": "2.7.10+1",
                },
                "3.4.3+2": {
                    "abi": "gnu",
                    "filename": "cpython-3.4.3+2-rh5_x86_64-gnu.runtime",
                    "implementation": "cpython",
                    "language_version": "3.4.3",
                    "platform": "rh5-x86_64",
                    "sha256": "2846e306bb3f1dd8ce572ffbe859ace160881ec4d15bd8b131c80eb72cb0f522",  # noqa
                    "version": "3.4.3+2",
                },
            },
        }

        platform_name = 'rh5-x86_64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.indices.runtimes.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                )
            ),
            body=json.dumps(given_index),
            status=200,
            content_type='application/json',
        )

        platform = self.repository.platform(platform_name)

        # When
        obtained_index = platform.runtime_index()

        # Then
        self.assertEqual(dict(obtained_index), dict(given_index))

    @responses.activate
    def test_runtime_metadata(self):
        # Given
        implementation = 'cpython'
        version = '2.7.10+1'
        platform_name = 'rh5-x86_6464'
        platform = self.repository.platform(platform_name)

        expected = {
            "abi": "gnu",
            "build_revision": "2.1.0-dev570",
            "filename": "cpython-2.7.10+1-rh5_x86_64-gnu.runtime",
            "implementation": "cpython",
            "language_version": "2.7.10",
            "metadata_version": "1.0",
            "platform": "rh5-x86_64",
            "sha256": "81ec4d15bd8b131c80eb72cb0f5222846e306bb3f1dd8ce572ffbe859ace1608",  # noqa
            "version": "2.7.10+1"
        }

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=json.dumps(expected),
            status=200,
            content_type='application/json',
        )

        # When
        metadata = platform.runtime_metadata(implementation, version)

        # Then
        self.assertEqual(metadata, expected)

    @responses.activate
    def test_download_runtime(self):
        # Given
        implementation = 'cpython'
        version = '2.7.10+1'
        platform_name = 'rh5-x86_64'
        platform = self.repository.platform(platform_name)
        filename = 'cpython-2.7.10+1-rh5_x86_64-gnu.runtime'
        body = 'data'.encode('ascii')
        sha256 = hashlib.sha256(body).hexdigest()

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(len(body)),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        platform.download_runtime(
            implementation, version, destination=self.temp_dir)

        # Then
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertTrue(os.path.isfile(filename),
                        msg='Expected file {0!r} to exist'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        with open(filename, 'rb') as fh:
            self.assertEqual(fh.read(), body)

    @responses.activate
    def test_download_runtime_bad_sha(self):
        # Given
        implementation = 'cpython'
        version = '2.7.10+1'
        platform_name = 'rh5-x86_64'
        platform = self.repository.platform(platform_name)
        filename = 'cpython-2.7.10+1-rh5_x86_64-gnu.runtime'
        body = 'data'.encode('ascii')
        sha256 = 'abc123efd'

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(len(body)),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        with self.assertRaises(ChecksumMismatchError):
            platform.download_runtime(
                implementation, version, destination=self.temp_dir)

        # Then
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

    @responses.activate
    def test_download_runtime_provided_sha256(self):
        # Given
        implementation = 'cpython'
        version = '2.7.10+1'
        platform_name = 'rh5-x86_64'
        platform = self.repository.platform(platform_name)
        filename = 'cpython-2.7.10+1-rh5_x86_64-gnu.runtime'
        body = 'data'.encode('ascii')
        sha256 = hashlib.sha256(body).hexdigest()

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(len(body)),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )

        # When
        platform.download_runtime(
            implementation, version, destination=self.temp_dir,
            expected_sha256=sha256)

        # Then
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertTrue(os.path.isfile(filename),
                        msg='Expected file {0!r} to exist'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        with open(filename, 'rb') as fh:
            self.assertEqual(fh.read(), body)

    @responses.activate
    def test_download_runtime_provided_bad_sha256(self):
        # Given
        implementation = 'cpython'
        version = '2.7.10+1'
        platform_name = 'rh5-x86_64'
        platform = self.repository.platform(platform_name)
        filename = 'cpython-2.7.10+1-rh5_x86_64-gnu.runtime'
        body = 'data'.encode('ascii')
        bad_body = 'not-data'.encode('ascii')
        sha256 = hashlib.sha256(bad_body).hexdigest()

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(len(body)),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )

        # When
        with self.assertRaises(ChecksumMismatchError):
            platform.download_runtime(
                implementation, version, destination=self.temp_dir,
                expected_sha256=sha256)

        # Then
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(os.path.isfile(filename),
                         msg='Expected file {0!r} to exist'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

    @responses.activate
    def test_iter_download_runtime(self):
        # Given
        implementation = 'cpython'
        version = '2.7.10+1'
        platform_name = 'rh5-x86_64'
        platform = self.repository.platform(platform_name)
        filename = 'cpython-2.7.10+1-rh5_x86_64-gnu.runtime'
        body = 'data'.encode('ascii')
        sha256 = hashlib.sha256(body).hexdigest()
        content_length = len(body)

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(content_length),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        length, iterator = platform.iter_download_runtime(
            implementation, version, destination=self.temp_dir)

        # Then
        self.assertEqual(length, content_length)
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        next(iterator)
        self.assertTrue(
            os.path.isfile(temp_filename),
            msg='Expected file {0!r} to exist'.format(temp_filename))
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))

        with self.assertRaises(StopIteration):
            next(iterator)

        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))
        self.assertTrue(
            os.path.isfile(filename),
            msg='Expected file {0!r} to exist'.format(filename))

        with open(filename, 'rb') as fh:
            self.assertEqual(fh.read(), body)

    @responses.activate
    def test_iter_download_runtime_bad_sha(self):
        # Given
        implementation = 'cpython'
        version = '2.7.10+1'
        platform_name = 'rh5-x86_64'
        platform = self.repository.platform(platform_name)
        filename = 'cpython-2.7.10+1-rh5_x86_64-gnu.runtime'
        body = 'data'.encode('ascii')
        sha256 = 'abc123efd'
        content_length = len(body)

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(content_length),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        length, iterator = platform.iter_download_runtime(
            implementation, version, destination=self.temp_dir)

        # Then
        self.assertEqual(length, content_length)
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        next(iterator)
        self.assertTrue(
            os.path.isfile(temp_filename),
            msg='Expected file {0!r} to exist'.format(temp_filename))
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))

        with self.assertRaises(ChecksumMismatchError):
            next(iterator)

        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))
        self.assertFalse(
            os.path.isfile(filename),
            msg='Expected file {0!r} to exist'.format(filename))

    @responses.activate
    def test_iter_download_runtime_provided_sha256(self):
        # Given
        implementation = 'cpython'
        version = '2.7.10+1'
        platform_name = 'rh5-x86_64'
        platform = self.repository.platform(platform_name)
        filename = 'cpython-2.7.10+1-rh5_x86_64-gnu.runtime'
        body = 'data'.encode('ascii')
        sha256 = hashlib.sha256(body).hexdigest()
        content_length = len(body)

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(content_length),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )

        # When
        length, iterator = platform.iter_download_runtime(
            implementation, version, destination=self.temp_dir,
            expected_sha256=sha256)

        # Then
        self.assertEqual(length, content_length)
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        next(iterator)
        self.assertTrue(
            os.path.isfile(temp_filename),
            msg='Expected file {0!r} to exist'.format(temp_filename))
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))

        with self.assertRaises(StopIteration):
            next(iterator)

        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))
        self.assertTrue(
            os.path.isfile(filename),
            msg='Expected file {0!r} to exist'.format(filename))

        with open(filename, 'rb') as fh:
            self.assertEqual(fh.read(), body)

    @responses.activate
    def test_iter_download_runtime_provided_bad_sha256(self):
        # Given
        implementation = 'cpython'
        version = '2.7.10+1'
        platform_name = 'rh5-x86_64'
        platform = self.repository.platform(platform_name)
        filename = 'cpython-2.7.10+1-rh5_x86_64-gnu.runtime'
        body = 'data'.encode('ascii')
        bad_body = 'not-data'.encode('ascii')
        sha256 = hashlib.sha256(bad_body).hexdigest()
        content_length = len(body)

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform=platform_name,
                    implementation=implementation,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(content_length),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )

        # When
        length, iterator = platform.iter_download_runtime(
            implementation, version, destination=self.temp_dir,
            expected_sha256=sha256)

        # Then
        self.assertEqual(length, content_length)
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        next(iterator)
        self.assertTrue(
            os.path.isfile(temp_filename),
            msg='Expected file {0!r} to exist'.format(temp_filename))
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))

        with self.assertRaises(ChecksumMismatchError):
            next(iterator)

        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))
        self.assertFalse(
            os.path.isfile(filename),
            msg='Expected file {0!r} to exist'.format(filename))

    @responses.activate
    def test_upload_runtime(self):
        # Given
        filepath = runtime_from_metadata(
            self.temp_dir, RUNTIME_CPYTHON_2_7_10_RH5_X86_64_METADATA)

        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    # okonomiyaki is now generating this format of
                    # platform string
                    platform='rh5_x86_64',
                ),
            ),
        )

        # When
        self.repository.upload_runtime(filepath)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)
        self.assertJsonValid(json_data, 'upload_runtime_v1.json')
        self.assertRegexpMatches(request.url, r'^.*?\?overwrite=False$')

    @responses.activate
    def test_upload_runtime_force(self):
        # Given
        filepath = runtime_from_metadata(
            self.temp_dir, RUNTIME_CPYTHON_2_7_10_RH5_X86_64_METADATA)

        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.v1.data.runtimes.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    # okonomiyaki is now generating this format of
                    # platform string
                    platform='rh5_x86_64',
                ),
            ),
        )

        # When
        self.repository.upload_runtime(filepath, overwrite=True)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)
        self.assertJsonValid(json_data, 'upload_runtime_v1.json')
        self.assertRegexpMatches(request.url, r'^.*?\?overwrite=True$')

    @responses.activate
    def test_upload_runtime_not_zipfile(self):
        # Given
        filename = 'runtime'
        data = 'python'
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as fh:
            fh.write(data)

        # When/Then
        with self.assertRaises(InvalidRuntime):
            self.repository.upload_runtime(filepath)
