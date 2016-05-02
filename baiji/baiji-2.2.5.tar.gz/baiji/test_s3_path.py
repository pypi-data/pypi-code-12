import unittest
import os
from baiji import s3

class TestS3Path(unittest.TestCase):

    def test_s3_parse(self):
        def test(s, expect, on_windows=None):
            if on_windows and os.name == 'nt':
                expect = expect[:2] + (on_windows,)
            o = s3.path.parse(s)
            for ii in range(3):
                self.assertEqual(o[ii], expect[ii])

        test('s3://foo/path/to/bar', ('s3', 'foo', '/path/to/bar'))
        test('s3://xx', ('s3', 'xx', ''))
        test('s3://xx/', ('s3', 'xx', '/'))
        self.assertRaises(ValueError, s3.path.parse, 's3:///path/to/bar')
        test('file:///path/to/blah', ('file', '', '/path/to/blah'), on_windows=r'C:\path\to\blah')
        test('/path/to/blah', ('file', '', '/path/to/blah'), on_windows=r'C:\path\to\blah')
        test('path/to/blah', ('file', '', os.path.abspath('./path/to/blah')))
        test('~/path/to/blah', ('file', '', os.path.abspath(os.path.expanduser('~/path/to/blah'))))
        test('', ('file', '', os.path.abspath('.')))

        self.assertTrue(s3.path.islocal('/path/to/bar'))
        self.assertFalse(s3.path.islocal('s3://foo/path/to/bar'))
        self.assertFalse(s3.path.isremote('/path/to/bar'))
        self.assertTrue(s3.path.isremote('s3://foo/path/to/bar'))

        self.assertEqual(s3.path.join('s3://foo/path', 'to/bar'), 's3://foo/path/to/bar')
        if os.name == 'nt':
            self.assertEqual(s3.path.join('/foo/path', 'to/bar'), r'C:\foo\path\to\bar')
        else:
            self.assertEqual(s3.path.join('/foo/path', 'to/bar'), '/foo/path/to/bar')

        self.assertEqual(s3.path.basename('file:///foo/path/to/bar.baz'), 'bar.baz')
        self.assertEqual(s3.path.basename('s3://bucket/foo/path/to/bar.baz'), 'bar.baz')

        test('C:\\path\\of\\quux', ('file', '', 'C:\\path\\of\\quux'))
        test('file:///C:\\path\\of\\quux', ('file', '', 'C:\\path\\of\\quux'))

        with self.assertRaises(ValueError):
            s3.path.parse('file:///foo;bar')

        # Make sure it preserves trailing slashes
        test('path/to/blah/', ('file', '', os.path.join(os.path.abspath('./path/to/blah'), '')))
        test('s3://foo/path/to/blah/', ('s3', 'foo', '/path/to/blah/'))
