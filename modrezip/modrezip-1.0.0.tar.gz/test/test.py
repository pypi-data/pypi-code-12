# pylint: disable=missing-docstring

from io import BytesIO
import os
from unittest import TestCase
from zipfile import ZipFile

from modrezip import repackage_zip

class TestModRezip(TestCase):
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.src_path = os.path.join(self.script_dir, 'test1.zip')

    def test_repackage_zip_empty(self):
        dst_file = BytesIO()

        def cb_none(src_zip, dst_info):
            return None

        repackage_zip(self.src_path, dst_file, cb_none)

        with ZipFile(dst_file) as dst_zip:
            self.assertEqual(dst_zip.namelist(), [])

    def test_repackage_zip_change_name(self):
        dst_file = BytesIO()

        def cb_change_name(src_zip, dst_info):
            if not dst_info.filename.endswith('/'):
                dst_info.filename += '.cool'
            return dst_info

        repackage_zip(self.src_path, dst_file, cb_change_name)

        with ZipFile(dst_file) as dst_zip:
            self.assertEqual(dst_zip.namelist(), [
                'testzip/',
                'testzip/hello.txt.cool',
            ])
