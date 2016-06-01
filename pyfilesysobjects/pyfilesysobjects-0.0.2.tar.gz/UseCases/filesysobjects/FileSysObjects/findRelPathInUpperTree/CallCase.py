"""Check search of a relative filepathname - side-branch - in upper tree.
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

# #
# # set search for the call of 'myscript.sh'
# from filesysobjects.FileSysObjects import setUpperTreeSearchPath
# setUpperTreeSearchPath(None,'UseCases')

from filesysobjects.FileSysObjects import findRelPathInUpperTree,getPythonPathModuleRel


#
#######################
#

class CallUnits(unittest.TestCase):
    name=os.path.curdir+__file__

    output=True
    output=False

    def testCase000(self):
        epy = findRelPathInUpperTree("test00")
        epy = getPythonPathModuleRel(epy,[os.path.abspath(os.path.dirname(__file__)+'../../../../..')])
        x = "UseCases/filesysobjects/FileSysObjects/test00"
        assert epy == x
        pass

    def testCase001(self):
        epy = findRelPathInUpperTree("test01")
        epy = getPythonPathModuleRel(epy,[os.path.abspath(os.path.dirname(__file__)+'../../../../..')])
        x = "UseCases/filesysobjects/test01"
        assert epy == x
        pass

    def testCase002(self):
        epy = findRelPathInUpperTree("test02")
        epy = getPythonPathModuleRel(epy,[os.path.abspath(os.path.dirname(__file__)+'../../../../..')])
        x = "UseCases/test02"
        assert epy == x
        pass
#
#######################
#

if __name__ == '__main__':
    unittest.main()

