import copy
import logging

import numpy as np
import scipy.signal
import scipy.stats

import auroraplot as ap
import auroraplot.dt64tools as dt64

logger = logging.getLogger(__name__)

def idl_filter_design(f_low, f_high, gibbs=-50, n=1):
    f_stop = (f_high < f_low)

    if gibbs < 0:
        gibbs = -gibbs

    if gibbs < 21:
        alpha = 0
    elif gibbs >= 50:
        alpha = 0.1102 * (gibbs-8.7)
    else:
        alpha = 0.5842 * np.power(gibbs-21, 0.4) + (0.07886 * (gibbs-21))
        
    arg = (np.arange(np.floor(n)) + 1) / n
    coef = np.i0(alpha * np.sqrt(1.0 - np.power(arg, 2.0))) / np.i0(alpha)
    t = (np.arange(np.floor(n)) + 1) * np.pi
    coef *= (np.sin(t * f_high) - np.sin(t * f_low)) / t

    #print('coef ' + repr(coef))
    r = list(coef[::-1])
    #print(r)
    r.append(f_high - f_low + f_stop)
    #print(r)
    r.extend(coef)
    #print(r)
    return np.array(r)



def samnet_filter(obj, p_short, p_long):
    cadence = obj.get_cadence()
    if cadence is None:
        raise Exception('Data must be spaced regularly')
    
    cadence_s = cadence / np.timedelta64(1, 's')
    f_nyquist = 1 / (2 * cadence_s) # in Hz

    p_short_s = p_short / np.timedelta64(1, 's')
    p_long_s = p_long / np.timedelta64(1, 's')

    if p_short_s > 2 * cadence_s:
        f_high = 1 / (f_nyquist * p_short_s)
    else:
        f_high = 1

    if p_long_s > 2 * cadence_s:
        f_low = 1 / (f_nyquist * p_long_s)
    else:
        f_low = 0
        
    gibbs = 76.8345
    filter_terms = float(np.fix(3.0 * f_nyquist * 
                                np.max([p_short_s, p_long_s])))
    coeffs = idl_filter_design(f_low, f_high, gibbs, filter_terms)
    nc = len(coeffs)


    r = copy.deepcopy(obj)
    r.data = np.tile(np.nan, obj.data.shape)

    for n in xrange(r.data.shape[0]):
        # Filter in forward and reverse direction
        fdata = scipy.signal.lfilter(coeffs, 1, obj.data[n])
        frdata = scipy.signal.lfilter(coeffs, 1, obj.data[n][::-1])
        print(repr(fdata))
        print(len(fdata))
        # Copy forward-filtered data
        print('filter terms: ' + repr(filter_terms))
        fdata[filter_terms:]
        r.data[n][:-filter_terms] = fdata[filter_terms:]

        # Insert reverse-filtered data at start (and reverse back)
        print('nc: ' + str(nc))
        print(repr(frdata.size))
        print(repr((frdata[-nc:]).size))
        tmp = frdata[-nc:]
        print('len tmp: ' + str(tmp.size))
        r.data[n][:nc] = tmp[::-1]

        # Is this needed?
        r.data[n][:filter_terms] = np.nan
        r.data[n][-filter_terms:] = np.nan
        
    return r


def calc_power(obj, cadence, average=scipy.stats.nanmean):
    r = copy.deepcopy(obj)
    N = int(np.ceil((obj.end_time - obj.start_time) / cadence))
    print(N)
    rdata = np.tile(np.nan, (obj.data.shape[0], N))
    r.sample_start_time = obj.start_time + (np.arange(N) * cadence)
    r.sample_end_time = r.sample_start_time + cadence
    r.nominal_cadence = cadence
    
    smt = dt64.mean(obj.sample_start_time, obj.sample_end_time)
    for n in xrange(N):
        for cn in xrange(rdata.shape[0]):
            tidx = np.logical_and(smt >= r.sample_start_time[n],
                                  smt < r.sample_end_time[n])
            rdata[cn][n] \
                = np.sqrt(average(np.power(obj.data[cn][tidx], 
                                                       2.0)))
    r.data = rdata
    return r
