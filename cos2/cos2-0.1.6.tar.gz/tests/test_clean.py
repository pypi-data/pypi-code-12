import unittest
import cos2

from common  import *
from cos2 import utils

class TestMultipart(CosTestCase):
    def test_delete_all_obj(self):
        for bucketInfo in self.service.list_buckets().buckets:
           for object in self.bucket.list_objects().object_list:
               self.bucket.delete_object(object.key)
           for uploadinfo in self.bucket.list_multipart_uploads().upload_list:
               self.bucket.abort_multipart_upload(uploadinfo.key,uploadinfo.upload_id)

if __name__ == '__main__':
    unittest.main()