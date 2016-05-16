import numpy as np, time, os, pdb, math
import math, sys, cPickle, re 
import numpy.random as random
from LumDist import LumDist as _lumdist

b_ = dict(u=1.4e-10, g=0.9e-10, r=1.2e-10, i=1.8e-10, z=7.4e-10) #band softening parameter
f0 = 3631.0 #Jy

def lumdist(a, units = "Mpc", da = 0.01, model = "LCDM"):

	results = _lumdist(a, model = model, da = da)
	if units == "Mpc":
		return results
	elif units == "pc":
		return results * 1e3
	elif units == "m":
		return results * 3.068e19
	elif units == "cm":
		return results * 3.068e21
	elif units == "AU":
		return results * 206265e3
	else:
		raise Exception("Invalid Units")

@np.vectorize
def luptitude_to_flux(mag, err, band): #Converts a Luptitude to an SDSS flux

	flux =  math.sinh(math.log(10.0)/-2.5*mag-math.log(b_[band]))*2*b_[band]*f0
	error = err*math.log(10)/2.5*2*b_[band]*math.sqrt(1+(flux/(2*b_[band]*f0))**2)*f0
	return flux, error 

@np.vectorize
def flux_to_lum(flux, z):

	lum = flux*4*math.pi*lumdist(1.0/(1+z), units = 'm')**2
	return lum

def time_to_restFrame(time, z): #Converts a cadence to the rest frame

	t = np.zeros(time.shape[0])
	t[1:] = np.cumsum((time[1:] - time[:-1])/(1+z))

	return t


def get_psd(f, sigma, ar_coefs, ma_coefs, percentile):

	numSamples = ma_coefs.shape[0]
	nfreq = f.shape[0]
	lower = (100.0 - percentile)/2.0
	upper = (100.0 - lower)

	psd = np.empty((numSamples, nfreq))
	K = math.pi*2*f*1j
	q = ma_coefs.shape[1]
	p = ar_coefs.shape[1]
	for i in xrange(nfreq):
		ma = sum(ma_coefs[:,j]*K[i]**(j) for j in xrange(q))
		ar = sum(K[i]**(p-j-1)*ar_coefs[:,j] for j in xrange(p))
		ma = abs(ma)**2
		ar = abs(ar)**2
	psd[:,i] = (sigma[:,0]**2)*ma/ar
	psd_mid = np.median(psd,axis=0)
	psd_high = np.percentile(psd,upper,axis=0)
	psd_low = np.percentile(psd,lower,axis=0)
	return (psd_low,psd_high,psd_mid,f)

def get_greens_func(time, ar_roots, percentile):

	g_func = np.empty((time.shape[0], ar_roots.shape[0]), dtype = np.complex64)	
	lower = (100.0 - percentile)/2.0
	upper = (100.0 - lower)
	t = time.reshape(1,time.shape[0]).T
	g_func[:] = (np.exp(ar_roots[:,0]*t) - np.exp(ar_roots[:,1]*t))/(ar_roots[:,0] - ar_roots[:,1])

	gfunc_mid = np.median(g_func[:].real, axis = 1)
	gfunc_high = np.percentile(g_func[:].real, upper, axis = 1)
	gfunc_low = np.percentile(g_func[:].real, lower, axis = 1)

	return gfunc_low, gfunc_high, gfunc_mid, time

