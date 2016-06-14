# -*- coding: utf-8 -*-

import requests
import filecmp
import calendar

from cos2.exceptions import (ClientError, RequestError,
                             NotFound, NoSuchKey, Conflict)
from common import *


def now():
    return int(calendar.timegm(time.gmtime()))


class TestObject(CosTestCase):
    def test_object(self):
        key = self.random_key('.js')
        content = random_bytes(1024)

        self.assertRaises(NotFound, self.bucket.head_object, key)

        lower_bound = now() - 60 * 16
        upper_bound = now() + 60 * 16

        def assert_result(result):
            self.assertEqual(result.content_length, len(content))
            self.assertEqual(result.content_type, 'application/javascript;charset=UTF-8')
            self.assertTrue(result.last_modified > lower_bound)
            self.assertTrue(result.last_modified < upper_bound)

            self.assertTrue(result.etag)

        self.bucket.put_object(key, content)

        get_result = self.bucket.get_object(key)
        self.assertEqual(get_result.read(), content)
        assert_result(get_result)

        head_result = self.bucket.head_object(key)
        assert_result(head_result)

        self.assertEqual(get_result.last_modified, head_result.last_modified)
        self.assertEqual(get_result.etag, head_result.etag)
        self.bucket.delete_object(key)
        self.assertRaises(NoSuchKey, self.bucket.get_object, key)

    def test_file(self):
        filename = random_string(12) + '.js'
        filename2 = random_string(12)

        key = self.random_key('.txt')
        content = random_bytes(100*1024 )

        with open(filename, 'wb') as f:
            f.write(content)

        # 上传本地文件到COS
        self.bucket.put_object_from_file(key, filename)

        # 检查Content-Type应该是javascript
        result = self.bucket.head_object(key)
        self.assertEqual(result.headers['content-type'], 'application/javascript;charset=UTF-8')

        # 下载到本地文件
        self.bucket.get_object_to_file(key, filename2)

        self.assertTrue(filecmp.cmp(filename, filename2))

        # 上传本地文件的一部分到COS
        key_partial = self.random_key('-partial.txt')
        offset = 100
        with open(filename, 'rb') as f:
            f.seek(offset, os.SEEK_SET)
            self.bucket.put_object(key_partial, f)

        # 检查上传后的文件
        result = self.bucket.get_object(key_partial)
        self.assertEqual(result.content_length, len(content) - offset)
        self.assertEqual(result.read(), content[offset:])

        # 清理
        os.remove(filename)
        os.remove(filename2)

    def test_streaming(self):
        src_key = self.random_key('.src')
        dst_key = self.random_key('.dst')

        content = random_bytes(100*1024)

        self.bucket.put_object(src_key, content)

        # 获取COS上的文件，一边读取一边写入到另外一个COS文件
        src = self.bucket.get_object(src_key).read()
        self.bucket.put_object(dst_key, src)

        # verify
        self.assertEqual(self.bucket.get_object(src_key).read(), self.bucket.get_object(dst_key).read())


    def test_request_error(self):
        bad_endpoint = random_string(8) + '.' + random_string(16) + '.com'
        bucket = cos2.Bucket(cos2.Auth(COS_ID, COS_SECRET), bad_endpoint, COS_BUCKET)

        try:
            bucket.get_bucket_acl()
        except RequestError as e:
            self.assertEqual(e.status, cos2.exceptions.COS_REQUEST_ERROR_STATUS)
            self.assertEqual(e.request_id, '')
            self.assertEqual(e.code, '')
            self.assertEqual(e.message, '')

            self.assertTrue(str(e))
            self.assertTrue(e.body)

    def test_timeout(self):
        bucket = cos2.Bucket(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT, COS_BUCKET,
                             connect_timeout=0.001)
        self.assertRaises(RequestError, bucket.get_bucket_acl)

    def test_default_timeout(self):
        cos2.defaults.connect_timeout = 0.001
        bucket = cos2.Bucket(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT, COS_BUCKET)
        self.assertRaises(RequestError, bucket.get_bucket_acl)

    def test_get_object_iterator(self):
        key = self.random_key()
        content = random_bytes(100 * 1024)

        self.bucket.put_object(key, content)
        result = self.bucket.get_object(key)
        content_got = b''

        for chunk in result:
            content_got += chunk

        self.assertEqual(len(content), len(content_got))
        self.assertEqual(content, content_got)

    def test_anonymous(self):
        key = self.random_key()
        content = random_bytes(512)

        # 设置bucket为public-read，并确认可以上传和下载
        self.bucket.put_bucket_acl('public-read')
        time.sleep(2)

        self.bucket_anonymousAuth.put_object(key, content)
        result = self.bucket_anonymousAuth.get_object(key)
        self.assertEqual(result.read(), content)

        # 测试sign_url
        url = self.bucket_anonymousAuth.sign_url('GET', key, 100)
        resp = requests.get(url)
        self.assertEqual(content, resp.content)

        # 设置bucket为private，并确认上传和下载都会失败
        self.bucket.put_bucket_acl('private')
        time.sleep(10)

        self.assertRaises(cos2.exceptions.AccessDenied, self.bucket_anonymousAuth.put_object, key, content)
        self.assertRaises(cos2.exceptions.AccessDenied, self.bucket_anonymousAuth.get_object, key)

    def test_range_get(self):
        key = self.random_key()
        content = random_bytes(1024)

        self.bucket.put_object(key, content)

        result = self.bucket.get_object(key, byte_range=(500, None))
        self.assertEqual(result.read(), content[500:])

        result = self.bucket.get_object(key, byte_range=(None, 199))
        self.assertEqual(result.read(), content[-199:])

        result = self.bucket.get_object(key, byte_range=(3, 3))
        self.assertEqual(result.read(), content[3:4])

    def test_list_objects(self):
        result = self.bucket.list_objects()
        self.assertEqual(result.status, 200)

    def test_batch_delete_objects(self):
        object_list = []
        for i in range(0, 5):
            key = self.random_key()
            object_list.append(key)

            self.bucket.put_object(key, random_string(64))

        result = self.bucket.batch_delete_objects(object_list)
        result_key_list=[]
        for key in result.deleted_keys:
            result_key_list.append(key["Key"])
        self.assertEqual(sorted(object_list), sorted(result_key_list))

        for object in object_list:
            self.assertTrue(not self.bucket.object_exists(object))


    def test_batch_delete_objects_empty(self):
        try:
            self.bucket.batch_delete_objects([])
        except ClientError as e:
            self.assertEqual(e.status, cos2.exceptions.COS_CLIENT_ERROR_STATUS)
            self.assertEqual(e.request_id, '')
            self.assertEqual(e.code, '')
            self.assertEqual(e.message, '')

            self.assertTrue(e.body)
            self.assertTrue(str(e))


    def test_private_download_url(self):
        for key in [self.random_key(), self.random_key(u'中文文件名')]:
            key = self.random_key()
            content = random_bytes(42)

            self.bucket.put_object(key, content)
            url = self.bucket.sign_url('GET', key, 600)

            resp = requests.get(url)
            self.assertEqual(content, resp.content)


    def test_object_exists(self):
        key = self.random_key()

        self.assertTrue(not self.bucket.object_exists(key))

        self.bucket.put_object(key, "hello world")
        self.assertTrue(self.bucket.object_exists(key))

    def test_user_meta(self):
        key = self.random_key()

        self.bucket.put_object(key, 'hello', headers={'x-cos-meta-key1': 'value1',
                                                      'X-cos-Meta-Key2': 'value2'})

        headers = self.bucket.get_object(key).headers
        self.assertEqual(headers['x-cos-meta-key1'], 'value1')
        self.assertEqual(headers['x-cos-meta-key2'], 'value2')


    def test_exceptions(self):
        key = self.random_key()
        content = random_bytes(16)

        self.assertRaises(NotFound, self.bucket.get_object, key)
        self.assertRaises(NoSuchKey, self.bucket.get_object, key)



if __name__ == '__main__':
    unittest.main()