#!/usr/bin/env python
"""
Line-of-sight integration.
"""


class LoSIntegral(object):
    _defaults = ()

    def __init__(density, distance, **kwargs):
        self.density = density
        self.distance = distance
        self.alpha = 1.0

    def losfn(self,psi):
    def __init__(self,d,xi,dp,alpha=4.0):
        self._d = d
        self._d2 = d*d
        self._xi = xi
        self._sinxi = np.sin(xi)
        self._sinxi2 = np.power(self._sinxi,2)
        self._dp = dp
        self._alpha = alpha

    def __call__(self,xp):

        x = np.power(xp,self._alpha)
        r = np.sqrt(x*x+self._d2*self._sinxi2)
        rho2 = np.power(self._dp.rho(r),2)
        return rho2*self._alpha*np.power(xp,self._alpha-1.0)
        
        
