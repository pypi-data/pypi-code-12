# -*- coding: utf-8 -*-

import unittest
import sys
import cos2

from cos2 import to_bytes, to_string

from common import *


class TestChinese(CosTestCase):
    def test_unicode_content(self):
        key = self.random_key()
        content = u'写代码呢最主要的就是开心。'

        self.bucket.put_object(key, content)
        self.assertEqual(self.bucket.get_object(key).read(), content.encode('utf-8'))

    def test_put_get_list_delete(self):
        for key in ['中文!@#$%^&*()-=文件\x0C-1.txt', u'中文!@#$%^&*()-=文件\x0C-1.txt']:
            content = '中文内容'

            self.bucket.put_object(key, content)
            self.assertEqual(self.bucket.get_object(key).read(), to_bytes(content))

            self.assertTrue(to_string(key) in list(to_string(info.key) for info in cos2.ObjectIterator(self.bucket, prefix='中文')))

            self.bucket.delete_object(key)

    def test_batch_delete_objects(self):
        for key in ['中文!@#$%^&*()-=文件\x0C-2.txt', u'中文!@#$%^&*()-=文件\x0C-3.txt', '<hello>']:
            content = '中文内容'

            self.bucket.put_object(key, content)
            result = self.bucket.batch_delete_objects([key])
            self.assertEqual(to_string(result.deleted_keys[0]['Key']), to_string(key))

            self.assertTrue(not self.bucket.object_exists(key))

    def test_local_file(self):
        key = self.random_key('文件!@#$%^&*()-=\x0D\x0E\x7F名')
        content = random_bytes(32) + u'内容\x0D\x0E\7F是中文\x01'.encode('utf-8')

        self.bucket.put_object(key, content)

        key2 = random_string(16)

        self.bucket.get_object_to_file(key, '中文本地文件名.txt')
        self.bucket.put_object_from_file(key2, '中文本地文件名.txt')

        self.assertEqual(self.bucket.get_object(key2).read(), content)

        os.remove(u'中文本地文件名.txt')
        self.bucket.delete_object(key2)


if __name__ == '__main__':
    unittest.main()