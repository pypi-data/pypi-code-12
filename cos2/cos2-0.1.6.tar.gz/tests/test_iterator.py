# -*- coding: utf-8 -*-

import unittest
import hashlib

import cos2

from common import *
from cos2 import to_string


class TestIterator(CosTestCase):
    # def test_bucket_iterator(self):
    #     service = cos2.Service(cos2.Auth(COS_ID, COS_SECRET), COS_ENDPOINT)
    #     self.assertTrue(COS_BUCKET in (b.name for b in cos2.BucketIterator(service, max_keys=2)))
    #     self.assertTrue(COS_BUCKET in list(b.name for b in cos2.BucketIterator(service, max_keys=2)))

    def test_object_iterator(self):
        prefix = self.random_key('/')
        object_list = []
        dir_list = []

        # 准备文件
        for i in range(20):
            object_list.append(prefix + random_string(16))
            self.bucket.put_object(object_list[-1], random_bytes(10))

        # 准备目录
        for i in range(5):
            dir_list.append(prefix + random_string(5) + '/')
            self.bucket.put_object(dir_list[-1] , random_bytes(3))

        # 验证
        objects_got = []
        dirs_got = []
        for info in cos2.ObjectIterator(self.bucket, prefix, delimiter='/'):
            if info.is_prefix():
                dirs_got.append(info.key)
            else:
                objects_got.append(info.key)
                result = self.bucket.head_object(info.key)
                #self.assertEqual(result.last_modified, info.last_modified)
        self.assertEqual(sorted(object_list), objects_got)
        self.assertEqual(sorted(dir_list), dirs_got)
        delete_keys(self.bucket, object_list)
        delete_keys(self.bucket,dir_list)

    def test_object_iterator_chinese(self):
        for prefix in [self.random_key('中+文'), self.random_key(u'中+文')]:
            self.bucket.put_object(prefix, b'content of obj')
            object_got = list(cos2.ObjectIterator(self.bucket, prefix=prefix, max_keys=1))[0].key
            self.assertEqual(to_string(prefix), to_string(object_got))

    def test_upload_iterator(self):
        prefix = self.random_key('/')
        key = prefix + random_string(16)

        upload_list = []
        expect = []

        # 准备分片上传
        for i in range(10):
            upload_list.append(self.bucket.init_multipart_upload(key).upload_id)

        # 验证
        uploads_got = []
        for u in cos2.MultipartUploadIterator(self.bucket, max_uploads=2):
            uploads_got.append(u.upload_id)

        self.assertEqual(sorted(upload_list), uploads_got)

        for upload_id in upload_list:
            self.bucket.abort_multipart_upload(key,upload_id)

    def test_upload_iterator_chinese(self):
        upload_list = []

        p = self.random_key()
        prefix_list = [p + '中文-阿+里-巴*巴', p + u'中文-四/十*大%盗']
        for prefix in prefix_list:
            upload_list.append(self.bucket.init_multipart_upload(prefix).upload_id)
        uploads_got = []
        result =[]
        for u in cos2.MultipartUploadIterator(self.bucket,max_uploads=1):
            uploads_got.append(u.upload_id)

        self.assertEqual(sorted(upload_list), sorted(uploads_got))
        for i in range(0,len(upload_list)):
            self.bucket.abort_multipart_upload(prefix_list[i],upload_list[i])


    def test_part_iterator(self):
        for key in [random_string(16), '中文+_)(*&^%$#@!前缀', u'中文+_)(*&^%$#@!前缀']:
            upload_id = self.bucket.init_multipart_upload(key).upload_id

            # 准备分片
            part_list = []
            for part_number in [1, 3, 6, 7, 9, 10]:
                content = random_string(128 * 1024)
                etag = hashlib.md5(cos2.to_bytes(content)).hexdigest().upper()
                part_list.append(cos2.models.PartInfo(part_number, etag, len(content)))

                self.bucket.upload_part(key, upload_id, part_number, content)
                #print(str(upload_id)+'--'+str(part_number))

            # 验证
            parts_got = []
            for part_info in cos2.PartIterator(self.bucket, key, upload_id):
                parts_got.append(part_info)

            self.assertEqual(len(part_list), len(parts_got))

            for i in range(len(part_list)):
                self.assertEqual(part_list[i].part_number, parts_got[i].part_number)
                self.assertEqual(part_list[i].etag.lower(), parts_got[i].etag)
                self.assertEqual(part_list[i].size, parts_got[i].size)

            self.bucket.abort_multipart_upload(key, upload_id)


if __name__ == '__main__':
    unittest.main()