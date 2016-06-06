"""Check defaults.
"""
from __future__ import absolute_import

import unittest
import os

from filesysobjects.PySourceInfo import getPythonPathModuleRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,\
    FileSysObjectsException


#
#######################
#
class CallUnits(unittest.TestCase):
    name=os.path.curdir+__file__

    output=True
    output=False

    def testCase000(self):
        start = os.sep+os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        
        top = '//tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchcnt':0,'relonly':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
#        res = []
#         for i in range(len(_res)):
#             res.append(getPythonPathModuleRel(_res[i]))
            
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c/d/tests/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c/d/tests/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c/d/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly/Case020', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/240_relonly', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', 
            '30_libs/030_FileSysObjects', 
            '30_libs'
        ]

        #print "4TEST:"+str(_res)
        assert resx == _res
        pass

    def testCase001(self):
        start = os.sep+os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        
        top = '//tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchcnt':1,'relonly':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        resx = [
            'a/b/tests/c/d/tests/b/c', 
            'a/b/tests/c/d/tests/b', 
            'a/b/tests/c/d/tests', 
            'a/b/tests/c/d', 
            'a/b/tests/c', 
            'a/b/tests', 
            'a/b', 
            'a'
        ]
        
        #print "4TEST:"+str(_res)
        assert resx == _res
        pass

    def testCase002(self):
        start = os.sep+os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        
        top = '//tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchcnt':2,'relonly':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        resx = [
            'c/d/tests/b/c', 
            'c/d/tests/b', 
            'c/d/tests', 
            'c/d', 
            'c'
        ]
        
        #print "4TEST:"+str(_res)
        assert resx == _res
        pass

    def testCase003(self):
        start = os.sep+os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        
        top = '//tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchcnt':3,'relonly':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        resx = [
            'b/c', 
            'b'
        ]
        
        #print "4TEST:"+str(res)
        assert resx == _res
        pass

if __name__ == '__main__':
    unittest.main()
