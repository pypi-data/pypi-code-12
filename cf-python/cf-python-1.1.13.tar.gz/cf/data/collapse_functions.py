from numpy import allclose    as numpy_allclose
from numpy import amax        as numpy_amax
from numpy import amin        as numpy_amin
from numpy import any         as numpy_any
from numpy import array       as numpy_array
from numpy import asanyarray  as numpy_asanyarray
from numpy import average     as numpy_average
from numpy import bool_       as numpy_bool_
from numpy import copy        as numpy_copy
from numpy import empty       as numpy_empty
from numpy import expand_dims as numpy_expand_dims
from numpy import integer     as numpy_integer
#from numpy import isclose     as numpy_isclose
from numpy import maximum     as numpy_maximum
from numpy import minimum     as numpy_minimum
from numpy import sum         as numpy_sum
from numpy import where       as numpy_where
from numpy import zeros       as numpy_zeros
import numpy

from numpy.ma import array        as numpy_ma_array
from numpy.ma import average      as numpy_ma_average
from numpy.ma import expand_dims  as numpy_ma_expand_dims
from numpy.ma import isMA         as numpy_ma_isMA
from numpy.ma import masked       as numpy_ma_masked
from numpy.ma import masked_less  as numpy_ma_masked_less
from numpy.ma import masked_where as numpy_ma_masked_where
from numpy.ma import nomask       as numpy_ma_nomask
from numpy.ma import where        as numpy_ma_where

from functools import partial
from itertools import izip
from operator import mul as mul

from ..functions import broadcast_array

def psum(x, y):
    '''

Add two arrays element-wise.

If either or both of the arrays are masked then the output array is
masked only where both input arrays are masked.

:Parameters:

    x : numpy array-like
        *Might be updated in place*.

    y : numpy array-like
        Will not be updated in place.

:Returns:

    out : numpy array

:Examples:

>>> c = psum(a, b)

'''
    if numpy_ma_isMA(x):
        if numpy_ma_isMA(y):
            # x and y are both masked
            x_mask = x.mask
            x  = x.filled(0)
            x += y.filled(0)
            x = numpy_ma_array(x, mask=x_mask & y.mask, copy=False)
        else:
            # Only x is masked
            x = x.filled(0)
            x += y
    elif numpy_ma_isMA(y):
        # Only y is masked
        x += y.filled(0)
    else:
        # x and y are both unmasked
        x += y

    return x
#--- End: def

def pmax(x, y):
    '''

:Parameters:

    x : array-like
        May be updated in place and should not be used again.

    y : array-like
        Will not be updated in place.

:Returns:

    out : numpy array

'''
    if numpy_ma_isMA(x):
        if numpy_ma_isMA(y):
            # x and y are both masked
            z = numpy_maximum(x, y)
            z = numpy_ma_where(x.mask & -y.mask, y, z)
            x = numpy_ma_where(y.mask & -x.mask, x, z)
            if x.mask is numpy_ma_nomask: #not numpy_any(x.mask):
                x = numpy_array(x)
        else:
            # Only x is masked
            z = numpy_maximum(x, y)
            x = numpy_ma_where(x.mask, y, z)
            if x.mask is numpy_ma_nomask: #not numpy_any(x.mask):
                x = numpy_array(x)
    elif numpy_ma_isMA(y):
        # Only y is masked
        z = numpy_maximum(x, y)
        x = numpy_ma_where(y.mask, x, z)
        if x.mask is numpy_ma_nomask: #not numpy_any(x.mask):
            x = numpy_array(x)
    else:
        # x and y are both unmasked
        if not x.ndim:
            # Make sure that we have a numpy array (as opposed to,
            # e.g. a numpy.float64)
            x = numpy_asanyarray(x)

        numpy_maximum(x, y, out=x)

    return x
#--- End: def

def pmin(x, y):
    '''

:Parameters:

    x : numpy array
        May be updated in place and should not be used again.

    y : numpy array
        Will not be updated in place.

:Returns:

    out : numpy array

'''
    if numpy_ma_isMA(x):
        if numpy_ma_isMA(y):
            # x and y are both masked
            z = numpy_minimum(x, y)
            z = numpy_ma_where(x.mask & -y.mask, y, z)
            x = numpy_ma_where(y.mask & -x.mask, x, z)
            if x.mask is numpy_ma_nomask:
                x = numpy_array(x)
        else:
            # Only x is masked
            z = numpy_minimum(x, y)
            x = numpy_ma_where(x.mask, y, z)
            if x.mask is numpy_ma_nomask:
                x = numpy_array(x)
    elif numpy_ma_isMA(y):
        # Only y is masked  
        z = numpy_minimum(x, y)
        x = numpy_ma_where(y.mask, x, z)
        if x.mask is numpy_ma_nomask:
            x = numpy_array(x)
    else:
        # x and y are both unmasked 
        if not x.ndim:
            # Make sure that we have a numpy array (as opposed to,
            # e.g. a numpy.float64)
            x = numpy_asanyarray(x)
        
        numpy_minimum(x, y, out=x)

    return x
