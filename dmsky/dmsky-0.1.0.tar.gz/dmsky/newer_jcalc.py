#!/usr/bin/env python
"""Python module for computing the line-of-sight integral over a
spherically symmetric DM distribution.
"""
__author__   = "Matthew Wood"
__date__     = "12/01/2011"

import copy
import numpy as np

from scipy.integrate import quad
from scipy.interpolate import splrep,splev
from scipy.interpolate import bisplrep,bisplev
from scipy.interpolate import interp1d, UnivariateSpline
from scipy.interpolate import UnivariateSpline, SmoothBivariateSpline
import scipy.special as spfn
import scipy.optimize as opt

class LoSFn(object):
    """Integrand function for LoS parameter (J).  The parameter alpha
    introduces a change of coordinates x' = x^(1/alpha).  The change
    of variables means that we need make the substitution:

    dx = alpha * (x')^(alpha-1) dx'

    A value of alpha > 1 weights the points at which we sample the
    integrand closer to x = 0 (distance of closest approach).

    Parameters
    ----------
    d: Distance to halo center.
    xi: Offset angle in radians.
    dp: Density profile.
    alpha: Rescaling exponent for line-of-sight coordinate.
    """

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
    
class LoSFnDecay(LoSFn):
    def __init__(self,d,xi,dp,alpha=1.0):
        super(LoSFnDecay,self).__init__(d,xi,dp,alpha)
        
    def __call__(self,xp):
        #xp = np.asarray(xp)
        #if xp.ndim == 0: xp = np.array([xp])

        x = np.power(xp,self._alpha)
        r = np.sqrt(x*x+self._d2*self._sinxi2)
        rho = self._dp.rho(r)
        return rho*self._alpha*np.power(xp,self._alpha-1.0)

class LoSIntegral(object):
    """Object that computes integral over DM density squared along a
    line-of-sight offset by an angle psi from the center of the DM
    halo.  We introduce a change of coordinates so that the integrand
    is more densely sampled near the distance of closest of approach
    to the halo center.

    Parameters
    ----------
    dist: Distance to halo center.
    dp: Density profile.
    alpha: Parameter determining the integration variable: x' = x^(1/alpha)
    rmax: Radius from center of halo at which LoS integral is truncated.
    """
    def __init__(self, dp, dist, rmax=None, alpha=3.0,ann=True):
        if rmax is None: rmax = np.inf

        self._dp = dp
        self._dist = dist
        self._rmax = rmax
        self._alpha = alpha
        self._ann = ann

    def __call__(self,psi,dhalo=None):
        """Evaluate the LoS integral at the offset angle psi for a halo
        located at the distance dhalo.

        Parameters
        ----------
        psi : array_like 
        Array of offset angles (in radians)

        dhalo : array_like
        Array of halo distances.
        """

        if dhalo is None: dhalo = np.array(self._dist,ndmin=1)
        else: dhalo = np.array(dhalo,ndmin=1)

        psi = np.array(psi,ndmin=1)

        if dhalo.shape != psi.shape:
            dhalo = dhalo*np.ones(shape=psi.shape)

        v = np.zeros(shape=psi.shape)

        for i, t in np.ndenumerate(psi):

            s0 = 0
            s1 = 0

            if self._ann:
                losfn = LoSFn(dhalo[i],t,self._dp,self._alpha)
            else:
                losfn = LoSFnDecay(dhalo[i],t,self._dp,self._alpha)

            # Closest approach to halo center
            rmin = dhalo[i]*np.sin(psi[i])

            # If observer inside the halo...
            if self._rmax > dhalo[i]:

                if psi[i] < np.pi/2.:

                    x0 = np.power(dhalo[i]*np.cos(psi[i]),1./self._alpha)
                    s0 = 2*quad(losfn,0.0,x0)[0]

                    x1 = np.power(np.sqrt(self._rmax**2 -
                                          rmin**2),1./self._alpha)
                
                    s1 = quad(losfn,x0,x1)[0]
                else:
                    x0 = np.power(np.abs(dhalo[i]*np.cos(psi[i])),
                                  1./self._alpha)

                    x1 = np.power(np.sqrt(self._rmax**2 -
                                          rmin**2),1./self._alpha)
                    s1 = quad(losfn,x0,x1)[0]

            # If observer outside the halo...
            elif self._rmax > rmin:
                x0 = np.power(np.sqrt(self._rmax**2 -
                                      rmin**2),1./self._alpha)
                s0 = 2*quad(losfn,0.0,x0)[0]
                
            v[i] = s0+s1

        return v

