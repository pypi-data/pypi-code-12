import unittest
import uuid
from baiji import s3
from baiji.test_s3 import TEST_BUCKET

class TestS3TmpDir(unittest.TestCase):
    '''
    We test this separately since we use it in TestAWSBase.setUp()

    '''
    def setUp(self):
        self.s3_path = 'tmp/' + str(uuid.uuid4()) + '/'

    def tearDown(self):
        b = s3.S3Connection()._bucket(TEST_BUCKET) # pylint: disable=protected-access
        for key in b.list(self.s3_path[0:-1]):
            b.delete_key(key)

    def test_s3_tmpdir(self):
        def fake_uuid():
            fake_uuid.counter += 1
            return "FAKE-UUID-%d" % fake_uuid.counter
        fake_uuid.counter = 0
        self.assertEqual(
            s3.path.gettmpdir(bucket=TEST_BUCKET, prefix=self.s3_path, uuid_generator=fake_uuid),
            's3://%s/%sFAKE-UUID-1/' % (TEST_BUCKET, self.s3_path))
        self.assertEqual(
            len(list(s3.ls('s3://%s/%sFAKE-UUID-1' % (TEST_BUCKET, self.s3_path)))),
            1)
        self.assertTrue(
            s3.exists('s3://%s/%sFAKE-UUID-1/.tempdir' % (TEST_BUCKET, self.s3_path)))
        self.assertEqual(
            s3.path.gettmpdir(bucket=TEST_BUCKET, prefix=self.s3_path, uuid_generator=fake_uuid),
            's3://%s/%sFAKE-UUID-2/' % (TEST_BUCKET, self.s3_path))
        self.assertEqual(len(list(s3.ls('s3://%s/%sFAKE-UUID-2' % (TEST_BUCKET, self.s3_path)))), 1)
        self.assertTrue(s3.exists('s3://%s/%sFAKE-UUID-2/.tempdir' % (TEST_BUCKET, self.s3_path)))
