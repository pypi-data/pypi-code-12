import os
import shutil
import unittest
import mock
from baiji import s3
from baiji.util.testing import create_random_temporary_file
from baiji.util import tempfile

TEST_BUCKET = 'baiji-test'

class TestAWSBase(unittest.TestCase):
    """
    Provides framework for testing.
    Among others:
    self.local_file                         # A local file that exists
    self.tmp_dir                            # A local temporary directory (that exists)
    self.existing_remote_file               # A remote file that exists
    self.s3_path                            # A remote temporary "directory" (N.B. it does not "exist" a priori)
                                            # Note: this should be accessed with self.remote_file(filename) for full s3 url
    self.retriable_s3_call(call, retries=3) # For testing methods that may fail due to bad connections
    """
    def setUp(self):
        self.bucket = TEST_BUCKET
        self.s3_test_location = s3.path.gettmpdir(bucket=self.bucket)
        loc = s3.path.parse(self.s3_test_location)
        self.s3_path = loc.path

        b = s3.S3Connection()._bucket(self.bucket) # pylint: disable=protected-access
        for key in b.list(self.s3_path[1:]):
            b.delete_key(key)
        self.assertEqual(len([x for x in b.list(self.s3_path[1:])]), 0) # just make sure we're starting with a clean slate

        self.tmp_dir = tempfile.mkdtemp('bodylabs-test')
        self.local_file = create_random_temporary_file()


    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        os.remove(self.local_file)
        b = s3.S3Connection()._bucket(self.bucket) # pylint: disable=protected-access
        for key in b.list(self.s3_path[1:]):
            b.delete_key(key)
        self.assertEqual(len([x for x in b.list(self.s3_path[1:])]), 0)

    def retriable_s3_call(self, call, retries=3):
        from boto.exception import S3ResponseError
        import time
        try:
            return call()
        except S3ResponseError:
            if retries > 0:
                time.sleep(0.1)
                return self.retriable_s3_call(call, retries=retries-1)
            else:
                raise

    def assert_s3_exists(self, path):
        self.assertTrue(self.retriable_s3_call(lambda: s3.exists(path)))

    def assert_s3_does_not_exist(self, path):
        self.assertFalse(self.retriable_s3_call(lambda: s3.exists(path)))

    def assert_is_public(self, s3_url, is_public):
        from urlparse import urlparse
        url = urlparse(s3_url)
        acl = self.retriable_s3_call(lambda: s3.S3Connection()._bucket(url.netloc).get_acl(url.path[1:])) # pylint: disable=protected-access
        actual_is_public = False
        for grant in acl.acl.grants:
            if grant.permission == 'READ':
                if grant.uri == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    actual_is_public = True
        self.assertEquals(actual_is_public, is_public)

    def remote_file(self, path):
        return s3.path.join(self.s3_test_location, path)

    @property
    def existing_remote_file(self):
        '''
        In some tests it is convenient to have a file already on s3;
        in some others we need it not to be there (e.g. for clarity in the s3.ls test)
        '''
        uri = self.remote_file("FOO/A_preexisting_file.md")
        if not s3.exists(uri):
            s3.cp(self.local_file, uri)
        return uri

class TestS3Exists(TestAWSBase):

    @mock.patch('baiji.s3.S3Connection._lookup')
    def test_s3_exists_retries_if_not_found_at_first(self, mock_lookup):
        import warnings
        from baiji.exceptions import EventualConsistencyWarning
        mock_key = "all_we_care_is_that_it's not None"
        mock_lookup.side_effect = [None, None, mock_key]
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            self.assertTrue(s3.exists('s3://foo'))
            # Verify the warning was triggered
            self.assertEqual(len(w), 1)
            self.assertIs(w[-1].category, EventualConsistencyWarning)
            self.assertEqual(str(w[-1].message), "S3 is behaving in an eventually consistent way in s3.exists(s3://foo) -- it took 3 attempts to locate the key")
        self.assertEqual(mock_lookup.call_count, 3)

    @mock.patch('baiji.s3.S3Connection._lookup')
    def test_s3_exists_does_not_retry_if_found_immidiately(self, mock_lookup):
        mock_key = "all_we_care_is_that_it's not None"
        mock_lookup.return_value = mock_key
        self.assertTrue(s3.exists('s3://foo'))
        self.assertEqual(mock_lookup.call_count, 1)

    @mock.patch('baiji.s3.S3Connection._lookup')
    def test_s3_exists_return_false_if_the_file_never_shows_up(self, mock_lookup):
        mock_lookup.return_value = None
        self.assertFalse(s3.exists('s3://foo'))
        self.assertEqual(mock_lookup.call_count, 3)