class LoSIntegralFast(LoSIntegral):
    """Vectorized version of LoSIntegral that performs midpoint
    integration with a fixed number of steps.

    Parameters
    ----------
    dist: Distance to halo center.
    dp:   Density profile.
    alpha: Parameter determining the integration variable: x' = x^(1/alpha)
    rmax: Radius from center of halo at which LoS integral is truncated.
    nstep: Number of integration steps.  Increase this parameter to
    improve the accuracy of the LoS integral.
    """
    def __init__(self, dp, dist, rmax=None, alpha=3.0,ann=True,nstep=400):
        if rmax is None:
            rmax = dp.rmax if dp.rmax < np.inf else 100*dp.rs
        super(LoSIntegralFast,self).__init__(dp,dist,rmax,alpha,ann)

        self._nstep = nstep
        xedge = np.linspace(0,1.0,self._nstep+1)
        self._x = 0.5*(xedge[1:] + xedge[:-1])

    def __call__(self,psi,dhalo=None):
        """Evaluate the LoS integral at the offset angle psi for a halo
        located at the distance dhalo.

        Parameters
        ----------
        psi : array_like 
        Array of offset angles (in radians)

        dhalo : array_like
        Array of halo distances.
        """

        if dhalo is None: dhalo = np.array(self._dist,ndmin=1)
        else: dhalo = np.array(dhalo,ndmin=1)

        psi = np.array(psi,ndmin=1)
        v = psi*dhalo
        v.fill(0)
        v = v.reshape(v.shape + (1,))

        dhalo = np.ones(v.shape)*dhalo[...,np.newaxis]
        psi = np.ones(v.shape)*psi[...,np.newaxis]

        if self._ann: losfn = LoSFn(dhalo,psi,self._dp,self._alpha)
        else: losfn = LoSFnDecay(dhalo,psi,self._dp,self._alpha)

        # Closest approach to halo center
        rmin = dhalo*np.sin(psi)

        msk0 = self._rmax > dhalo
        msk1 = self._rmax > rmin

        # Distance between observer and point of closest approach
        xlim0 = np.power(np.abs(dhalo*np.cos(psi)),1./self._alpha)

        # Distance from point of closest approach to maximum
        # integration radius
        xlim1 = np.zeros(shape=psi.shape)
        xlim1[msk1] = np.power(np.sqrt(self._rmax**2 - rmin[msk1]**2),
                               1./self._alpha)

        # If observer inside the halo...
        if np.any(msk0):

            msk01 = msk0 & (psi < np.pi/2.)
            msk02 = msk0 & ~(psi < np.pi/2.)

            if np.any(msk01):

                dx0 = xlim0/float(self._nstep)
                dx1 = (xlim1-xlim0)/float(self._nstep)

                x0 = self._x*xlim0
                x1 = xlim0 + self._x*(xlim1-xlim0)

#                s0 = 2*np.sum(losfn(x0)*dx0,axis=0)
#                s1 = np.sum(losfn(x1)*dx1,axis=0)
                s0 = 2*np.apply_over_axes(np.sum,losfn(x0)*dx0,axes=[-1])
                s1 = np.apply_over_axes(np.sum,losfn(x1)*dx1,axes=[-1])

                v[msk01] = s0[msk01]+s1[msk01]

            if np.any(msk02):
            
                dx1 = (xlim1-xlim0)/float(self._nstep)

                x1 = xlim0 + self._x*(xlim1-xlim0)
#                s0 = np.sum(losfn(x1)*dx1,axis=0)
                s0 = np.apply_over_axes(np.sum,losfn(x1)*dx1,axes=[-1])
            
                v[msk02] = s0[msk02]
                
        # If observer outside the halo...
        if np.any(~msk0 & msk1):
            
            dx0 = xlim1/float(self._nstep)
            x0 = xlim1*self._x
            s0 = 2*np.apply_over_axes(np.sum,losfn(x0)*dx0,axes=[-1])

            v[~msk0 & msk1] = s0[~msk0 & msk1]

        v = v.reshape(v.shape[:-1])
        return v

class LoSIntegralFunc(LoSIntegralFast):
    """ Subclass for interpolation, spline, and file functions.
    """
    def __init__(self, dp, dist, rmax=None, alpha=3.0, ann=True, nstep=400):
        """Create a fast lookup function"""
        super(LoSIntegralFunc,self).__init__(dp, dist, rmax, alpha, ann, nstep)
        self._func,self._spline = self.create_func(dist)

    def create_profile(self, dhalo, npsi=150):
        dhalo = np.unique(np.atleast_1d(dhalo))
        dp = self._dp

        rmin = dp.rmin if dp.rmin else dp.rs*1e-6
        psimin = np.arctan(rmin/dhalo.max())
        rmax = dp.rmax if dp.rmax < np.inf else 100*dp.rs
        psimax = np.arctan(rmax/dhalo.min()) if rmax > dhalo.max() else np.pi
        psi = np.logspace(np.log10(psimin),np.log10(psimax),npsi)

        psi = np.radians(np.logspace(-5,np.log10(120),1000))

        # Pin the last point to 180 deg
        #psi[-1] = np.pi
        
        _dhalo, _psi = np.meshgrid(dhalo,psi)
        _jval = super(LoSIntegralFunc,self).__call__(_psi,_dhalo)
        return _dhalo, _psi, _jval

    def create_func(self, dhalo):
        """Create the spline function
        """
        _dhalo,_psi,_jval = self.create_profile(dhalo)
        log_dhalo,log_psi,log_jval = np.clip(np.log10([_dhalo,_psi,_jval]),-32,None)
        scalar = (_dhalo.shape[-1] == 1)

        #kx = ky = k = 2
        #s=0
        if scalar:
            print "Univariate"
            spline=UnivariateSpline(log_psi.flat,log_jval.flat,k=2,s=0)
            fn = lambda psi: 10**(spline(np.log10(psi)))
        else:
            print "Bivariate"
            spline=SmoothBivariateSpline(log_dhalo.flat,log_psi.flat,log_jval.flat,
                                         kx=1,ky=1)
            fn = lambda dhalo, psi: 10**(spline.ev(np.log10(dhalo),np.log10(psi)))

        return fn,spline

    def __call__(self,psi,dhalo=None):
        """Compute the LoS integral from an interpolating function.

        Returns
        -------
        vals: LoS amplitude per steradian.
        """
        if dhalo is None or np.all(np.in1d(dhalo,self._dist)):
            func = self._func
        else:
            func = self.create_func(dhalo)

        dhalo = np.atleast_1d(dhalo)
        psi = np.atleast_1d(psi)
        if len(dhalo) == 1:
            return func(psi)
        else:
            return func(dhalo,psi)

