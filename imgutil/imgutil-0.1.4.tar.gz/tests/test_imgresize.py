#!/usr/bin/env python

# standard library imports
from contextlib import closing
import os.path
from tempfile import NamedTemporaryFile
import unittest

# third party related imports
from PIL import Image
from sure import expect

# local library imports
from imgutil import imgresize


class TestImgresize(unittest.TestCase):

    def setUp(self):

        self.curr_dir = os.path.abspath(os.path.dirname(__file__))
        self.test_jpeg = os.path.join(self.curr_dir, 'fixture',
                                      'test_1024x768.jpg')

    def test_specify_width_and_preserve_aspect_ratio(self):

        with closing(NamedTemporaryFile(suffix='.jpg')) as f:
            imgresize(self.test_jpeg, width=1000, output_filename=f.name)

            img = Image.open(f.name)
            expect(img.size[0]).to.equal(1000)
            expect(img.size[1]).to.equal(int(1. * 768 / 1024 * 1000 + 0.5))

    def test_specify_height_and_preserve_aspect_ratio(self):

        with closing(NamedTemporaryFile(suffix='.jpg')) as f:
            imgresize(self.test_jpeg, height=600, output_filename=f.name)

            img = Image.open(f.name)
            expect(img.size[0]).to.equal(int(1. * 1024 / 768 * 600 + 0.5))
            expect(img.size[1]).to.equal(600)

    def test_specify_width_and_height_ignore_aspect_ratio(self):

        with closing(NamedTemporaryFile(suffix='.jpg')) as f:
            imgresize(self.test_jpeg, width=1024, height=768,
                      output_filename=f.name)

            img = Image.open(f.name)
            expect(img.size[0]).to.equal(1024)
            expect(img.size[1]).to.equal(768)

