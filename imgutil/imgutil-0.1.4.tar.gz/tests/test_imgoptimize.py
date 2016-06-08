#!/usr/bin/env python

# standard library imports
from contextlib import closing
import os
import os.path
from tempfile import NamedTemporaryFile
import unittest

# third party related imports
from PIL import Image
from sure import expect

# local library imports
from imgutil import imgoptimize


class TestImgOptimize(unittest.TestCase):

    def setUp(self):

        self.curr_dir = os.path.abspath(os.path.dirname(__file__))

    def test_reduce_jpeg_file_size(self):

        test_jpeg = os.path.join(self.curr_dir, 'fixture', 'test_1024x768.jpg')
        original_size = os.stat(test_jpeg).st_size

        with closing(NamedTemporaryFile(suffix='.jpg')) as f:
            imgoptimize(test_jpeg, output_filename=f.name)
            file_size = os.stat(f.name).st_size
            expect(file_size).to.lower_than(original_size)

    def test_reduce_png_file_size(self):

        test_png = os.path.join(self.curr_dir, 'fixture', 'test_1024x768.png')
        original_size = os.stat(test_png).st_size

        with closing(NamedTemporaryFile(suffix='.png')) as f:
            imgoptimize(test_png, output_filename=f.name)
            file_size = os.stat(f.name).st_size
            expect(file_size).to.lower_than(original_size)

    def test_convert_cmyk_to_rgb(self):

        cmyk_jpeg = os.path.join(self.curr_dir, 'fixture', 'cmyk.jpg')

        with closing(NamedTemporaryFile(suffix='.jpg')) as f:
            imgoptimize(cmyk_jpeg, output_filename=f.name)

            img = Image.open(f.name)
            expect(img.getbands()).to.equal(('R', 'G', 'B'))

