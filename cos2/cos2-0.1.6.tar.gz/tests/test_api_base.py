# -*- coding: utf-8 -*-

import unittest
import cos2
import socket
import sys
from common import *


class TestApiBase(CosTestCase):

    def test_whitespace(self):
         bucket = cos2.Bucket(cos2.Auth(COS_ID, ' ' + COS_SECRET + ' '), COS_ENDPOINT, COS_BUCKET)
         bucket.get_bucket_acl()

         bucket = cos2.Bucket(cos2.Auth(COS_ID, COS_SECRET), ' ' + COS_ENDPOINT + ' ', COS_BUCKET)
         bucket.get_bucket_acl()

         bucket = cos2.Bucket(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT, ' ' + COS_BUCKET + ' ')
         bucket.get_bucket_acl()

    if sys.version_info >= (3, 3):
        def test_user_agent(self):
            app = 'fantastic-tool'

            assert_found = False
            def do_request(session_self, req, timeout):
                if assert_found:
                    self.assertTrue(req.headers['User-Agent'].find(app) >= 0)
                else:
                    self.assertTrue(req.headers['User-Agent'].find(app) < 0)

                raise cos2.exceptions.ClientError('intentional')

            from unittest.mock import patch
            with patch.object(cos2.Session, 'do_request', side_effect=do_request, autospec=True):
                # 不加 app_name
                assert_found = False
                self.assertRaises(cos2.exceptions.ClientError, self.bucket.get_bucket_acl)

                service = cos2.Service(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT)
                self.assertRaises(cos2.exceptions.ClientError, service.list_buckets)

                # 加app_name
                assert_found = True
                bucket = cos2.Bucket(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT, COS_BUCKET,
                                     app_name=app)
                self.assertRaises(cos2.exceptions.ClientError, bucket.get_bucket_acl)

                service = cos2.Service(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT,
                                       app_name=app)
                self.assertRaises(cos2.exceptions.ClientError, service.list_buckets)


if __name__ == '__main__':
    unittest.main()