#--- End: def

def mask_where_too_few_values(Nmin, N, x):
    '''

Mask elements of N and x where N is strictly less than Nmin.

:Parameters:

    Nmin : int

    N : numpy array

    x : numpy array

:Returns:

    out : tuple
        A 2-tuple containing *N* and *x*, both masked where *N* is
        strictly less than *Nmin*.

'''
    if N.min() < Nmin:
        mask = N < Nmin
        N = numpy_ma_array(N, mask=mask, copy=False, shrink=False)
        x = numpy_ma_array(x, mask=mask, copy=False, shrink=True)

    return N, x
#--- End: def

#---------------------------------------------------------------------
# Maximum
#---------------------------------------------------------------------
def max_f(a, axis=None, masked=False):
    '''
        
Return the maximum of an array, or the maxima of an array along an
axis.

:Parameters:

    a : numpy array_like
        Input array

    axis : int, optional
        Axis along which to operate. By default, flattened input is
        used.

    masked : bool

:Returns:

    out : 2-tuple of numpy arrays
        The sample sizes and the maxima.

'''
    N    = sample_size_f(a, axis=axis, masked=masked)
    amax = numpy_amax(a, axis=axis)

    if not amax.ndim:
        # Make sure that we have a numpy array (as opposed to, e.g. a
        # numpy.float64)
        amax = numpy_asanyarray(amax)

    return N, amax
#--- End: def

def max_fpartial(out, out1=None):
    N, amax = out

    if out1 is not None:
        N1, amax1 = out1
        N    = psum(N, N1)
        amax = pmax(amax, amax1)
    #--- End: if

    return N, amax
#--- End: def

def max_ffinalise(out, sub_samples=None):
    '''
    sub_samples : *optional*
        Ignored.

'''
    return mask_where_too_few_values(1, *out)
#--- End: def

#---------------------------------------------------------------------
# Minimum
#---------------------------------------------------------------------
def min_f(a, axis=None, masked=False):
    '''
       
Return the minimum of an array, or the minima of an array along an
axis.

:Parameters:

    a : numpy array_like
        Input array

    axis : int, optional
        Axis along which to operate. By default, flattened input is
        used.

    masked : bool

:Returns:

    out : 2-tuple of numpy arrays
        The sample sizes and the minima.
     
'''
    N    = sample_size_f(a, axis=axis, masked=masked)
    amin = numpy_amin(a, axis=axis)

    if not amin.ndim:
        # Make sure that we have a numpy array (as opposed to, e.g. a
        # numpy.float64)
        amin = numpy_asanyarray(amin)

    return N, amin
#--- End: def

def min_fpartial(out, out1=None):
    '''
'''
    N, amin = out
    
    if out1 is not None:
        N1, amin1 = out1
        N    = psum(N, N1)
        amin = pmin(amin, amin1)
    #--- End: if

    return N, amin
#--- End: def

def min_ffinalise(out, sub_samples=None):
    '''
    sub_samples : *optional*
        Ignored.

'''
    return mask_where_too_few_values(1, *out)
#--- End: def

#---------------------------------------------------------------------
# Mean
#---------------------------------------------------------------------
def mean_f(a, axis=None, weights=None, masked=False):
    '''

The weighted average along the specified axes.

:Parameters:

    a : array-like
        Input array. Not all missing data

    axis : int, optional
        Axis along which to operate. By default, flattened input is
        used.

    weights : array-like, optional

    masked : bool, optional

    kwargs : ignored

:Returns:

    out : tuple
        3-tuple.

'''
    if masked:
        average = numpy_ma_average
    else:
        average = numpy_average

    avg, sw = average(a, axis=axis, weights=weights, returned=True)
        
    if not avg.ndim:
        avg = numpy_asanyarray(avg)
        sw  = numpy_asanyarray(sw)

    if weights is None:
        N = sw.copy()
    else:
        N = sample_size_f(a, axis=axis, masked=masked)

    return N, avg, sw
