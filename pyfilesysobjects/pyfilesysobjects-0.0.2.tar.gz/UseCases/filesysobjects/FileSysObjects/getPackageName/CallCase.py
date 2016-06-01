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

def _funcDummyLvl0(sx=2):
    return (filesysobjects.FileSysObjects.getCallerPackageName(sx), None, )

def _funcDummyLvl1(sx=1):
    return (filesysobjects.FileSysObjects.getCallerPackageName(sx), _funcDummyLvl0(sx+1), )

def _funcDummyLvl2(sx=1):
    return (filesysobjects.FileSysObjects.getCallerPackageName(sx), _funcDummyLvl1(sx+1), )

def _funcDummyLvl3(sx=1):
    return (filesysobjects.FileSysObjects.getCallerPackageName(sx), _funcDummyLvl2(sx+1), )


class CallUnits(unittest.TestCase):
    name=os.path.curdir+__file__

    output=True
    output=False

    def testCase000(self):
        ret = filesysobjects.FileSysObjects.getCallerPackageName()
        retx = None 
        assert retx == ret

    def testCase001(self):
        ret = filesysobjects.FileSysObjects.getCallerPackageName(1)
        retx = None 
        assert retx == ret

    def testCase002(self):
        ret = filesysobjects.FileSysObjects.getCallerPackageName(2)
        retx = 'unittest' 
        assert retx == ret

    def testCase003(self):
        ret = filesysobjects.FileSysObjects.getCallerPackageName(3)
        retx = 'unittest' 
        assert retx == ret

    def testCase004(self):
        ret = filesysobjects.FileSysObjects.getCallerPackageName(4)
        retx = 'unittest2' 
        assert retx == ret

    def testCase009(self):
        ret = filesysobjects.FileSysObjects.getCallerPackageName(9)
        retx = 'unittest2' 
        assert retx == ret


#
#######################
#

if __name__ == '__main__':
    unittest.main()

