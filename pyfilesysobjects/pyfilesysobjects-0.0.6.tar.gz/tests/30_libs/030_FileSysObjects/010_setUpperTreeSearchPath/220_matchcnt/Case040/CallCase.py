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
        start = os.sep+os.sep+os.path.dirname(__file__)+os.sep+'a/tests//////a/b/tests//c////////d/tests/b///c'
        
        top = '/////tests///'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchcnt':0,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path #@UnusedVariable
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i]))
            
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', 
            '30_libs/030_FileSysObjects', 
            '30_libs', 
            ''
        ]

        #print "4TEST:"+str(res)
        assert resx == res
        pass

    def testCase000r(self):
        start = os.sep+os.sep+os.path.dirname(__file__)+os.sep+'a/tests//////a/b/tests//c////////d/tests/b///c'
        
        top = '/////tests///'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchcnt':0,'reverse':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path #@UnusedVariable
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i]))
            
        resx = [
            '', 
            '30_libs', 
            '30_libs/030_FileSysObjects', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b/c'
        ]

        #print "4TEST:"+str(res)
        assert resx == res
        pass

    def testCase001(self):
        start = os.sep+os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        
        top = '//tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchcnt':1,'reverse':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path #@UnusedVariable
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i]))
            
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b',
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b/c'
        ]

        #print "4TEST:"+str(res)
        assert resx == res
        pass

    def testCase002(self):
        start = os.sep+os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        
        top = '//tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchcnt':2,'reverse':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path #@UnusedVariable
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i]))
            
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b/c'
        ]
        
        #print "4TEST:"+str(res)
        assert resx == res
        pass


    def testCase005(self):
        start = os.sep+os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        
        top = '//tests'
        _res = []
        try:
            ret = setUpperTreeSearchPath(start,top,_res,**{'matchcnt':5,'ignore-app-slash':True}) #@UnusedVariable
        except FileSysObjectsException as e:
            pass
        else:
            assert False
        pass


if __name__ == '__main__':
    unittest.main()
