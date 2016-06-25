#!/usr/bin/env python
import os
from unittest import TestCase
from ..core import core


class TestCore(TestCase):
    '''
    Test package core configuration class.
    '''
    def test_init(self):
        '''
        Test core class reinitialisation via call method.
        '''
        # Default initialisation.
        core()

        # Assert default properties.
        self.assertEqual(core._stdout, None)
        self.assertEqual(core._stderr, None)
        self.assertEqual(core._log_level, 'WARNING')
        self.assertEqual(core._log_file, None)

    def test_default_input_file(self):
        '''
        Test default input file path.
        '''
        # Assert path is absolute.
        input_file = core.get_default_input_file()
        self.assertTrue(os.path.isabs(input_file))
