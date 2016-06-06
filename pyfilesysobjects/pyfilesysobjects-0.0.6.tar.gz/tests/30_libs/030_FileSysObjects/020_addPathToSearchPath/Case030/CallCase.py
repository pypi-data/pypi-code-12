from __future__ import absolute_import

import unittest
import os

from filesysobjects.FileSysObjects import setUpperTreeSearchPath,addPathToSearchPath


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

        start = None
        top = None
        res = []
        ret = setUpperTreeSearchPath(start,top,res) #@UnusedVariable
        res.append(os.path.dirname(os.path.dirname(__file__)+os.sep+D))
        res.append(os.path.dirname(os.path.dirname(__file__)+os.sep+A))
        
        addPathToSearchPath(os.path.dirname(os.path.dirname(__file__)+os.sep+C), res,**{'pos':1})
        
        resx = [
            os.path.abspath(os.path.dirname(__file__)),
            os.path.dirname(os.path.dirname(__file__)+os.sep+C),
            os.path.dirname(os.path.dirname(__file__)+os.sep+D),
            os.path.dirname(os.path.dirname(__file__)+os.sep+A),
        ]

        assert resx == res
        pass

if __name__ == '__main__':
    unittest.main()
