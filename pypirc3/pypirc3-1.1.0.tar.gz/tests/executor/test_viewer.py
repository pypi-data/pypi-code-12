#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import nose
from nose.tools import assert_equal, assert_true, assert_false, raises
from pypirc3.executor.viewer import Viewer

class TestViewer(object):

    def setup(self):
        self.path = os.path.join(os.path.dirname(__file__), os.path.pardir, '.pypirc')
        self.test_pypirc_content = ''
        with open(self.path, 'r') as f:
            for line in f.readlines():
                self.test_pypirc_content += line

    def test_is_exists(self):
        viewer = Viewer(self.path)
        assert_true(viewer._is_exists())

    def test_is_not_exists(self):
        not_exists_path = os.path.join(os.path.dirname(__file__), '.pypirc')
        viewer = Viewer(not_exists_path)
        assert_false(viewer._is_exists())

    def test_execute_not_exists(self):
        not_exists_path = os.path.join(os.path.dirname(__file__), '.pypirc')
        viewer = Viewer(not_exists_path)
        return_value = viewer.execute()
        assert_equal(2, len(return_value))
        assert_equal(0, return_value[0])
        assert_equal("Don't exists ~/.pypirc! See pypirc3 help, and create ~/.pypirc with pypirc3",
                     return_value[1])

    def test_execute_exists(self):
        viewer = Viewer(self.path)
        return_value = viewer.execute()
        assert_equal(2, len(return_value))
        assert_equal(0, return_value[0])
        assert_equal(self.test_pypirc_content, return_value[1])
