import hashlib
import mock
from ubackup.tests import TestCase
from ubackup.utils import filesizeformat
from ubackup.utils import gzip_stream
from ubackup.utils import md5_stream
from ubackup.utils import stream_shell
from ubackup.utils import crypt_stream
from ubackup.utils import decrypt_stream
from ubackup.utils import memoized


class UtilsTest(TestCase):

    def test_filesizeformat(self):
        size = filesizeformat(1024)
        self.assertEqual(size, '1.00KB')

        size = filesizeformat(0)
        self.assertEqual(size, '0B')

    def test_gzip_stream(self):
        gzip_stream(stream_shell(
            cmd='echo test')).read()

    def test_md5_stream(self):
        md5_hash = md5_stream(stream_shell(
            cmd='echo test'))

        m = hashlib.md5()
        m.update('test\n')
        self.assertEqual(m.hexdigest(), md5_hash)

    def test_stream_shell(self):
        stream = stream_shell(cmd='echo test')
        self.assertEqual(stream.read(), "test\n")

    def test_crypt(self):
        stream = stream_shell(cmd='echo test')
        crypted_stream = crypt_stream(stream, 'foo')
        decrypted_stream = decrypt_stream(crypted_stream, 'foo')
        self.assertEqual(decrypted_stream.read(), "test\n")

    def test_memoized(self):
        mock_fn = mock.Mock()

        @memoized
        def test():
            mock_fn()

        for i in range(2):
            test()
        self.assertEqual(mock_fn.call_count, 1)
