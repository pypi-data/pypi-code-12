#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of pypeline.
# https://github.com/rfloriano/pypeline

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com

from unittest import TestCase
from preggy import expect

from exec_pypeline import __version__


class VersionTestCase(TestCase):
    def test_has_proper_version(self):
        expect(__version__).to_equal("0.4.1")
