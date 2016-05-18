# ============================================================
#
# Copyright (C) 2010 by Johannes Wienke <jwienke at techfak dot uni-bielefeld dot de>
# Copyright (C) 2013, 2015 Jan Moringen <jmoringe@techfak.uni-bielefeld.de>
#
# This file may be licensed under the terms of the
# GNU Lesser General Public License Version 3 (the ``LGPL''),
# or (at your option) any later version.
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the LGPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the LGPL along with this
# program. If not, go to http://www.gnu.org/licenses/lgpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# The development of this software was supported by:
#   CoR-Lab, Research Institute for Cognition and Robotics
#     Bielefeld University
#
# ============================================================

from setuptools import setup
from setuptools import find_packages
from setuptools import Command
from setuptools.command.bdist_egg import bdist_egg

from distutils.command.build import build
from distutils.command.sdist import sdist
from distutils.spawn import find_executable

from unittest import TestResult

import os
import re
import setuptools.command.test
import subprocess
import sys
import time
import shutil

class Coverage(Command):
    """
    A command to generate a coverage report using coverage.py.

    @author: jwienke
    """

    description = "generates a coverage report"

    def initialize_options(self):
        self.spread = None

    def finalize_options(self):
        import rsb
        if self.spread == None and rsb.haveSpread():
            self.spread = find_executable("spread")
            if self.spread == None:
                print("WARNING: no spread daemon found. Make sure that one is running before starting the coverage report")

    def run(self):

        spread = None
        if self.spread:
            spread = CommandStarter([self.spread, "-n", "localhost", "-c", "test/spread.conf"])

        import coverage
        cov = coverage.coverage(branch=True, source=["rsb"], omit=["*_pb2*"])
        cov.erase()
        cov.start()
        import test
        suite = test.suite()
        results = TestResult()
        suite.run(results)
        if not results.wasSuccessful():
            print("Unit tests failed while generating test report.")
        cov.stop()
        cov.html_report(directory='covhtml')
        cov.xml_report(outfile='coverage.xml')

class Test(setuptools.command.test.test):
    """
    Wrapper for test command to execute build before testing use a custom test
    runner.

    @author: jwienke
    """

    def initialize_options(self):
        setuptools.command.test.test.initialize_options(self)

    def finalize_options(self):
        setuptools.command.test.test.finalize_options(self)

    def run(self):
        self.run_command('build')

        setuptools.command.test.test.run(self)

    def run_tests(self):
        """
        This method is overridden because setuptools 0.6 does not contain
        support for handling different test runners. In later versions it is
        probably not required to override this method.
        """
        import unittest
        import xmlrunner
        from pkg_resources import EntryPoint
        loader_ep = EntryPoint.parse("x=" + self.test_loader)
        loader_class = loader_ep.load(require=False)
        unittest.main(None, None, [unittest.__file__] + self.test_args,
                      testLoader = loader_class(),
                      testRunner = xmlrunner.XMLTestRunner(output = 'test-reports'))

def defineProjectVersion(majorMinor):

    # first, try to get the required information from git directly and put them
    # in cache files, which can also be created manually in cases we export an
    # archive

    def checkedProgramOutput(commandLine, filename):
        """
        Tries to get the stdout of a program and writes it to the specified file
        in cases where the execution of the program succeeded. Otherwise the
        file remains untouched.
        """

        try:
            proc = subprocess.Popen(commandLine, stdout=subprocess.PIPE)
            (versionOutput, _) = proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError("Git process terminated with return code %s" % proc.returncode)
            if len(versionOutput.strip()) == 0:
                raise RuntimeError("Git process did not produce output")

            with open(filename, 'w') as f:
                f.write(versionOutput)
        except:
            print("Error calling git. Add git to the PATH.")

    checkedProgramOutput(['git', 'describe', '--tags', '--match', 'release-*.*', '--long'], 'gitversion')
    checkedProgramOutput(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 'gitbranch')

    # grab the relevant information from the files
    patchVersion = '0'
    lastCommit = 'archive'

    try:
        gitversion = open('gitversion', 'r').read().strip()
        versionMatch = re.match('^(.+)-([0-9]+)-(g[0-9a-fA-F]+)$', gitversion.strip())
        groups = versionMatch.groups()
        if len(groups) == 3:
            patchVersion = groups[1]
            lastCommit = groups[2]
        else:
            print("Unable to extract patch version and last commit from version string '%s'" % gitversion.strip())
    except Exception, e:
        print("Unable to read from the gitversion file: %s" % e)

    gitbranch = None
    try:
        gitbranch = open('gitbranch', 'r').read().strip()
    except:
        print("Unable to read from the gitbranch file")
    if gitbranch is not None and re.match('[0-9]+\.[0-9]+', gitbranch.strip()) is not None:
        print("This is a release branch. Defining ")
    else:
        patchVersion = '0'
        print("Not on a release branch. Skipping patch version")

    # if we were still not successful defining the commit hash, try to get it
    # using git log
    if lastCommit == 'archive':
        p = subprocess.Popen(['git', 'log' ,'-1', '--pretty=format:g%h'], stdout=subprocess.PIPE)
        lastCommitOnline, _ = p.communicate()
        if p.returncode == 0:
            lastCommit = str(lastCommitOnline).strip()

    return ("%s.%s" % (majorMinor, patchVersion), str(lastCommit))

(version, commit) = defineProjectVersion('0.13')

print("This is version %s-%s" % (version, commit))

# Generate a version file so that version information is available at
# runtime.
with open(os.path.join('rsbag', 'version.py.in'), 'r') as template:
    with open(os.path.join('rsbag', 'version.py'), 'w') as target:
        target.write(template.read()
                     .replace('@VERSION@', version)
                     .replace('@COMMIT@', commit))

setup(name             = 'rsbag-python',
      version          = version,
      description      = """
                         Client API for RSBag.
                         """,
      author           = 'Jan Moringen',
      author_email     = 'jmoringe@techfak.uni-bielefeld.de',
      license          = 'LGPLv3+',
      url              = 'https://code.cor-lab.org/projects/rsbag',
      keywords         = [ 'middleware', 'study', 'logging', 'robotics' ],
      classifiers      = [
          "Programming Language :: Python",
          "Development Status :: 5 - Production/Stable",
          "Environment :: Other Environment",
          "Intended Audience :: Developers",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Operating System :: OS Independent",
          "Topic :: Communications",
          "Topic :: Scientific/Engineering",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],

      setup_requires   = [ "coverage", "epydoc", "unittest-xml-reporting",
                           "setuptools-epydoc", "rsb-python" ],

      install_requires = [ "rsb-python>=%s" % '.'.join(version.split('.')[:-1]),
                           "loggerbyclass>=0.1" ],

      packages         = find_packages(),
      test_suite       = "test.suite",

      cmdclass         = {
          'test':     Test,
          'coverage': Coverage
      })
