from __future__ import absolute_import

import unittest
import os

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
        A = 'a/A.txt'         #@UnusedVariable
        B = 'a/b/B.txt'       #@UnusedVariable
        C = 'a/b/c/C.txt'     #@UnusedVariable
        D = 'a/b/c/d/D.txt'   #@UnusedVariable

        start = os.path.dirname(os.path.dirname(__file__)+os.sep+D)
        top = os.path.dirname(__file__)
        res = [
            os.path.abspath(os.path.dirname(__file__)),
            os.path.dirname(os.path.dirname(__file__)+os.sep+C),
            os.path.dirname(os.path.dirname(__file__)+os.sep+A),
        ]
        ret = setUpperTreeSearchPath(start,top,res,**{'unique':True}) #@UnusedVariable

        resx = [
            os.path.dirname(os.path.dirname(__file__)+os.sep+D),
            os.path.dirname(os.path.dirname(__file__)+os.sep+B),
            os.path.abspath(os.path.dirname(__file__)),
            os.path.dirname(os.path.dirname(__file__)+os.sep+C),
            os.path.dirname(os.path.dirname(__file__)+os.sep+A),
        ]

        assert resx == res
        pass

if __name__ == '__main__':
    unittest.main()
