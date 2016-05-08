#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import nose
from nose.tools import assert_equal, assert_true, assert_false, raises
from pypirc3.executor.creator import Creator

class TestCreator(object):

    def setup(self):
        self.path     = os.path.join(os.path.dirname(__file__), '.pypirc')
        self.username = 'hoge'
        self.password = 'password'
        # remove .pypirc file for test at each testcase
        if os.path.exists(self.path):
            os.remove(self.path)

    @raises(TypeError)
    def test_require_path(self):
        creator = Creator()

    @raises(TypeError)
    def test_require_username(self):
        creator = Creator(self.path)

    @raises(TypeError)
    def test_require_password(self):
        creator = Creator(self.path, self.username)

    def test_is_empty_empty_username_and_password(self):
        creator = Creator(self.path, '', '')
        assert_true(creator._is_empty())

    def test_is_empty_empty_username(self):
        creator = Creator(self.path, '', self.password)
        assert_true(creator._is_empty())

    def test_is_empty_empty_password(self):
        creator = Creator(self.path, self.username, '')
        assert_true(creator._is_empty())

    def test_is_empty_not_empty_username_and_password(self):
        creator = Creator(self.path, self.username, self.password)
        assert_false(creator._is_empty())

    def test_builded_config_as_ConfigParser(self):
        creator = Creator(self.path, self.username, self.password)
        config = creator._build_config()
        assert_equal('ConfigParser', config.__class__.__name__)

    def test_builded_config_contains_sections_distutils_and_pypi(self):
        creator = Creator(self.path, self.username, self.password)
        config = creator._build_config()
        assert_equal(['distutils', 'pypi'], config.sections())

    def test_builded_config_contains_distutils_items(self):
        creator = Creator(self.path, self.username, self.password)
        config = creator._build_config()
        assert_equal([('index-servers', 'pypi')], config.items('distutils'))

    def test_builded_config_contains_pypi_items(self):
        creator = Creator(self.path, self.username, self.password)
        config = creator._build_config()
        assert_equal([
            ('repository', 'https://pypi.python.org/pypi'),
            ('username', 'hoge'),
            ('password', 'password'),
        ], config.items('pypi'))

    def test_execute_return_value_empty_username_and_password(self):
        creator = Creator(self.path, '', '')
        return_value = creator.execute()
        assert_equal(2, len(return_value))
        assert_equal(1, return_value[0])
        assert_equal('error: username and password are required!', return_value[1])

    def test_execute_return_value(self):
        creator = Creator(self.path, self.username, self.username)
        return_value = creator.execute()
        assert_equal(2, len(return_value))
        assert_equal(0, return_value[0])
        assert_equal('Created ~/.pypirc successfully!', return_value[1])

    def test_execute_and_create_pypirc_file(self):
        creator = Creator(self.path, self.username, self.username)
        creator.execute()
        assert_true(os.path.exists(self.path))
