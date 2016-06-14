# -*- coding: utf-8 -*-

import unittest
import cos2

from common  import *
from cos2 import utils



class TestMultipart(CosTestCase):
    def test_multipart(self):
        key = "large"
        content = random_bytes(5*1024* 1024)

        parts = []

        upload_id = self.bucket.init_multipart_upload(key).upload_id
        for i in range (1,10):
            result = self.bucket.upload_part(key, upload_id, i, content)
            parts.append(cos2.models.PartInfo(i, result.etag))
        self.bucket.complete_multipart_upload(key, upload_id, parts)

        result = self.bucket.get_object(key).read()
        #self.assertEqual(utils.md5_string(content), utils.md5_string(result))

        parts = []

        upload_id = self.bucket.init_multipart_upload(key).upload_id
        for i in range (1,20):
            result = self.bucket.upload_part(key, upload_id, i, content)
            parts.append(cos2.models.PartInfo(i, result.etag))

        self.bucket.complete_multipart_upload(key, upload_id, parts)

        result = self.bucket.get_object(key).read()
        #self.assertEqual(utils.md5_string(content), utils.md5_string(result))
        self.assertEqual(self.bucket.head_object(key).status,200)
        self.assertEqual(self.bucket.delete_object(key).status,200)


    def test_upload(self):
        filename = "my-first-cos-upload.txt"
        content = cos2.to_bytes(random_string(10 *1024 * 1024 ))

        with open(filename, 'wb') as fileobj:
            fileobj.write(content)


# 也可以直接调用分片上传接口。
# 首先可以用帮助函数设定分片大小，设我们期望的分片大小为128KB
        total_size = os.path.getsize(filename)
        part_size = cos2.determine_part_size(total_size, preferred_size=5*1024*1024)

# 初始化分片上传，得到Upload ID。接下来的接口都要用到这个Upload ID。
        key = 'remote-multipart.txt'
        upload_id = self.bucket.init_multipart_upload(key).upload_id

# 逐个上传分片
# 其中cos2.SizedFileAdapter()把fileobj转换为一个新的文件对象，新的文件对象可读的长度等于num_to_upload
        with open(filename, 'rb') as fileobj:
            parts = []
            part_number = 1
            offset = 0
            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                result = self.bucket.upload_part(key, upload_id, part_number,
                                    cos2.SizedFileAdapter(fileobj, num_to_upload))
                parts.append(cos2.models.PartInfo(part_number, result.etag))

                offset += num_to_upload
                part_number += 1

    # 完成分片上传
        self.bucket.complete_multipart_upload(key, upload_id, parts)
        print("complete upload")


# 验证一下
        with open(filename, 'rb') as fileobj:
            assert self.bucket.get_object(key).read() == fileobj.read()

        os.remove(filename)

if __name__ == '__main__':
    unittest.main()