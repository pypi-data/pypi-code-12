import mock
from StringIO import StringIO
from ubackup.tests import TestCase
from ubackup.bucket.dropbox import DropboxBucket
from ubackup.bucket.local import LocalBucket
from ubackup.bucket.base import Bucket


class DropboxRequest(object):
    def json(*args, **kwargs):
        return {}

    @property
    def status_code(*args, **kwargs):
        return 200


class BucketTest(TestCase):

    def test_bucket_base(self):
        bucket = Bucket()
        self.assertRaises(NotImplementedError, bucket.pull, 'filename')
        self.assertRaises(NotImplementedError, bucket.push, StringIO('stream'), 'filename')
        self.assertRaises(NotImplementedError, bucket.exists, 'filename')

    @mock.patch('requests.request')
    def test_dropbox_bucket(self, mock_method):
        mock_method.return_value = DropboxRequest()

        # Test pull/push
        bucket = DropboxBucket(token="coucou")
        bucket.pull('filename')
        bucket.pull('filename', rev=1)
        bucket.push(StringIO('test'), 'filename')
        self.assertFalse(bucket.exists('foo'))

        # Test revisions
        class DropboxRequest2(object):
            def json(*args, **kwargs):
                return [{
                    'rev': 1,
                    'bytes': 1000,
                    'modified': 'Fri, 16 Sep 2011 01:01:25 +0000'
                }, {
                    'rev': 2,
                    'bytes': 1000,
                    'modified': 'Fri, 16 Sep 2011 01:01:25 +0000'
                }]

            @property
            def status_code(*args, **kwargs):
                return 200
        mock_method.return_value = DropboxRequest2()
        self.assertEqual(len(bucket.get_revisions('filename')), 2)

        self.assertTrue(mock_method.called)

    def test_local_bucket(self):
        # Test versioning
        bucket = LocalBucket(path=self.tmp_dir, files_limit=2)
        bucket.push(StringIO('test'), 'foo', versioning=True)
        bucket.push(StringIO('test'), 'foo', versioning=True)
        self.assertEqual(len(bucket.get_revisions('foo')), 2)

        # Test files limit
        bucket.push(StringIO('test'), 'foo', versioning=True)
        bucket.push(StringIO('test'), 'foo', versioning=True)
        self.assertEqual(len(bucket.get_revisions('foo')), 2)

        # Test pull
        self.assertEqual(bucket.pull('foo').read(), 'test')

        # Test pull with rev
        rev = bucket.get_revisions('foo')[-1]['id']
        self.assertEqual(bucket.pull('foo', rev=rev).read(), 'test')

        # Test exists
        self.assertTrue(bucket.exists('foo'))
        self.assertFalse(bucket.exists('bar'))
