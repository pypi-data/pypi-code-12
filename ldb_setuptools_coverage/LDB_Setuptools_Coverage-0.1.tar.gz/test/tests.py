# Copyright 2016 Alex Orange
# 
# This file is part of LDB Setuptools Coverage.
# 
# LDB Setuptools Coverage is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# LDB Setuptools Coverage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with LDB Setuptools Coverage.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import subprocess

def do_coverage(path):
    my_pipe = subprocess.Popen(['python', 'setup.py', 'coverage'], cwd=path,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    comm = my_pipe.communicate()
    return comm, my_pipe.wait()

class SimpleTestCase(unittest.TestCase):
    # TODO: Investigate doing this with multiprocessing and hacking
    # sys.path and the like
    # TODO: Parse output to make sure error messages specifying reason for
    # failure are provided and success message is given.
    def testPkgPass(self):
        comm, exit_code = do_coverage('test_packages/test_pass/')
        self.assertEqual(0, exit_code, comm)

    def testPkgFailTest(self):
        comm, exit_code = do_coverage('test_packages/test_fail_test/')
        self.assertEqual(1, exit_code, comm)

    def testPkgFailCoverage(self):
        comm, exit_code = do_coverage('test_packages/test_fail_coverage/')
        self.assertEqual(2, exit_code, comm)