#--- End: def

def mean_fpartial(out, out1=None):
    '''
'''
    N, avg, sw = out
    
    if out1 is None:
        avg *= sw
    else:
        N1, avg1, sw1 = out1

        avg1 *= sw1
        
        N   = psum(N, N1)
        avg = psum(avg, avg1)
        sw  = psum(sw, sw1)
    #--- End: if

    return N, avg, sw
#--- End: def

def mean_ffinalise(out, sub_samples=None):
    '''

    sub_samples : *optional*
        Ignored.

'''
    N, avg, sw = out

    if sub_samples:
        avg /= sw

    return mask_where_too_few_values(1, N, avg)
#--- End: def

#---------------------------------------------------------------------
# Mid range: Average of maximum and minimum 
#---------------------------------------------------------------------
def mid_range_f(a, axis=None, masked=False):
    '''
        
Return the minimum and maximum of an array or the minima and maxima
along an axis.

``mid_range_f(a, axis=axis)`` is equivalent to ``(numpy.amin(a,
axis=axis), numpy.amax(a, axis=axis))``

:Parameters:

    a : numpy array_like
        Input array

    axis : int, optional
        Axis along which to operate. By default, flattened input is
        used.

    kwargs : ignored

:Returns:

    out : tuple
        The minimum and maximum inside a 2-tuple.

'''
    N    = sample_size_f(a, axis=axis, masked=masked)
    amin = numpy_amin(a, axis=axis)
    amax = numpy_amax(a, axis=axis)

    if not amin.ndim:
        # Make sure that we have a numpy array (as opposed to, e.g. a
        # numpy.float64)
        amin = numpy_asanyarray(amin)
        amax = numpy_asanyarray(amax)

    return N, amin, amax
#--- End: def

def mid_range_fpartial(out, out1=None):
    '''
'''
    N, amin, amax = out

    if out1 is not None:
        N1, amin1, amax1 = out1

        N    = psum(N, N1)
        amin = pmin(amin, amin1)
        amax = pmax(amax, amax1)
    #--- End: if

    return N, amin, amax
#--- End: def

def mid_range_ffinalise(out, sub_samples=None):
    '''

:Parameters:

    out : ordered sequence

    amin : numpy.ndarray

    amax : numpy.ndarray

    sub_samples : *optional*
        Ignored.

'''
    N, amin, amax = out
    
    # Cast bool, unsigned int, and int to float64
    if issubclass(amax.dtype.type, (numpy_integer, numpy_bool_)):
        amax = amax.astype(float)

    amax += amin
    amax *= 0.5

    return mask_where_too_few_values(1, N, amax)
#--- End: def

#---------------------------------------------------------------------
# Range: Absolute difference between maximum and minimum 
#---------------------------------------------------------------------
range_f        = mid_range_f
range_fpartial = mid_range_fpartial

def range_ffinalise(out, sub_samples=None):
    '''
Absolute difference between maximum and minimum 

:Parameters:

    out : ordered sequence

    sub_samples : *optional*
        Ignored.

'''
    N, amin, amax = out
  
    amax -= amin
      
    return mask_where_too_few_values(1, N, amax)
#--- End: def

#---------------------------------------------------------------------
# Sample size
#---------------------------------------------------------------------
def sample_size_f(a, axis=None, masked=False):
    '''

    axis : int, optional
        non-negative
'''
    if masked:        
        N = numpy_sum(-a.mask, axis=axis, dtype=float)
        if not N.ndim:
            N = numpy_asanyarray(N)
    else:
        if axis is None:
            N = numpy_array(a.size, dtype=float)
        else:
            shape = a.shape
            N = numpy_empty(shape[:axis]+shape[axis+1:], dtype=float)
            N[...] = shape[axis]
    #--- End: if

    return N
#--- End: def

def sample_size_fpartial(N, out1=None):
    '''

:Parameters:

    N : numpy array

:Returns:

    out : numpy array

'''
    if out1 is not None:
        N1 = out1
        N = psum(N, N1)

    return N
#--- End: def

def sample_size_ffinalise(N, sub_samples=None):
    '''

:Parameters:

    N : numpy array

    sub_samples : *optional*
        Ignored.

:Returns:

    out : tuple
        A 2-tuple containing *N* twice.

'''
    return N, N
#--- End: def

