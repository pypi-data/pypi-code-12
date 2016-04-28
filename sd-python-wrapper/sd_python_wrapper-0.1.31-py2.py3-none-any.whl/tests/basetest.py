#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os.path
import json


class BaseTest(unittest.TestCase):

    def get_json(self, path):
        with open(os.path.dirname(__file__) + path, 'r') as f:
            jsondata = json.load(f)
        return jsondata
