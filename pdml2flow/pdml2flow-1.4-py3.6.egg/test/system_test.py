#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import os
import io
import json
import unittest
from .testcase import TestCase

from pdml2flow.conf import Conf
import pdml2flow

TEST_DIR_PDML2FLOW="test/pdml2flow_tests/"
TEST_DIR_PDML2JSON="test/pdml2json_tests/"

class TestSystem(TestCase):

    def read_json(self, f):
        objs = []
        data = ''
        for line in f:
            data += line
            try:
                objs.append(json.loads(data))
                data = ''
            except ValueError:
                # Not yet a complete JSON value
                pass
        return objs

def get_test(run, directory, test):
    def system_test(self):
        if os.path.isfile('{}/{}/skip'.format(directory, test)):
            self.skipTest('Skipfile found')
        with    open('{}/{}/stdin'.format(directory, test)) as f_stdin, \
                io.StringIO() as f_stdout, \
                io.StringIO() as f_stderr:
            # set stdin & stdout
            Conf.IN = f_stdin
            Conf.OUT = f_stdout
            try:
                # try to load arguments
                with open('{}/{}/args'.format(directory, test)) as f:
                    Conf.ARGS = f.read().split()
            except FileNotFoundError:
                Conf.ARGS = ''
            # run
            run()
            # compare stdout
            objs = self.read_json(f_stdout.getvalue())
            with open('{}/{}/stdout'.format(directory, test)) as f:
                expected = self.read_json(f.read())
            for e in expected:
                self.assertIn(e, objs)
            for o in objs:
                self.assertIn(o, expected)
            try:
                # try compare stderr
                with open('{}/{}/stderr'.format(directory, test)) as f:
                    expected = c_stdout.read()
                self.assertEqual(expected, f_stderr.getvalue())
            except FileNotFoundError:
                pass
    return system_test

def add_tests(run, directory):
    for test in os.listdir(directory):
        # append test
        setattr(TestSystem, "test_system_{}".format(test), get_test(run, directory, test))

# Add tests
add_tests(pdml2flow.pdml2flow, TEST_DIR_PDML2FLOW)
add_tests(pdml2flow.pdml2json, TEST_DIR_PDML2JSON)


if __name__ == '__main__':
    unittest.main()
