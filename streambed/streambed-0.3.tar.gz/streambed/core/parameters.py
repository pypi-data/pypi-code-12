#! /usr/bin/env python

class Parameters(object):
    
    """ Data structure and methods for parameters of a streambed model.
    """    
    
    waterDensity = 1000
    gravitationalAcceleration = 9.81
    manningsn = 0.07
    criticalShearStress = 0.0067
    
    def __init__(self, sedimentDensity=2650):

        self.sedimentDensity = sedimentDensity
        