# -*- coding: utf-8 -*-


import datetime

from common import *
from cos2 import to_string


class TestBucket(CosTestCase):
    def test_bucket(self):
        auth = cos2.Auth(COS_ID, COS_SECRET)
        bucket = cos2.Bucket(auth, COS_ENDPOINT, random_string(63).lower())

        bucket.create_bucket(cos2.BUCKET_ACL_PRIVATE)

        service = cos2.Service(auth, COS_ENDPOINT)

        self.retry_assert(lambda: bucket.bucket_name in (b.name for b in service.list_buckets().buckets))

        key = 'a.txt'
        bucket.put_object(key, 'content')

        self.assertRaises(cos2.exceptions.BucketNotEmpty, bucket.delete_bucket)

        bucket.delete_object(key)
        bucket.delete_bucket()
        time.sleep(10)

        self.assertRaises(cos2.exceptions.NoSuchBucket, bucket.delete_bucket)

    def test_acl(self):
        auth = cos2.Auth(COS_ID, COS_SECRET)
        bucket = cos2.Bucket(auth, COS_ENDPOINT, random_string(63).lower())
        bucket.create_bucket(cos2.BUCKET_ACL_PUBLIC_READ)
        time.sleep(10)
        self.retry_assert(lambda: bucket.get_bucket_acl().acl == cos2.BUCKET_ACL_PUBLIC_READ)

        bucket.put_bucket_acl(cos2.BUCKET_ACL_PRIVATE)
        time.sleep(10)
        self.retry_assert(lambda: bucket.get_bucket_acl().acl == cos2.BUCKET_ACL_PRIVATE)
        bucket.delete_bucket()
        time.sleep(10)

    def test_website(self):
        key = self.random_key()
        index_content = random_bytes(32)
        error_content = random_bytes(32)

        self.bucket.put_object('index.html', index_content)
        self.bucket.put_object('error.html',error_content)

        # 设置index页面和error页面
        self.bucket.put_bucket_website(cos2.models.BucketWebsite('index.html', 'error.html'))

        def same_website(website, index, error):
            return to_string(website.index_file) == index and to_string(website.error_file) == error

        # 验证index页面和error页面
        time.sleep(10)
        self.retry_assert(lambda: same_website(self.bucket.get_bucket_website(), 'index.html', 'error.html'))

        #验证访问website域名跳转到index页面
        self.bucket.put_bucket_acl('public-read')
        time.sleep(10)
        result = self.bucket_website_anonymousAuth.get_object('')
        self.assertEqual(result.read(), index_content)

        # 验证获取不存在的对象，会重定向到error页面
        result = self.bucket_website_anonymousAuth.get_object(key)
        self.assertEqual(result.read(), error_content)

        self.bucket.delete_object('index.html')
        self.bucket.delete_object('error.html')

        # # 中文
        for index, error in [('index+中文.html', 'error.中文'), (u'index+中文.html', u'error.中文')]:
             self.bucket.put_bucket_website(cos2.models.BucketWebsite(index, error))
             time.sleep(10)
             self.retry_assert(lambda: same_website(self.bucket.get_bucket_website(), to_string(index), to_string(error)))

        # 关闭静态网站托管模式
        self.bucket.delete_bucket_website()
        self.bucket.delete_bucket_website()
        time.sleep(10)
        self.assertRaises(cos2.exceptions.NoSuchWebsite, self.bucket.get_bucket_website)

    def test_location(self):
        result = self.bucket.get_bucket_location()
        self.assertTrue(result.location)


if __name__ == '__main__':
    unittest.main()