class TestS3(TestAWSBase):

    def test_s3_cp_local_to_local(self):
        s3.cp(self.local_file, os.path.join(self.tmp_dir, 'TEST.foo'))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, 'TEST.foo')))

    def test_s3_cp_local_to_local_file_in_dir_that_needs_making(self):
        s3.cp(self.local_file, os.path.join(self.tmp_dir, 'FOO', 'TEST.foo'))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, 'FOO', 'TEST.foo')))

    def test_s3_cp_local_to_local_dir(self):
        s3.cp(self.local_file, self.tmp_dir)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, os.path.basename(self.local_file))))

    def test_s3_cp_upload(self):
        s3.cp(self.local_file, self.remote_file("FOO/NAMED.md"))
        self.assert_s3_exists(self.remote_file("FOO/NAMED.md"))

    def test_s3_cp_download(self):
        s3.cp(self.existing_remote_file, os.path.join(self.tmp_dir, 'DL', 'TEST.foo'))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, 'DL', 'TEST.foo')))
        s3.cp(self.existing_remote_file, os.path.join(self.tmp_dir, 'DL'))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, 'DL', s3.path.basename(self.existing_remote_file))))

    @mock.patch('baiji.s3.S3CopyOperation.ensure_integrity')
    def test_s3_cp_download_corrupted_recover_in_one_retry(self, ensure_integrity_mock):
        from baiji.s3 import get_transient_error_class
        ensure_integrity_mock.side_effect = [get_transient_error_class()('etag does not match'), None]
        s3.cp(self.existing_remote_file, self.tmp_dir, force=True)

    @mock.patch('baiji.s3.S3CopyOperation.ensure_integrity')
    def test_s3_cp_download_lookup_recover_in_one_retry(self, ensure_integrity_mock):
        from baiji.exceptions import KeyNotFound
        ensure_integrity_mock.side_effect = [KeyNotFound('key not found'), None]
        s3.cp(self.existing_remote_file, self.tmp_dir, force=True)

    @mock.patch('boto.s3.key.Key.get_contents_to_file')
    def test_downloads_from_s3_are_atomic_under_truncation(self, download_mock):
        from baiji.s3 import get_transient_error_class
        def write_fake_truncated_file(fp, **kwargs): # just capturing whatever is thrown at us: pylint: disable=unused-argument
            fp.write("12345")
        download_mock.side_effect = write_fake_truncated_file
        # Now when the call to download the file is made, the etags won't match
        with self.assertRaises(get_transient_error_class()):
            s3.cp(self.existing_remote_file, os.path.join(self.tmp_dir, 'truncated.foo'), validate=True)
        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, 'truncated.foo')))

    @mock.patch('baiji.s3.S3CopyOperation.ensure_integrity')
    def test_downloads_from_s3_are_atomic_under_exceptions(self, download_mock):
        download_mock.side_effect = ValueError()
        # Now when the call to download the file is made, an exception will be thrown.
        # ideally, we'd throw it "in" boto via a mock, but we really want to test that
        # the file doesn't get written, so let's go ahead and let boto do the download
        # and then throw the exception in the validation
        with self.assertRaises(ValueError):
            s3.cp(self.existing_remote_file, os.path.join(self.tmp_dir, 'erroneous.foo'), validate=True)
        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, 'erroneous.foo')))

    @mock.patch('baiji.s3.S3CopyOperation.ensure_integrity')
    def test_s3_cp_download_corrupted_raise_transient_error_after_retried_once(self, ensure_integrity_mock):

        from baiji.s3 import get_transient_error_class

        ensure_integrity_mock.side_effect = get_transient_error_class()('etag does not match')

        with self.assertRaises(get_transient_error_class()):
            s3.cp(self.existing_remote_file, self.tmp_dir, force=True)

    def test_s3_cp_in_s3(self):
        s3.cp(self.existing_remote_file, self.remote_file("COPY/NAMED.md"))
        self.assert_s3_exists(self.remote_file("COPY/NAMED.md"))

    def test_s3_cp_overwrite_errors_unless_force(self):
        s3.cp(self.local_file, os.path.join(self.tmp_dir, os.path.basename(self.local_file)))
        # local to local
        with self.assertRaises(s3.KeyExists):
            s3.cp(self.local_file, os.path.join(self.tmp_dir, os.path.basename(self.local_file)))
        with self.assertRaises(s3.KeyExists):
            s3.cp(self.local_file, self.tmp_dir)
        s3.cp(self.local_file, os.path.join(self.tmp_dir, os.path.basename(self.local_file)), force=True)
        s3.cp(self.local_file, self.tmp_dir, force=True)
        # local to remote
        with self.assertRaises(s3.KeyExists):
            s3.cp(self.local_file, self.existing_remote_file)
        # remote to local
        with self.assertRaises(s3.KeyExists):
            s3.cp(self.existing_remote_file, self.local_file)
        # remote to remote
        with self.assertRaises(s3.KeyExists):
            s3.cp(self.existing_remote_file, self.existing_remote_file)

    def test_s3_cp_errors_if_source_is_missing(self):
        # remote
        with self.assertRaisesRegexp(s3.KeyNotFound, "Error copying"):
            s3.cp(self.remote_file("definitely_not_there.foo"), self.tmp_dir)
        # local
        with self.assertRaisesRegexp(s3.KeyNotFound, "Error copying"):
            s3.cp(os.path.join(self.tmp_dir, "definitely_not_there.foo"), self.tmp_dir)


    def test_s3_cp_skip_existing_files_without_raise_exceptions(self):
        import warnings
        s3.cp(self.local_file, os.path.join(self.tmp_dir, os.path.basename(self.local_file)))
        with self.assertRaises(s3.KeyExists):
            s3.cp(self.local_file, os.path.join(self.tmp_dir, os.path.basename(self.local_file)))
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            s3.cp(self.local_file, os.path.join(self.tmp_dir, os.path.basename(self.local_file)), skip=True)
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "Skipping" in str(w[-1].message)

    def test_s3_cp_errors_raised_by_missing_source_file(self):
        self.assertRaises(s3.KeyNotFound, s3.cp, os.path.join(self.tmp_dir, 'MISSING.file'), self.tmp_dir)
        self.assertRaises(s3.KeyNotFound, s3.cp, self.remote_file("MISSING.file"), self.tmp_dir)

    def test_s3_cp_errors_raised_by_unimplemented_source_scheme(self):
        self.assertRaises(s3.InvalidSchemeException, s3.cp, 'http://www.google.com/', self.tmp_dir)
        self.assertRaises(s3.InvalidSchemeException, s3.cp, self.local_file, 'http://www.google.com/')

    def test_s3_cp_relative_paths(self):
        s3.cp(self.local_file, 'test-DELETEME', force=True)
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test-DELETEME')))
        s3.cp('test-DELETEME', self.remote_file("local"), force=True)
        self.assert_s3_exists(self.remote_file("local"))
        s3.rm('test-DELETEME')
        self.assertFalse(os.path.exists(os.path.join(os.getcwd(), 'test-DELETEME')))

    def test_s3_cp_HOME_paths(self):
        s3.cp(self.local_file, '~/test-DELETEME', force=True)
        self.assertTrue(os.path.exists(os.path.expanduser('~/test-DELETEME')))
        s3.cp('~/test-DELETEME', self.remote_file("local"), force=True)
        self.assert_s3_exists(self.remote_file("local"))
        s3.rm('~/test-DELETEME')
        self.assertFalse(os.path.exists(os.path.expanduser('~/test-DELETEME')))

    def test_s3_cp_policy(self):
        # test policy for file -> s3
        s3.cp(self.local_file, self.remote_file("public.md"), policy='public-read')
        self.assert_is_public(self.remote_file("public.md"), is_public=True)
        s3.cp(self.local_file, self.remote_file("private.md"), policy='bucket-owner-read')
        self.assert_is_public(self.remote_file("private.md"), is_public=False)

        # test policy for s3 -> s3
        s3.cp(self.remote_file("private.md"), self.remote_file("made_public_on_copy.md"), policy='public-read')
        self.assert_is_public(self.remote_file("made_public_on_copy.md"), is_public=True)

        s3.cp(self.remote_file("private.md"), self.remote_file("left_private_on_copy.md"))
        self.assert_is_public(self.remote_file("left_private_on_copy.md"), is_public=False)

        with self.assertRaises(ValueError):
            s3.cp(self.remote_file("private.md"), os.path.join(self.tmp_dir, 'NoCanDo.txt'), policy='public-read')

    def test_s3_cp_preserve_acl(self):
        s3.cp(self.local_file, self.remote_file("also_public.md"), policy='public-read')
        s3.cp(self.remote_file("also_public.md"), self.remote_file("still_public.md"), preserve_acl=True)
        self.assert_is_public(self.remote_file("also_public.md"), is_public=True)
        s3.cp(self.remote_file("also_public.md"), self.remote_file("no_longer_public.md"))
        self.assert_is_public(self.remote_file("no_longer_public.md"), is_public=False)

        with self.assertRaises(ValueError):
            s3.cp(self.remote_file("also_public.md"), os.path.join(self.tmp_dir, 'NoCanDo.txt'), preserve_acl=True)

    def test_s3_cp_content_encoding(self):
        s3.cp(self.local_file, self.remote_file("encoded.md"), encoding='gzip')
        self.assertEqual(s3.info(self.remote_file("encoded.md"))['content_encoding'], 'gzip')
        s3.cp(self.local_file, self.remote_file("notencoded.md")) # just make sure gzip isn't the default ;)
        self.assertNotEqual(s3.info(self.remote_file("notencoded.md"))['content_encoding'], 'gzip')
        s3.cp(self.remote_file("encoded.md"), self.remote_file("still_encoded.md"))
        self.assertEqual(s3.info(self.remote_file("still_encoded.md"))['content_encoding'], 'gzip')
        s3.cp(self.remote_file("notencoded.md"), self.remote_file("now_encoded.md"), encoding='gzip')
        self.assertEqual(s3.info(self.remote_file("now_encoded.md"))['content_encoding'], 'gzip')

    def test_s3_cp_content_type(self):
        s3.cp(self.local_file, self.remote_file("typed.md"), content_type='text/html')
        self.assertEqual(s3.info(self.remote_file("typed.md"))['content_type'], 'text/html')

        s3.cp(self.local_file, self.remote_file("nottyped.md")) # default is
        self.assertEqual(s3.info(self.remote_file("nottyped.md"))['content_type'], 'application/octet-stream')

        s3.cp(self.remote_file("typed.md"), self.remote_file("still_typed.md"))
        self.assertEqual(s3.info(self.remote_file("still_typed.md"))['content_type'], 'text/html')
        s3.cp(self.remote_file("nottyped.md"), self.remote_file("now_typed.md"), content_type='text/html')
        self.assertEqual(s3.info(self.remote_file("now_typed.md"))['content_type'], 'text/html')

    def test_s3_cp_gzip(self):
        s3.cp(self.local_file, self.remote_file("big.md"))
        s3.cp(self.local_file, self.remote_file("small.md"), gzip=True)
        self.assertNotEqual(s3.info(self.remote_file("big.md"))['content_encoding'], 'gzip')
        self.assertEqual(s3.info(self.remote_file("small.md"))['content_encoding'], 'gzip')
        self.assertLess(s3.info(self.remote_file("small.md"))['size'], s3.info(self.remote_file("big.md"))['size'])

    def test_s3_cp_trailing_slashes_in_dst(self):
        # https://bitbucket.org/bodylabs/core/issue/25
        s3.cp(self.local_file, os.path.join(self.tmp_dir, 'FOO2', ''))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, 'FOO2', os.path.basename(self.local_file))))
        s3.cp(self.local_file, self.remote_file("FOO2/"))
        self.assert_s3_exists(self.remote_file("FOO2/%s" % os.path.basename(self.local_file)))
        s3.cp(self.existing_remote_file, os.path.join(self.tmp_dir, 'DL2', ''))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, 'DL2', s3.path.basename(self.existing_remote_file))))

    def test_s3_rm(self):
        for path in [os.path.join(self.tmp_dir, 'foo'), self.remote_file("foo")]:
            s3.cp(self.local_file, path)
            self.assert_s3_exists(path)
            s3.rm(path)
            self.assert_s3_does_not_exist(path)
            with self.assertRaises(s3.KeyNotFound):
                s3.rm(path)
        self.assertRaises(s3.InvalidSchemeException, s3.rm, ("http://example.com/foo"))

    def test_s3_ls(self):
        files = ["foo", "bar.baz", "quack/foo.foo"]
        for f in files:
            s3.cp(self.local_file, self.remote_file(f))
        self.assertEqual(set(s3.ls(self.s3_test_location)), set(map(lambda x: self.s3_path+x, files)))
        self.assertEqual(set(s3.ls(self.s3_test_location, return_full_urls=True)), set([self.remote_file(x) for x in files]))
        self.assertEqual(set(s3.ls(self.s3_test_location, shallow=True)), set([self.s3_path+x for x in ['foo', 'bar.baz', 'quack/']]))

    def test_s3_md5(self):
        s3.cp(self.local_file, self.remote_file("file_to_md5"))
        from baiji.util.md5 import md5_for_file
        self.assertEqual(s3.md5(self.remote_file("file_to_md5")), md5_for_file(self.local_file))

    def test_strings(self):
        s = "TEST STRING"
        s3.put_string(self.remote_file("string"), s)
        self.assertEqual(s3.get_string(self.remote_file("string")), s)

    # TODO: Test with local paths. Instead of having a single local file
    # we can have a local subdirectory that is cleaned up on teardown.
    def test_s3_glob_match_single_wildcard(self):
        files = ['a.obj', 'b.obj', 'a.ply', 'a.object']
        for f in files:
            s3.cp(self.local_file, self.remote_file(f))
        glob_results = list(s3.glob(self.s3_test_location, '*.obj'))
        self.assertEqual(2, len(glob_results))
        self.assertEqual(set(glob_results), set([self.remote_file(f) for f in ['a.obj', 'b.obj']]))

    def test_s3_glob_match_multiple_wildcards(self):
        files = ['body_1_pose_T.obj', 'body_1_pose_Fun.obj', 'body_2_pose_T.obj', 'body_02_pose_T.obj']
        for f in files:
            s3.cp(self.local_file, self.remote_file(f))
        glob_results = list(s3.glob(self.s3_test_location, 'body_?_pose_*.obj'))
        self.assertEqual(3, len(glob_results))
        self.assertEqual(
            set(glob_results),
            set([self.remote_file(f) for f in ['body_1_pose_T.obj', 'body_1_pose_Fun.obj', 'body_2_pose_T.obj']])
        )

    def test_s3_glob_exclude(self):
        files = ['pose_T.obj', 'pose_A.obj', 'pose_Scan.obj']
        for f in files:
            s3.cp(self.local_file, self.remote_file(f))
        glob_results = list(s3.glob(self.s3_test_location, 'pose_[!T].obj'))
        self.assertEqual(1, len(glob_results))
        self.assertEqual(set(glob_results), set([self.remote_file('pose_A.obj')]))

    def test_s3_with_double_slashes_in_key(self):
        '''
        boto has a nasty behavior by default where it collapses `//` to `/` in keys
        '''
        s3.cp(self.local_file, self.remote_file('double//slashes//bork//boto.foo'))
        self.assertEqual([self.remote_file('double//slashes//bork//boto.foo')], list(s3.ls(self.remote_file(''), return_full_urls=True)))

    def test_s3_path_isdir(self):
        existing_remote_dir = os.path.dirname(self.existing_remote_file)
        #case: local dir, exists
        self.assertTrue(s3.path.isdir(self.tmp_dir))
        #case: local dir, does not exist
        self.assertFalse(s3.path.isdir(os.path.join(self.tmp_dir, 'does_not_exist')))
        #case: local dir, exists but is file
        self.assertFalse(s3.path.isdir(self.local_file))
        #case: remote dir, exists
        self.assertTrue(s3.path.isdir(existing_remote_dir))
        #case: remote dir, does not exist
        self.assertFalse(s3.path.isdir(self.remote_file('does_not_exist')))
        #case: remote dir, exists but is file
        self.assertFalse(s3.path.isdir(self.existing_remote_file))

    def test_s3_path_isfile(self):
        existing_remote_dir = os.path.dirname(self.existing_remote_file)
        #case: local file, exists
        self.assertTrue(s3.path.isfile(self.local_file))
        #case: local file, does not exist
        self.assertFalse(s3.path.isfile(os.path.join(self.tmp_dir, 'does_not_exist')))
        #case: local file, exists but is directory
        self.assertFalse(s3.path.isfile(self.tmp_dir))
        #case: remote file, exists
        self.assertTrue(s3.path.isfile(self.existing_remote_file))
        #case: remote file, does not exist
        self.assertFalse(s3.path.isfile(self.remote_file('does_not_exist')))
        #case: remote file, "exists" but is directory (so it actually doesn't exist but could return false positive)
        self.assertFalse(s3.path.isfile(existing_remote_dir))


