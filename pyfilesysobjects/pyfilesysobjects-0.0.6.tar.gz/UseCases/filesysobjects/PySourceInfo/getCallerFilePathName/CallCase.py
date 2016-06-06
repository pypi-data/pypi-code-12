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
import os

#
# set search for the call of 'myscript.sh'
from filesysobjects.FileSysObjects import setUpperTreeSearchPath
setUpperTreeSearchPath(None,'UseCases')

import filesysobjects.PySourceInfo

#
#######################
#

class CallUnits(unittest.TestCase):
    name=os.path.curdir+__file__

    output=True
    output=False

    def testCase000(self):
        f0 = filesysobjects.PySourceInfo.getCallerFilePathName()
        pp0 = filesysobjects.PySourceInfo.getCallerModulePythonPath()
        ret = filesysobjects.PySourceInfo.getPythonPathModuleRel(f0,[pp0])
        retx = 'UseCases/filesysobjects/PySourceInfo/getCallerFilePathName/CallCase.py'
        assert retx == ret

    def testCase001(self):
        f0 = filesysobjects.PySourceInfo.getCallerFilePathName(1)
        pp0 = filesysobjects.PySourceInfo.getCallerModulePythonPath(1)
        ret = filesysobjects.PySourceInfo.getPythonPathModuleRel(f0,[pp0])
        retx = 'UseCases/filesysobjects/PySourceInfo/getCallerFilePathName/CallCase.py'
        assert retx == ret

    def testCase002(self):
        f0 = filesysobjects.PySourceInfo.getCallerFilePathName(2)
        pp0 = filesysobjects.PySourceInfo.getCallerModulePythonPath(2)
        ret = filesysobjects.PySourceInfo.getPythonPathModuleRel(f0,[pp0])
        retx = 'unittest/case.py'
        assert retx == ret

    def testCase003(self):
        f0 = filesysobjects.PySourceInfo.getCallerFilePathName(3)
        pp0 = filesysobjects.PySourceInfo.getCallerModulePythonPath(3)
        ret = filesysobjects.PySourceInfo.getPythonPathModuleRel(f0,[pp0])
        retx = 'unittest/case.py'
        assert retx == ret

    def testCase004(self):
        f0 = filesysobjects.PySourceInfo.getCallerFilePathName(4)
        pp0 = filesysobjects.PySourceInfo.getCallerModulePythonPath(4)
        ret = filesysobjects.PySourceInfo.getPythonPathModuleRel(f0,[pp0])
        retx = 'unittest2/suite.py'
        assert retx == ret

#
#######################
#

if __name__ == '__main__':
    unittest.main()

