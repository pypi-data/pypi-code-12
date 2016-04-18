import uuid
import os
import mock
from baiji import s3
from baiji.test_s3 import TestAWSBase

class TestCachedFile(TestAWSBase):
    def setUp(self):
        super(TestCachedFile, self).setUp()
        s3.cp(self.local_file, self.remote_file("openable"))
        with open(self.local_file, 'rb') as f:
            self.truth = f.read()

    def test_s3_open_read_remote_file_with_context_manager(self):
        self.assert_s3_exists(self.remote_file("openable"))

        with s3.open(self.remote_file("openable"), 'r') as f:
            tempname = f.name
            self.assertEqual(self.truth, f.read())

        self.assertFalse(os.path.exists(tempname))

    def test_s3_open_read_remote_file_without_context_manager(self):
        self.assert_s3_exists(self.remote_file("openable"))

        f = s3.open(self.remote_file("openable"), 'r')
        tempname = f.name
        self.assertEqual(self.truth, f.read())
        f.close()

        self.assertFalse(os.path.exists(tempname))

    def test_s3_open_read_local_file_with_context_manager(self):
        self.assert_s3_exists(self.local_file)

        with s3.open(self.local_file, 'r') as f:
            self.assertEqual(self.truth, f.read())
            self.assertEqual(f.name, self.local_file)

    def test_s3_open_read_local_file_without_context_manager(self):
        self.assert_s3_exists(self.local_file)

        f = s3.open(self.local_file, 'r')
        self.assertEqual(self.truth, f.read())
        self.assertEqual(f.name, self.local_file)
        f.close()

    def test_s3_open_write_remote_file_with_context_manager(self):
        remote_file_name = self.remote_file("write_test_1")
        local_file_name = os.path.join(self.tmp_dir, "write_test_1")
        self.assert_s3_does_not_exist(remote_file_name)

        with s3.open(remote_file_name, 'w') as f:
            tempname = f.name
            f.write(self.truth)

        self.assertFalse(os.path.exists(tempname))
        self.assert_s3_exists(remote_file_name)
        # download and confirm that it contains the correct contents
        s3.cp(remote_file_name, local_file_name)
        with open(local_file_name) as f:
            self.assertEqual(self.truth, f.read())

    def test_s3_open_write_local_file_creates_parent_dirs(self):
        local_file_name = os.path.join(self.tmp_dir, "subdir", "write_test_subdir")
        self.assert_s3_does_not_exist(local_file_name)
        self.assert_s3_does_not_exist(os.path.dirname(local_file_name))

        with s3.open(local_file_name, 'w') as f:
            f.write(self.truth)

        self.assert_s3_exists(local_file_name)
        self.assert_s3_exists(os.path.dirname(local_file_name))

    def test_s3_open_write_remote_file_without_context_manager(self):
        remote_file_name = self.remote_file("write_test_2")
        local_file_name = os.path.join(self.tmp_dir, "write_test_2")
        self.assert_s3_does_not_exist(remote_file_name)

        f = s3.open(remote_file_name, 'w')
        tempname = f.name
        f.write(self.truth)
        f.close()

        self.assertFalse(os.path.exists(tempname))
        self.assert_s3_exists(remote_file_name)
        # download and confirm that it contains the correct contents
        s3.cp(remote_file_name, local_file_name)
        with open(local_file_name) as f:
            self.assertEqual(self.truth, f.read())

    def test_s3_open_write_local_file_with_context_manager(self):
        local_file_name = os.path.join(self.tmp_dir, "write_test_local_1")
        self.assert_s3_does_not_exist(local_file_name)

        with s3.open(local_file_name, 'w') as f:
            self.assertEqual(f.name, local_file_name)
            f.write(self.truth)

        self.assert_s3_exists(local_file_name)
        # confirm that it contains the correct contents
        with open(local_file_name) as f:
            self.assertEqual(self.truth, f.read())

    def test_s3_open_write_local_file_without_context_manager(self):
        local_file_name = os.path.join(self.tmp_dir, "write_test_local_2")
        self.assert_s3_does_not_exist(local_file_name)

        f = s3.open(local_file_name, 'w')
        self.assertEqual(f.name, local_file_name)
        f.write(self.truth)
        f.close()

        self.assert_s3_exists(local_file_name)
        # confirm that it contains the correct contents
        with open(local_file_name) as f:
            self.assertEqual(self.truth, f.read())

    def test_s3_open_exclusive_write_remote_file_throws_error_for_existing_file(self):
        self.assert_s3_exists(self.remote_file("openable"))
        with self.assertRaises(s3.KeyExists):
            s3.open(self.remote_file("openable"), 'x')

    def test_s3_open_exclusive_write_local_file_throws_error_for_existing_file(self):
        self.assert_s3_exists(self.local_file)
        with self.assertRaises(s3.KeyExists):
            s3.open(self.local_file, 'x')

    def test_s3_open_exclusive_write_remote_file_throws_error_for_double_open(self):
        self.assert_s3_does_not_exist(self.remote_file("exclusive_write_test_3"))
        with s3.open(self.remote_file("exclusive_write_test_3"), 'x'):
            with self.assertRaises(s3.KeyExists):
                with s3.open(self.remote_file("exclusive_write_test_3"), 'x'):
                    pass

    def test_s3_open_exclusive_write_local_file_throws_error_for_double_open(self):
        local_file_name = os.path.join(self.tmp_dir, "exclusive_write_test_local_3")
        self.assert_s3_does_not_exist(local_file_name)
        with s3.open(local_file_name, 'x'):
            with self.assertRaises(s3.KeyExists):
                with s3.open(local_file_name, 'x'):
                    pass

    def test_s3_open_exclusive_write_remote_file_with_context_manager(self):
        remote_file_name = self.remote_file("exclusive_write_test_1")
        local_file_name = os.path.join(self.tmp_dir, "exclusive_write_test_1")
        self.assert_s3_does_not_exist(remote_file_name)

        with s3.open(remote_file_name, 'x') as f:
            self.assert_s3_exists(remote_file_name)
            tempname = f.name
            f.write(self.truth)

        self.assertFalse(os.path.exists(tempname))
        self.assert_s3_exists(remote_file_name)
        # download and confirm that it contains the correct contents
        s3.cp(remote_file_name, local_file_name)
        with open(local_file_name) as f:
            self.assertEqual(self.truth, f.read())

    def test_s3_open_exclusive_write_remote_file_without_context_manager(self):
        remote_file_name = self.remote_file("exclusive_write_test_2")
        local_file_name = os.path.join(self.tmp_dir, "exclusive_write_test_2")
        self.assert_s3_does_not_exist(remote_file_name)

        f = s3.open(remote_file_name, 'x')
        self.assert_s3_exists(remote_file_name)
        tempname = f.name
        f.write(self.truth)
        f.close()

        self.assertFalse(os.path.exists(tempname))
        self.assert_s3_exists(remote_file_name)
        # download and confirm that it contains the correct contents
        s3.cp(remote_file_name, local_file_name)
        with open(local_file_name) as f:
            self.assertEqual(self.truth, f.read())

    def test_s3_open_exclusive_write_local_file_with_context_manager(self):
        local_file_name = os.path.join(self.tmp_dir, "exclusive_write_test_local_1")
        self.assert_s3_does_not_exist(local_file_name)

        with s3.open(local_file_name, 'x') as f:
            self.assertEqual(f.name, local_file_name)
            f.write(self.truth)

        self.assert_s3_exists(local_file_name)
        # confirm that it contains the correct contents
        with open(local_file_name) as f:
            self.assertEqual(self.truth, f.read())

    def test_s3_open_exclusive_write_local_file_without_context_manager(self):
        local_file_name = os.path.join(self.tmp_dir, "exclusive_write_test_local_2")
        self.assert_s3_does_not_exist(local_file_name)

        f = s3.open(local_file_name, 'x')
        self.assertEqual(f.name, local_file_name)
        f.write(self.truth)
        f.close()

        self.assert_s3_exists(local_file_name)
        # confirm that it contains the correct contents
        with open(local_file_name) as f:
            self.assertEqual(self.truth, f.read())

    def test_s3_open_read_raises_error_for_nonexistent_remote_file(self):
        nonexistent_file = self.remote_file(str(uuid.uuid4()))
        self.assert_s3_does_not_exist(nonexistent_file)
        with self.assertRaises(s3.KeyNotFound):
            s3.open(nonexistent_file, 'r')

    def test_s3_open_write_does_not_raise_error_for_nonexistent_remote_file(self):
        nonexistent_file = self.remote_file(str(uuid.uuid4()))
        self.assert_s3_does_not_exist(nonexistent_file)
        with s3.open(nonexistent_file, 'w') as f:
            test_string = 'FOO!\n'
            f.write(test_string)
        self.assert_s3_exists(nonexistent_file)

    def test_s3_open_write_update_raises_error_for_nonexistent_remote_file(self):
        nonexistent_file = self.remote_file(str(uuid.uuid4()))
        self.assert_s3_does_not_exist(nonexistent_file)
        with self.assertRaises(NotImplementedError):
            s3.open(nonexistent_file, 'w+')

    def test_s3_open_exclusive_write_does_not_raise_error_for_nonexistent_remote_file(self):
        nonexistent_file = self.remote_file(str(uuid.uuid4()))
        self.assert_s3_does_not_exist(nonexistent_file)
        with s3.open(nonexistent_file, 'x') as f:
            test_string = 'FOO!\n'
            f.write(test_string)
        self.assert_s3_exists(nonexistent_file)

    def test_s3_open_read_raises_error_for_nonexistent_local_file(self):
        nonexistent_file = os.path.join(self.tmp_dir, "test_s3_open_read_raises_error_for_nonexistent_local_file")
        self.assert_s3_does_not_exist(nonexistent_file)
        with self.assertRaises(s3.KeyNotFound):
            s3.open(nonexistent_file, 'r')

    def test_s3_open_write_does_not_raise_error_for_nonexistent_local_file(self):
        nonexistent_file = os.path.join(self.tmp_dir, "test_s3_open_write_does_not_raise_error_for_nonexistent_local_file")
        self.assert_s3_does_not_exist(nonexistent_file)
        with s3.open(nonexistent_file, 'w') as f:
            test_string = 'FOO!\n'
            f.write(test_string)
        self.assert_s3_exists(nonexistent_file)

    def test_s3_open_write_update_does_not_raise_error_for_nonexistent_local_file(self):
        nonexistent_file = os.path.join(self.tmp_dir, "test_s3_open_write_update_does_not_raise_error_for_nonexistent_local_file")
        self.assert_s3_does_not_exist(nonexistent_file)
        with s3.open(nonexistent_file, 'w+') as f:
            test_string = 'FOO!\n'
            f.write(test_string)
            f.seek(0)
            self.assertEqual(test_string, f.read())
        self.assert_s3_exists(nonexistent_file)

    def test_s3_open_exclusive_write_does_not_raise_error_for_nonexistent_local_file(self):
        nonexistent_file = os.path.join(self.tmp_dir, "test_s3_open_exclusive_write_does_not_raise_error_for_nonexistent_local_file")
        self.assert_s3_does_not_exist(nonexistent_file)
        with s3.open(nonexistent_file, 'x') as f:
            test_string = 'FOO!\n'
            f.write(test_string)
        self.assert_s3_exists(nonexistent_file)

    def test_s3_open_local_underlying_error_raises_ioerror_with_errno_and_strerror(self):
        import errno
        with self.assertRaises(IOError) as ctx:
            s3.open(os.getcwd(), 'w')
        self.assertEquals(ctx.exception.errno, errno.EISDIR)
        self.assertIn('Is a directory:', ctx.exception.strerror)

    @mock.patch('baiji.s3.CachedFile.upload')
    def test_s3_open_write_calls_upload(self, upload):
        remote_file_name = self.remote_file("write_test_1")
        with s3.open(remote_file_name, 'w'):
            self.assertFalse(upload.called)
        self.assertTrue(upload.called)

    @mock.patch('baiji.s3.CachedFile.upload')
    def test_s3_open_write_does_not_upload_if_exception_raised(self, upload):
        remote_file_name = self.remote_file("write_test_1")
        try:
            with s3.open(remote_file_name, 'w'):
                raise AttributeError()
        except AttributeError:
            pass
        self.assertFalse(upload.called)

        # Sanity check
        with s3.open(remote_file_name, 'w'):
            pass
        self.assertTrue(upload.called)

    @mock.patch('baiji.s3.CachedFile.upload')
    def test_s3_open_read_does_not_call_upload(self, upload):
        self.assert_s3_exists(self.remote_file("openable"))
        with s3.open(self.remote_file("openable"), 'r'):
            pass
        self.assertFalse(upload.called)
