import mock
from baiji import s3
from baiji.test_s3 import TestAWSBase

class TestSync(TestAWSBase):
    def setUp(self):
        super(TestSync, self).setUp()

        # Files that are the same on both sides:
        self.create_random_file_at((self.tmp_dir, self.s3_test_location), 'foo/a.txt')
        self.create_random_file_at((self.tmp_dir, self.s3_test_location), 'foo/b.txt')
        self.create_random_file_at((self.tmp_dir, self.s3_test_location), 'foo/bar/c.txt')
        self.create_random_file_at((self.tmp_dir, self.s3_test_location), 'foo/bar/baz/d.txt')
        # Files that are different locally and remotely:
        self.create_random_file_at((self.tmp_dir,), 'foo/x.txt')
        self.create_random_file_at((self.s3_test_location,), 'foo/x.txt')
        self.create_random_file_at((self.tmp_dir,), 'foo/bar/x.txt')
        self.create_random_file_at((self.s3_test_location,), 'foo/bar/x.txt')
        # Files that are only local:
        self.create_random_file_at((self.tmp_dir,), 'foo/loc.txt')
        self.create_random_file_at((self.tmp_dir,), 'foo/bar/loc.txt')
        # Files that are only remote:
        self.create_random_file_at((self.s3_test_location,), 'foo/rem.txt')
        self.create_random_file_at((self.s3_test_location,), 'foo/bar/rem.txt')

        self.local_dir_to_sync = s3.path.join(self.tmp_dir, 'foo')
        self.remote_dir_to_sync = s3.path.join(self.s3_test_location, 'foo')

        self.expected_local_contents = s3.ls(self.local_dir_to_sync)
        self.expected_remote_contents = [x.replace(self.s3_path+'foo/', '') for x in s3.ls(self.remote_dir_to_sync)]

    def create_random_file_at(self, bases, path):
        from baiji.util.testing import random_data
        data = random_data()
        for base in bases:
            with s3.open(s3.path.join(base, path), 'w') as f:
                f.write(data)

    def assertContentsAre(self, expected_contents):
        self.assertSetEqual(set(s3.ls(self.local_dir_to_sync)), set(expected_contents))
        self.assertSetEqual(set([x.replace(self.s3_path+'foo/', '') for x in s3.ls(self.remote_dir_to_sync)]), set(expected_contents))
        # TODO files are equal:


    def test_sync_local_to_remote(self):
        s3.sync(self.local_dir_to_sync, self.remote_dir_to_sync)
        self.assertContentsAre(self.expected_local_contents)

    def test_sync_remote_to_local(self):
        s3.sync(self.remote_dir_to_sync, self.local_dir_to_sync)
        self.assertContentsAre(self.expected_remote_contents)

    @mock.patch('baiji.s3.S3Connection.cp')
    @mock.patch('baiji.s3.S3Connection.rm')
    def test_sync_file_same(self, rm, cp):
        # In these tests, we want to check that rm and cp are invoked only
        # when they should be, so we mock out cp and rm on a new instance of
        # S3Connection. (It seems difficult to use mock.patch on module
        # methods.)
        #
        # We also need s3.path.join but it's defined on the module, not on
        # instances of S3Connection.
        from baiji.s3 import S3Connection

        s3_with_mocks = S3Connection()

        s3_with_mocks.sync_file(
            s3.path.join(self.local_dir_to_sync, 'a.txt'),
            s3.path.join(self.remote_dir_to_sync, 'a.txt')
        )

        self.assertFalse(cp.called)
        self.assertFalse(rm.called)

    @mock.patch('baiji.s3.S3Connection.cp')
    @mock.patch('baiji.s3.S3Connection.rm')
    def test_sync_file_only_src(self, rm, cp):
        from baiji.s3 import S3Connection

        s3_with_mocks = S3Connection()

        s3_with_mocks.sync_file(
            s3.path.join(self.local_dir_to_sync, 'loc.txt'),
            s3.path.join(self.remote_dir_to_sync, 'loc.txt')
        )

        cp.assert_called_once_with(
            s3.path.join(self.local_dir_to_sync, 'loc.txt'),
            s3.path.join(self.remote_dir_to_sync, 'loc.txt'),
            force=False,
            progress=False,
            policy=None,
            encoding=None,
            encrypt=True,
            guess_content_type=False
        )
        self.assertFalse(rm.called)

    @mock.patch('baiji.s3.S3Connection.cp')
    @mock.patch('baiji.s3.S3Connection.rm')
    def test_sync_file_only_dst(self, rm, cp):
        from baiji.s3 import S3Connection

        s3_with_mocks = S3Connection()

        # Test with delete=True and delete=False.

        s3_with_mocks.sync_file(
            s3.path.join(self.local_dir_to_sync, 'rem.txt'),
            s3.path.join(self.remote_dir_to_sync, 'rem.txt'),
            delete=True
        )

        self.assertFalse(cp.called)
        rm.assert_called_once_with(
            s3.path.join(self.remote_dir_to_sync, 'rem.txt')
        )

        rm.reset_mock()

        with self.assertRaises(s3.KeyNotFound):
            s3_with_mocks.sync_file(
                s3.path.join(self.local_dir_to_sync, 'rem.txt'),
                s3.path.join(self.remote_dir_to_sync, 'rem.txt'),
                delete=False
            )

        self.assertFalse(cp.called)
        self.assertFalse(rm.called)

    @mock.patch('baiji.s3.S3Connection.cp')
    @mock.patch('baiji.s3.S3Connection.rm')
    def test_sync_file_exists_but_outdated(self, rm, cp):
        from baiji.s3 import S3Connection

        s3_with_mocks = S3Connection()

        # Test with update=True and update=False.

        s3_with_mocks.sync_file(
            s3.path.join(self.local_dir_to_sync, 'x.txt'),
            s3.path.join(self.remote_dir_to_sync, 'x.txt'),
            update=True
        )

        cp.assert_called_once_with(
            s3.path.join(self.local_dir_to_sync, 'x.txt'),
            s3.path.join(self.remote_dir_to_sync, 'x.txt'),
            force=True,
            progress=False,
            policy=None,
            encoding=None,
            encrypt=True,
            guess_content_type=False
        )
        self.assertFalse(rm.called)

        cp.reset_mock()

        s3_with_mocks.sync_file(
            s3.path.join(self.local_dir_to_sync, 'x.txt'),
            s3.path.join(self.remote_dir_to_sync, 'x.txt'),
            update=False
        )

        self.assertFalse(cp.called)
        self.assertFalse(rm.called)
