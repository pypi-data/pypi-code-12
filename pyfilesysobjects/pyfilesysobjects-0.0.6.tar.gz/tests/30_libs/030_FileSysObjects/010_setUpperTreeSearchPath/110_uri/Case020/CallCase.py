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
        start = 'file://'+str(os.path.dirname(__file__))
        top = 'tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case020', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', 
            '30_libs/030_FileSysObjects', 
            '30_libs',
            ''
        ]                

        assert resx == res
        pass

    def testCase001(self):
        start = 'file://'+str(os.path.dirname(__file__))
        top = 'tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'reverse':True}) #@UnusedVariable
        
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
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case020', 
        ]                

        assert resx == res
        pass

    def testCase010(self):
        start = 'file://'+str(os.path.dirname(__file__))
        top = 'file://tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case020', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', 
            '30_libs/030_FileSysObjects', 
            '30_libs', 
            ''
        ]

        assert resx == res
        pass

    def testCase011(self):
        start = 'file://'+str(os.path.dirname(__file__))
        top = 'file://tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'reverse':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '',
            '30_libs', '30_libs/030_FileSysObjects', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/110_uri/Case020', 
        ]

        assert resx == res
        pass


if __name__ == '__main__':
    unittest.main()
