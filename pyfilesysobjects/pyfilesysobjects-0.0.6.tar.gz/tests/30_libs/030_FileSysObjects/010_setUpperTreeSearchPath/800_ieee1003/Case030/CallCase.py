"""Check defaults.
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
        start = os.sep+os.path.dirname(__file__)+os.sep+'a'+os.sep+os.sep+'b'+os.sep+os.sep+'c'+os.sep+'d'+os.sep+'b'+os.sep+'c'+os.sep
        top = '//tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'reverse':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i]))
            
        resx = [
            '',
            '30_libs', 
            '30_libs/030_FileSysObjects', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c/d/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c/d/b/c',
        ]

        assert resx == res
        pass

    def testCase001(self):
        start = os.sep+os.path.dirname(__file__)+os.sep+'a'+os.sep+os.sep+'b'+os.sep+os.sep+os.sep+os.sep+'c'+os.sep+'d'+os.sep+'b'+os.sep+'c'+os.sep+os.sep+os.sep
        top = '//tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'reverse':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i]))
            
        resx = [
            '',
            '30_libs', 
            '30_libs/030_FileSysObjects', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c/d/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c/d/b/c',
        ]

        assert resx == res
        pass

    def testCase002(self):
        start = os.sep+os.path.dirname(__file__)+os.sep+'a'+os.sep+os.sep+'b'+os.sep+os.sep+os.sep+os.sep+'c'+os.sep+'d'+os.sep+'b'+os.sep+'c'+os.sep+os.sep+os.sep
        top = '//tests////'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'reverse':True,'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i]))
            
        resx = [
            '',
            '30_libs', 
            '30_libs/030_FileSysObjects', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c/d/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case030/a/b/c/d/b/c',
        ]

        assert resx == res
        pass

if __name__ == '__main__':
    unittest.main()
