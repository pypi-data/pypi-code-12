# -*- coding: utf-8 -*-
from __future__ import print_function

import unittest

import filecmp
import os
import tempfile

from redirector import FileOutputRedirector
from redirector import FunctionOutputRedirector
from redirector import NullOutputRedirector
from redirector import VariableOutputRedirector


class OutputRedirectionTest(unittest.TestCase):
    def testVariableOutputRedirection(self):
        with VariableOutputRedirector() as out:
            print('line1')
            print('line2')
            value = out.getvalue()

        self.assertEqual('line1\nline2\n', value)

    def testNullOutputRedirector(self):
        with VariableOutputRedirector() as out:
            with NullOutputRedirector():
                print('line1')
                print('line2')
            value = out.getvalue()

        self.assertFalse(value)

    def testFileOutputRedirection(self):
        redirected_file = tempfile.NamedTemporaryFile().name
        correct_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'static', 'output_redirection_test',
                                    'correct_file_redirection.txt')
        with FileOutputRedirector(redirected_file):
            print('line3')
            print('line4')
            print('line5')

        print(redirected_file)
        print(correct_file)
        self.assertTrue(filecmp.cmp(redirected_file, correct_file, True))

    def testFunctionOutputRedirector(self):
        output_list = []

        with FunctionOutputRedirector(lambda x: output_list.append(x)):
            print('line6')

        self.assertEquals(output_list, ['l', 'i', 'n', 'e', '6', '\n'])


if __name__ == '__main__':
    unittest.main()