class LoSIntegralSpline(LoSIntegralFunc): pass
    

def SolidAngleIntegral(psi,pdf,angle):
    """ Compute the solid-angle integrated j-value
    within a given radius

    Parameters
    ----------
    psi : array_like 
    Array of offset angles (in radians)

    pdf : array_like
    Array of j-values at angle psi
    
    angle : array_like
    Maximum integration angle (in degrees)
    """
    angle = np.asarray(angle)
    if angle.ndim == 0: angle = np.array([angle])

    scale=max(pdf)
    norm_pdf = pdf/scale
    bad = np.where(norm_pdf <= 0)[0]
    idx = bad.min() if bad.size else len(pdf)
    log_spline = UnivariateSpline(psi[:idx],np.log10(norm_pdf[:idx]),k=1,s=0)
    spline = lambda r: 10**(log_spline(r))
    integrand = lambda r: spline(r)*2*np.pi*np.sin(r)

    integral = []
    for a in angle:
        integral.append(quad(integrand, 0, np.radians(a),full_output=True)[0])
    integral = np.asarray(integral)

    return integral*scale

class JProfile(object):
    def __init__(self,losfn):

        log_psi = np.linspace(np.log10(np.radians(1E-5)),
                              np.log10(np.radians(90.)),1001)
        self._psi = np.power(10,log_psi)
        self._psi = np.insert(self._psi,0,0)

        domega = 2*np.pi*(-np.cos(self._psi[1:])+np.cos(self._psi[:-1]))
        x = 0.5*(self._psi[1:]+self._psi[:-1])

        self._jpsi = losfn(x)
        self._spline = UnivariateSpline(x,self._jpsi,s=0,k=1)
        self._jcum = np.cumsum(self._spline(x)*domega)
        self._jcum = np.insert(self._jcum,0,0)

        self._cum_spline = UnivariateSpline(self._psi,self._jcum,s=0,k=2)

    @staticmethod
    def create(dp,dist,rmax):
        losfn = LoSIntegral(dp,dist,rmax=rmax)        
        return JProfile(losfn)

    def __call__(self,psi):
        return self._spline(psi)

    def integrate(self,psimax):

        xedge = np.linspace(0.0,np.radians(psimax),1001)
        x = 0.5*(xedge[1:] + xedge[:-1])
        domega = 2.0*np.pi*(-np.cos(xedge[1:])+np.cos(xedge[:-1]))
        return np.sum(self._spline(x)*domega)

    def cumsum(self,psi):
        return self._cum_spline(np.radians(psi))

class Units(object):
    # Could be replaced by astropy

    # length
    cm = 1
    m  = 1e2           # m to cm
    km = m*1e3         # km to cm
    pc = 3.08568e18   # pc to cm
    kpc = pc*1e3      # kpc to cm
    m2 = 1e4

    # mass
    g = 1.0
    msun = 1.98892e33 # solar mass to g
    gev = 1.78266e-24 # gev to g

    # density
    msun_pc3 = msun*np.power(pc,-3) 
    msun_kpc3 = msun*np.power(kpc,-3)
    msun2_pc5 = np.power(msun,2)*np.power(pc,-5)
    msun2_kpc5 = np.power(msun,2)*np.power(kpc,-5)
    gev2_cm5 = np.power(gev,2)
    gev_cm3 = np.power(gev,1)
    gev_cm2 = np.power(gev,1)
    g_cm3 = 1.0
    cm3_s = 1.0

    # random
    hr = 3600.
    deg2 = np.power(np.pi/180.,2)


if __name__ == '__main__':
    print "Line-of-sight Integral Package..."

    import matplotlib.pyplot as plt

    psi = np.linspace(0.01,0.1,500)
    dp = NFWProfile(1,1)

    fn0 = LoSIntegralFast(dp,100,10)
    fn1 = LoSIntegral(dp,100,10)

    dhalo = np.linspace(100,100,500)
    v0 = fn0(dhalo,psi)

    v1 = fn1(dhalo,psi)

    delta = (v1-v0)/v0

    print delta

    plt.hist(delta,range=[min(delta),max(delta)],bins=100)

    plt.show()
    
