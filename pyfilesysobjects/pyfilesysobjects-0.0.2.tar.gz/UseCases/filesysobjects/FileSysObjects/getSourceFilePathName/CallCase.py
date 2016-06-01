"""Get the caller name.
"""
from __future__ import absolute_import
from __future__ import print_function

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os,sys

#
# set search for the call of 'myscript.sh'
from filesysobjects.FileSysObjects import setUpperTreeSearchPath
setUpperTreeSearchPath(None,'UseCases')

import filesysobjects.FileSysObjects

#
#######################
#

class CallUnits(unittest.TestCase):
    name=os.path.curdir+__file__

    output=True
    output=False

    def testCase000(self):
        f0 = filesysobjects.FileSysObjects.getSourceFilePathName()
        pp0 = filesysobjects.FileSysObjects.getCallerModulePythonPath()
        ret = filesysobjects.FileSysObjects.getPythonPathModuleRel(f0,[pp0])
        retx = 'UseCases/filesysobjects/FileSysObjects/getSourceFilePathName/CallCase.py'
        assert retx == ret

    def testCase001(self):
        f0 = filesysobjects.FileSysObjects.getSourceFilePathName(1)
        pp0 = filesysobjects.FileSysObjects.getCallerModulePythonPath(1)
        ret = filesysobjects.FileSysObjects.getPythonPathModuleRel(f0,[pp0])
        retx = 'UseCases/filesysobjects/FileSysObjects/getSourceFilePathName/CallCase.py'
        assert retx == ret

    def testCase002(self):
        f0 = filesysobjects.FileSysObjects.getSourceFilePathName(2)
        pp0 = filesysobjects.FileSysObjects.getCallerModulePythonPath(2)
        ret = filesysobjects.FileSysObjects.getPythonPathModuleRel(f0,[pp0])
        retx = 'unittest/case.py'
        assert retx == ret

    def testCase003(self):
        f0 = filesysobjects.FileSysObjects.getSourceFilePathName(3)
        pp0 = filesysobjects.FileSysObjects.getCallerModulePythonPath(3)
        ret = filesysobjects.FileSysObjects.getPythonPathModuleRel(f0,[pp0])
        retx = 'unittest/case.py'
        assert retx == ret

    def testCase004(self):
        f0 = filesysobjects.FileSysObjects.getSourceFilePathName(4)
        pp0 = filesysobjects.FileSysObjects.getCallerModulePythonPath(4)
        ret = filesysobjects.FileSysObjects.getPythonPathModuleRel(f0,[pp0])
        retx = 'unittest2/suite.py'
        assert retx == ret

#
#######################
#

if __name__ == '__main__':
    unittest.main()