#---------------------------------------------------------------------
# Sum
#---------------------------------------------------------------------
def sum_f(a, axis=None, masked=False):
    '''

Return the sum of an array or the sum along an axis.

``sum_f(a, axis=axis)`` is equivalent to ``(numpy.sum(a,
axis=axis),)``

:Parameters:

    array : numpy array-like
        Input array

    axis : int, optional
        Axis along which to operate. By default, flattened input is
        used.

    kwargs : ignored

:Returns:

    out : tuple
        2-tuple

'''
    N    = sample_size_f(a, axis=axis, masked=masked)
    asum = a.sum(axis=axis)

    if not asum.ndim:
        asum = numpy_asanyarray(asum)

    return N, asum
#--- End: def

def sum_fpartial(out, out1=None):
    '''
'''
    N, asum = out

    if out1 is not None:
        N1, asum1 = out1

        N    = psum(N, N1)
        asum = psum(asum, asum1)
    #--- End: if

    return N, asum
#--- End: def

def sum_ffinalise(out, sub_samples=None):
    '''
    sub_samples : *optional*
        Ignored.
'''
    return mask_where_too_few_values(1, *out)
#--- End: def

#---------------------------------------------------------------------
# Sum of weights
#---------------------------------------------------------------------
def sw_f(a, axis=None, masked=False, weights=None):
    '''
'''
    N = sample_size_f(a, axis=axis, masked=masked)

    if weights is not None:
        if weights.ndim < a.ndim:
            weights = broadcast_array(weights, a.shape)

        if masked:
            weights = numpy_ma_array(weights, mask=a.mask, copy=False)

        sw = weights.sum(axis=axis)
        if not sw.ndim:
            sw = numpy_asanyarray(sw)
    else:
        sw = N.copy()

    return N, sw
#--- End: def

sw_fpartial  = sum_fpartial
sw_ffinalise = sum_ffinalise

#---------------------------------------------------------------------
# Sum of squares of weights
#---------------------------------------------------------------------
def sw2_f(a, axis=None, masked=False, weights=None):
    '''
'''
    N = sample_size_f(a, axis=axis, masked=masked)

    if weights is not None:
        if weights.ndim < a.ndim:
            weights = broadcast_array(weights, a.shape)
            
        if masked:                    
            weights = numpy_ma_array(weights, mask=a.mask, copy=False)

        sw2 = (weights*weights).sum(axis=axis)
        if not sw2.ndim:
            sw2 = numpy_asanyarray(sw2)
    else:
        sw2 = N.copy()
            
    return N, sw2
#--- End: def

sw2_fpartial  = sum_fpartial
sw2_ffinalise = sum_ffinalise

#---------------------------------------------------------------------
# Variance
#---------------------------------------------------------------------
def var_f(a, axis=None, weights=None, masked=False, ddof=1, f=None):
    '''

''' 
    # ----------------------------------------------------------------
    # Find the minimum and maximum values of the weights if required
    # ----------------------------------------------------------------
    if not f and weights is not None and ddof:
        if weights.ndim <= 1:
            # Weights are 1-d
            wmin = weights.min()
            wmax = weights.max()
        else:
            # Weights have the same shape as a
            wmin = weights.min(axis=axis)
            wmax = weights.max(axis=axis)
    else:
        wmin  = None
        wmax  = None

    # ----------------------------------------------------------------
    # Methods:
    #
    # http://en.wikipedia.org/wiki/Standard_deviation#Population-based_statistics
    # http://en.wikipedia.org/wiki/Weighted_mean#Weighted_sample_variance
    # ----------------------------------------------------------------
    N, avg, sw = mean_f(a, weights=weights, axis=axis, masked=masked)
 
    if axis is not None and avg.size > 1:
        # We collapsed over a single axis and the array has 2 or more
        # axes, so add an extra size 1 axis to the mean so that
        # broadcasting works when we calculate the variance.
        reshape_avg = True
        if masked:
            expand_dims = numpy_ma_expand_dims
        else:
            expand_dims = numpy_expand_dims

        avg = expand_dims(avg, axis)
    else:
        reshape_avg = False

    var  = a - avg
    var *= var

    if masked:
        average = numpy_ma_average
    else:
        average = numpy_average

    var = average(var, axis=axis, weights=weights)
    
    if reshape_avg:
        shape = avg.shape        
        avg = avg.reshape(shape[:axis] + shape[axis+1:])

    if not var.ndim:
        var = numpy_asanyarray(var)

    return N, var, avg, sw, ddof, f, wmin, wmax
#--- End: def

