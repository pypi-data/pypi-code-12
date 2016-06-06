"""Check IEEE1003.1-Chap. 4.2.
"""
from __future__ import absolute_import

import unittest
import os

from filesysobjects.PySourceInfo import getPythonPathModuleRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,FileSysObjectsException


#
#######################
#
class CallUnits(unittest.TestCase):
    name=os.path.curdir+__file__

    output=True
    output=False

    def testCase000(self):
        start = '//a/b/c'
        top = os.path.curdir
        _res = []
        try:
            ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
        except FileSysObjectsException as e:
            # currently the default is to keep '//', thus this is an error 
            pass
        else:
            assert False
        pass

    def testCase001(self):
        start = os.sep+os.path.abspath(os.path.dirname(__file__))+'/a/b/c'
        top = '//a/'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'ignore-app-slash':True})
        
        import sys
        forDebugOnly = sys.path #@UnusedVariable
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case020/a'
        ]

        assert resx == res
        pass

    def testCase010(self):
        start = os.sep+os.path.abspath(os.path.dirname(__file__))+'/a/b/c'
        top = 'file:///a/'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case020/a'
        ]

        assert resx == res
        pass

    def testCase011(self):
        start = os.sep+os.path.abspath(os.path.dirname(__file__))+'/a/b/c'
        top = 'file:////a/'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'ignore-app-slash':True}) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i])) 
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/800_ieee1003/Case020/a'
        ]

        assert resx == res
        pass


if __name__ == '__main__':
    unittest.main()