class TestEncryption(TestAWSBase):
    def test_encrypt_in_place(self):
        s3.cp(self.local_file, self.remote_file("to_encrypt.txt"), encrypt=False) # just make sure there's something to copy
        self.assertFalse(s3.info(self.remote_file("to_encrypt.txt"))['encrypted'])
        s3.encrypt_at_rest(self.remote_file("to_encrypt.txt"))
        self.assertTrue(s3.info(self.remote_file("to_encrypt.txt"))['encrypted'])

    def test_upload(self):
        s3.cp(self.local_file, self.remote_file("unencrypted.txt"), encrypt=False)
        self.assertFalse(s3.info(self.remote_file("unencrypted.txt"))['encrypted'])
        s3.cp(self.local_file, self.remote_file("encrypted.txt")) # default now to encrypt
        self.assertTrue(s3.info(self.remote_file("encrypted.txt"))['encrypted'])

    def test_copy(self):
        s3.cp(self.local_file, self.remote_file("unencrypted.txt"), encrypt=False) # just make sure there's something to copy
        self.assertFalse(s3.info(self.remote_file("unencrypted.txt"))['encrypted'])
        s3.cp(self.remote_file("unencrypted.txt"), self.remote_file("encrypted.txt"))
        self.assertTrue(s3.info(self.remote_file("encrypted.txt"))['encrypted'])


class TestS3ConnectionPersistence(unittest.TestCase):
    def test_connection_is_cached(self):
        # pylint: disable=protected-access
        # Using a cached connection is 2 orders of magnitude faster than
        # creating a new connection instance.

        connection = s3.S3Connection()

        # Creating the object does not a connection make
        self.assertFalse(connection._connected)

        # connection.conn is created on first use and contains the connection object
        # Whenever s3 operations are performed, a call is made to this object.
        # In order to eliminate the middleman, we make the call directly in this test.
        established_connection_id = id(connection.conn)

        # Now it should be registered that the connection is made and cached.
        self.assertTrue(connection._connected)

        # And connection.conn should not change when accessed again.
        connection_id_on_second_call = id(connection.conn)
        self.assertEquals(established_connection_id, connection_id_on_second_call)