def var_fpartial(out, out1=None):
    '''
'''
    N, var, avg, sw, ddof, f, wmin, wmax = out

    if out1 is None:
        # ------------------------------------------------------------
        # var = sw(var+avg**2)
        # avg = sw*avg
        # ------------------------------------------------------------
        var += avg*avg
        var *= sw 
        avg *= sw 
    else:       
        # ------------------------------------------------------------
        # var = var + sw1(var1+avg1**2)
        # avg = avg + sw1*avg1
        # sw  = sw + sw1
        # ------------------------------------------------------------
        N1, var1, avg1, sw1, ddof, f, wmin1, wmax1 = out1

        N = psum(N, N1)
        
        var1 += avg1*avg1
        var1 *= sw1
        avg1 *= sw1

        var = psum(var, var1)
        avg = psum(avg, avg1)
        sw  = psum(sw , sw1)

        if wmin is not None:
            wmin = pmin(wmin, wmin1)
            wmax = pmax(wmax, wmax1)
    #--- End: def

    return N, var, avg, sw, ddof, f, wmin, wmax
#--- End: def

def var_ffinalise(out, sub_samples=None):
    '''
    '''
    N, var, avg, sw, ddof, f, wmin, wmax = out

    N, var = mask_where_too_few_values(max(2, ddof+1), N, var)

    if sub_samples:
        # ----------------------------------------------------------------
        # The global biased variance = {[SUM(psw(pv+pm**2)]/sw} - m**2        
        # 
        #   where psw = partial sum of weights
        #         pv  = partial biased variance 
        #         pm  = partial mean            
        #         sw  = global sum of weights
        #         m   = global mean             
        #
        # Currently: var = SUM(psw(pv+pm**2)
        #            avg = sw*m
        #
        # http://en.wikipedia.org/wiki/Standard_deviation#Population-based_statistics
        # ----------------------------------------------------------------
        avg /= sw
        avg *= avg
        var /= sw
        var -= avg
    #--- End: if

    # ----------------------------------------------------------------
    # var is now the global variance with sw degrees of freedom
    # ----------------------------------------------------------------

    if ddof:
        if f:
            sw *= f
        elif wmin is not None:
           # ---------------------------------------------------------
           # The global variance is weighted and needs to be
           # calculated with greater than 0 delta degrees of
           # freedom. The sum of weights (sw) needs to be adjusted:
           #
           # sw = f*sw (approximately!)
           # 
           # where f = smallest positive number whose products with
           #           the smallest and largest weights and the sum of
           #           weights are all integers
           # ---------------------------------------------------------
           wmin = wmin.astype(float)
           wmax = wmax.astype(float)
           sw   = sw.astype(float)
           
           wmax /= wmin
           sw   /= wmin
           
           if (not numpy_allclose(wmax, wmax.astype(int), rtol=1e-05, atol=1e-08) or
               not numpy_allclose(sw  , sw.astype(int)  , rtol=1e-05, atol=1e-08)):
           
               m = numpy_zeros(wmax.shape, dtype=int)            
               n = 2
               while True:
                   nwmax = n*wmax
                   nsw   = n*sw
                   ccc = (m == 0)
                   ccc &= numpy.isclose(nwmax, nwmax.astype(int), rtol=1e-05, atol=1e-08)
                   ccc &= numpy.isclose(nsw  , nsw.astype(int)  , rtol=1e-05, atol=1e-08)
                   m = numpy_where(ccc, n, m)
                   if m.min():
                       # Every element of m has been set (to an integer
                       # greater than 1), so we are done.
                       break                
                   
                   # Some elements of m have not been set, so try the
                   # next multiplier.
                   n += 1
               #--- End: while
               sw *= m
           #--- End: if
        #--- End: if
    
        # ------------------------------------------------------------
        # Adjust the variance for fewer than sw degrees of freedom:
        #
        # var = var*sw/(sw-ddof)
        # ------------------------------------------------------------
        var *= sw
        sw -= ddof
        var /= sw
    #--- End: if

    return N, var
#--- End: def

#---------------------------------------------------------------------
# Standard deviation
#---------------------------------------------------------------------
sd_f        = var_f
sd_fpartial = var_fpartial

def sd_ffinalise(out, sub_samples=None):
    '''

:Parameters:

    out : tuple
        A 2-tuple

    sub_samples : *optional*
        Ignored.


'''
    N, sd = var_ffinalise(out, sub_samples)
    
    sd **= 0.5
    
    return N, sd
#--- End: def
