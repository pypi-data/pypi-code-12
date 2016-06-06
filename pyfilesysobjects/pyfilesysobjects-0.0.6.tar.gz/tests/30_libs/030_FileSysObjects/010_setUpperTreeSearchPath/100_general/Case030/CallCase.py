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

    #
    # Create by object
    #
    def testCase000(self):
        """Check defaults.
        """

        start = os.path.dirname(__file__)+os.sep+'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'+os.sep+'b'+os.sep+'c'+os.sep
        top = 'tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
        
        import sys
        forDebugOnly = sys.path
        
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathModuleRel(_res[i]))
            
        resx = [
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/100_general/Case030/a/b/c/d/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/100_general/Case030/a/b/c/d/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/100_general/Case030/a/b/c/d', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/100_general/Case030/a/b/c', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/100_general/Case030/a/b', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/100_general/Case030/a', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/100_general/Case030', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath/100_general', 
            '30_libs/030_FileSysObjects/010_setUpperTreeSearchPath', '30_libs/030_FileSysObjects', 
            '30_libs',
            ''
        ]

        assert resx == res
        pass

if __name__ == '__main__':
    unittest.main()
