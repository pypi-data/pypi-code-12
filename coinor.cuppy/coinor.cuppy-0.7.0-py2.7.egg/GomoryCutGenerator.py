import os
import math
import numpy as np
from cylp.cy import CyClpSimplex
from cylp.py.modeling import CyLPArray, CyLPModel
from cylp.py.modeling.CyLPModel import getCoinInfinity
from cuttingPlanes import gomoryCut

epsilon = 0.01

def isInt(x):
    '''
    Return True if x is an integer, or if x is a numpy array
    with all integer elements, False otherwise
    '''
    if isinstance(x, (int, long, float)):
        return abs(math.floor(x) - x) < epsilon
    return (np.abs(np.floor(x) - x) < epsilon).all()

def getFraction(x):
    'Return the fraction part of x: x - floor(x)'
    return x - math.floor(x)

class GomoryCutGenerator:
    def __init__(self, cyLPModel):
        self.cyLPModel = cyLPModel

    def generateCuts(self, si, cglTreeInfo):
        m = self.cyLPModel
        x = m.getVarByName('x')

        clpModel = si.clpModel
        clpModel.dual(startFinishOptions='x')
        solution = clpModel.primalVariableSolution
        bv = clpModel.basicVariables
        rhs = clpModel.rhs

        intInds = clpModel.integerInformation

        rhsIsInt = map(isInt, rhs)

        cuts = []
        for rowInd in xrange(s.nConstraints):
            basicVarInd = bv[rowInd]
            if basicVarInd < clpModel.nVariables and intInds[basicVarInd] and not rhsIsInt[rowInd]:
                coef, b = gomoryCut(clpModel, rowInd)
                if b != None:
                    print 'Adding cut: ', coef, '>=', b
                    expr = CyLPArray(coef) * x >= b
                    cuts.append(expr)
        return cuts


if __name__ == '__main__':
    m = CyLPModel()

    import_model = True

    if (import_model):
        from MIP11 import numVars, A, b, c, sense
        try:
            from MIP11 import x_u
        except ImportError:
            x_u = None
        else:
            x_u = CyLPArray(x_u)
                    
        A = np.matrix(A)
        b = CyLPArray(b)
        
        #We assume variables have zero lower bounds
        x_l = CyLPArray([0 for i in range(numVars)])
        
        #Integrality tolerance
        epsilon = .01
        
        x = m.addVariable('x', numVars, isInt = True)
        
        m += x >= x_l
        if x_u is not None:
            m += x <= x_u
        
        m += (A * x <= b if sense[1] == '<=' else
               A * x >= b)
        
        c = CyLPArray(c)
        m.objective = -c * x if sense[0] == 'Max' else c * x

        s = CyClpSimplex(m)
    else:
        s = CyClpSimplex()
        #cylpDir = os.environ['CYLP_SOURCE_DIR']
        #inputFile = os.path.join('..', '..', 'input', 'p0033.mps')
        m = s.extractCyLPModel('p0033.mps')
        x = m.getVarByName('x')
        s.setInteger(x)

    cbcModel = s.getCbcModel()

    gc = GomoryCutGenerator(m)
    cbcModel.addPythonCutGenerator(gc, name='PyGomory')

    cbcModel.logLevel = 10000
    cbcModel.branchAndBound()
    #cbcModel.solve()
    
    print cbcModel.primalVariableSolution

