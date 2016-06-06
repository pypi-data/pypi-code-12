"""Check IEEE1003.1-Chap. 4.2.
"""
from __future__ import absolute_import

import unittest
import os

from filesysobjects.PySourceInfo import getPythonPathModuleRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath


#
#######################
#
class CallUnits(unittest.TestCase):
    name=os.path.curdir+__file__

    output=True
    output=False

    def testCase000(self):
        A = 'a/A.txt'         #@UnusedVariable
        B = 'a/b/B.txt'       #@UnusedVariable
        C = 'a/b/c/C.txt'     #@UnusedVariable
        D = 'a/b/c/d/D.txt'   #@UnusedVariable

        start = 'file://'+str(os.path.dirname(__file__))+os.sep+D
        top = 'file://a/b'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b'
        ]

        assert resx == res
        pass

    def testCase001(self):
        A = 'a/A.txt'         #@UnusedVariable
        B = 'a/b/B.txt'       #@UnusedVariable
        C = 'a/b/c/C.txt'     #@UnusedVariable
        D = 'a/b/c/d/D.txt'   #@UnusedVariable

        start = 'file://'+str(os.path.dirname(__file__))+os.sep+D
        top = 'file:///a/b'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable

        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b'
        ]

        assert resx == res
        pass

    def testCase010(self):
        A = 'a/A.txt'         #@UnusedVariable
        B = 'a/b/B.txt'       #@UnusedVariable
        C = 'a/b/c/C.txt'     #@UnusedVariable
        D = 'a/b/c/d/D.txt'   #@UnusedVariable

        start = 'file://'+str(os.path.dirname(__file__))+os.sep+D
        top = 'file:////a/b'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable

        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b'
        ]

        assert resx == res
        pass

    def testCase011(self):
        A = 'a/A.txt'         #@UnusedVariable
        B = 'a/b/B.txt'       #@UnusedVariable
        C = 'a/b/c/C.txt'     #@UnusedVariable
        D = 'a/b/c/d/D.txt'   #@UnusedVariable

        start = 'file://'+str(os.path.dirname(__file__))+os.sep+D
        top = 'file://///a/b'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable

        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case030/a/b'
        ]

        assert resx == res
        pass


if __name__ == '__main__':
    unittest.main()
