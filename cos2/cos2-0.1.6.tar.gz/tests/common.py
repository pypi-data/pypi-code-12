import os
import random
import string
import unittest
import time
import tempfile

import cos2


COS_ID = os.getenv("COS_TEST_ACCESS_KEY_ID")
COS_SECRET = os.getenv("COS_TEST_ACCESS_KEY_SECRET")
COS_ENDPOINT = os.getenv("COS_TEST_ENDPOINT")
COS_BUCKET =  os.getenv("COS_TEST_BUCKET")
COS_WEBSITE_ENDPOINT = os.getenv("COS_WEBSITE_ENDPOINT")

def random_string(n):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(n))


def random_bytes(n):
    return cos2.to_bytes(random_string(n))


def delete_keys(bucket, key_list):
    if not key_list:
        return

    n = 100
    grouped = [key_list[i:i+n] for i in range(0, len(key_list), n)]
    for g in grouped:
        bucket.batch_delete_objects(g)

def delete_bucket(bucket):
    bucket.delete_bucket()

class CosTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(CosTestCase, self).__init__(*args, **kwargs)
        self.bucket = None
        self.prefix = random_string(12)
        self.default_connect_timeout = 360

    def setUp(self):
        self.service =cos2.Service(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT)
        self.bucket = cos2.Bucket(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT, COS_BUCKET,connect_timeout=self.default_connect_timeout)
        self.bucket_anonymousAuth =cos2.Bucket(cos2.AnonymousAuth(), COS_ENDPOINT, COS_BUCKET)
        self.bucket_website_anonymousAuth = cos2.Bucket(cos2.AnonymousAuth(), COS_WEBSITE_ENDPOINT, COS_BUCKET)
        try:
            self.bucket.get_bucket_acl()
        except :
            self.bucket.create_bucket()
            time.sleep(10)
        self.key_list = []
        self.temp_files = []

    def tearDown(self):
        time.sleep(2)
        for temp_file in self.temp_files:
            os.remove(temp_file)
        ## delete object
        for objectInfo in self.bucket.list_objects().object_list:
            self.key_list.append(objectInfo.key)
        delete_keys(self.bucket, self.key_list)
        ## delete uploadInfo
        for uploadinfo in self.bucket.list_multipart_uploads().upload_list:
            self.bucket.abort_multipart_upload(uploadinfo.key,uploadinfo.upload_id)
        ## delete bucket
        delete_bucket(self.bucket)
        time.sleep(10)



    def random_key(self, suffix=''):
        key = self.prefix + random_string(12) + suffix
        self.key_list.append(key)

        return key

    def _prepare_temp_file(self, content):
        fd, pathname = tempfile.mkstemp(suffix='test-upload')

        os.write(fd, content)
        os.close(fd)

        self.temp_files.append(pathname)
        return pathname

    def retry_assert(self, func):
        for i in range(5):
            if func():
                return
            else:
                time.sleep(i+2)

        self.assertTrue(False)
