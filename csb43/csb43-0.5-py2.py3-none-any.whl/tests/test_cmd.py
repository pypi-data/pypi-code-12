# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest
import tempfile
#import pandas as pd
import sys
import os
import json
import yaml

from ..utils import cmd
from ..utils import compat
from . import samples


class TestCmd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.doc = samples.sample1()
        cls.tmpdir = tempfile.mkdtemp()
        cls.finput = os.path.join(cls.tmpdir, "input.n43")

        with open(cls.finput, "wb") as fd:
            fd.write(compat.m3_bytes(cls.doc))
            cls.finput = fd.name
            print(cls.finput)

    def setUp(self):
        self.parser = cmd.get_parser()

    def new_file(self, filename):
        return os.path.join(self.tmpdir, filename)

    def make_args(self, foutput, fmt):
        largs = [
            "--strict",
            "-f", fmt,
            self.finput,
            foutput
        ]
        print(" ".join(largs), file=sys.stderr)
        return self.parser.parse_args(largs)

    def test_convert_to_json(self):
        foutput = self.new_file("output.json")
        args = self.make_args(foutput, "json")

        cmd.convert(args)

        with open(foutput) as fd:
            d = json.load(fd)
            print(d)

    def test_convert_to_yaml(self):
        foutput = self.new_file("output.yaml")
        args = self.make_args(foutput, "yaml")

        cmd.convert(args)

        with open(foutput) as fd:
            d = yaml.load(fd)
            print(d)

    def test_convert_to_homebank(self):
        foutput = self.new_file("output.homebank")
        args = self.make_args(foutput, "homebank")

        cmd.convert(args)

    def test_convert_to_csv(self):
        foutput = self.new_file("output.csv")
        args = self.make_args(foutput, "csv")

        cmd.convert(args)

    def test_convert_to_tsv(self):
        foutput = self.new_file("output.tsv")
        args = self.make_args(foutput, "tsv")

        cmd.convert(args)

    def test_convert_to_ofx(self):
        foutput = self.new_file("output.ofx")
        args = self.make_args(foutput, "ofx")

        cmd.convert(args)

    def test_convert_to_ofx1(self):
        foutput = self.new_file("output.ofx1")
        args = self.make_args(foutput, "ofx1")

        cmd.convert(args)

    def test_convert_to_ods(self):
        foutput = self.new_file("output.ods")
        args = self.make_args(foutput, "ods")

        cmd.convert(args)

    def test_convert_to_xls(self):
        foutput = self.new_file("output.xls")
        args = self.make_args(foutput, "xls")

        cmd.convert(args)

    def test_convert_to_xlsx(self):
        foutput = self.new_file("output.xlsx")
        args = self.make_args(foutput, "xlsx")

        cmd.convert(args)
