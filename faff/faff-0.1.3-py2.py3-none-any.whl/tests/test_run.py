#!/usr/bin/env python
import os
from unittest import TestCase
from ..run import Run


class TestRun(TestCase):
    '''
    Test command run class.
    '''
    def test_run(self):
        '''
        Test run command class.
        '''
        cmd = 'echo "Hello, world!"'
        cwd = os.path.abspath(os.path.dirname(__file__))
        Run(cmd, cwd)

    # TODO: Test output file, override text, etc.
