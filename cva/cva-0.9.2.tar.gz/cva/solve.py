# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
#  Copyright (c) 2016, Robert Whitinger <cva_account@wmkt.com>
#
#  Distributed under the terms of the LGPL license either version 2.1 or
#  (at your option) any later version.
#
#  The full license is in the file LICENSE.txt, distributed with this software,
#  and is also available at <http://www.gnu.org/licenses/>
#-----------------------------------------------------------------------------
"""
cva.solve

A calculus of variations solver.

This module implements the CVA algorithm for the numerical computation of
minimum paths.
"""

from __future__ import division

# system libraries:
import sys
import numpy as np
import math
from copy import deepcopy
import time
import itertools

# project library
import cva

# Constants
PI = math.pi
TPI = 2.0*PI
EPS = sys.float_info.epsilon


# here we store this module's parameter set and make it accessible

# initialize default tuning parameters
_parms = {'tp_starting_trial_space_radius': 0.5,
          'tp_eps_multiplier': 100,
          'tp_straddles': 32,
          'tp_max_trials': 20,
          'trace_minpoint': False,
          'trace_straddle': False,
          'trace_refine': False
         }
def set_parm(parm_name, parm_value):
    """
    cva.solve.set_parm(parm_name, parm_value)
    """
    _parms[parm_name] = parm_value

def get_parm(parm_name):
    """
    parm_value = cva.solve.get_parm(parm_name)
    """
    return _parms[parm_name]

def list_parms():
    """
    keys = cva.solve.list_parms()
    """
    keys = _parms.keys()
    return keys

def select(function_model, function_metric):
    """
    cva.solve.select(function_model, function_metric)

    Parameters
    ----------
    function_model : function
        This parameter assigns a model.
    function_metric : function
        This parameter assigns a metric.

    Returns
    -------
    nothing

    Notes
    -----
    This function is called prior to cva.solve.run() invokation in order to
    specify a model with an associated metric.  See also cva.solve.run().

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    sb = (0.6,0.7)
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    path = cva.solve.run(sa,sb)

    In this example, a spherical model with a Euclidean distance metric
    are specified, and then with this configuration a minimal path is
    calculated and a minimal curve is returned.
    """
    _parms['G'] = function_model
    _parms['M'] = function_metric
    return

# The basic computational element finds a minimum of the objective functional
# over a successively smaller trial space.
def minpoint(sa, sb):
    """
    cva.solve.minpoint(sa, sb)

    Parameters
    ----------
    sa : array_like
        This parameter contains a starting point in the parameter space.
    sb : array_like
        This parameter contains an ending point in the parameter space.

    Returns
    -------
    sm : ndarray
        On return sm contains the minpoint between the starting point sa
        and the ending point sb.  Given the constraints of the specified
        model and metric.

    Notes
    -----
    This is the basic building block of the cva algorithm.

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    sb = (0.6,0.7)
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    sm = cva.solve.minpoint(sa,sb)
    """
    # we determine the dimension of our phase space by examining the sa point
    sa = np.asarray(sa)
    sb = np.asarray(sb)
    if np.allclose(sa, sb):
        return sa           # quick return if starting and ending are equal
    nparm = np.shape(sa)[0]
    # use Gramm-Schmidt to form an n-dimensional space perpendicular to
    # the secant line

    # step 1: form a non-orthogonal basis space including our secant vector
    basis = np.zeros((nparm, nparm))
    cartesian_space = np.zeros((nparm, nparm))
    for i in range(nparm):
        cartesian_space[i, i] = 1.0
    # our non-orthogonal basis must include the primary (secant) unit vector
    basis[0] = (sb - sa)/np.linalg.norm(sb - sa)
    # we select a the set of cartesian unit vectors by eliminating the worst choice
    worst_choice = np.argmax(np.abs(basis[0]))
    # then we list the indices of the best cartesian choices
    axis = [axis for axis in range(nparm) if axis != worst_choice]
    for i in range(1, nparm):
        # and use them to form the rest of our basis
        basis[i] = cartesian_space[axis[i-1]]
        if np.allclose(basis[i], basis[0]):
            raise ValueError('colinear vectors found in basis')

    # step 2: form an orthonormal basis including the secant vector
    perp = np.empty((nparm, nparm))
    perp[0] = basis[0]        # perp[0] is the secant unit vector
    for i in range(1, nparm):  # the Gramm-Schmidt summation
        perp[i] = basis[i]    # starting with the basis vector
        for j in range(i):    # then subtracting previous vector components
            perp[i] -= perp[j]*np.inner(basis[i], perp[j])/np.inner(perp[j], perp[j])
        perp[i] = perp[i]/np.linalg.norm(perp[i])   # normalize

    # step 3: starting with a midpoint and a radius, find the best path
    sm = (sb-sa)/2.0 + sa
    radius = np.linalg.norm(sb-sa)*_parms['tp_starting_trial_space_radius']
    # our trial space has 5**(n-1) points,
    # five points accross each axis centered on the current midpoint estimate
    trial_shape = []
    for i in range(nparm-1):
        trial_shape.append(5)
    trial_array_shape = deepcopy(trial_shape)
    trial_array_shape.append(nparm)
    # trial_space = np.zeros(trial_array_shape)     # the set of trial points
    # trial_integral = np.zeros(trial_shape)  # path summations for each trial point
    maxtries = _parms['tp_max_trials']
    while maxtries > 0 and radius > EPS*_parms['tp_eps_multiplier']:
        maxtries -= 1
        best_integral = np.infty
        # create a tuple of all possible trial index permutations
        trial_index_set = itertools.product(range(5), repeat=nparm-1)
        trial_space = np.zeros(trial_array_shape)     # the set of trial points
        trial_integral = np.zeros(trial_shape)  # path summations for each trial point
        for it in trial_index_set:    # loop over all trial permutations
            trial_space[it] = sm  # our trial point includes the center
            for i in range(nparm-1):  # and spans the basis coordinates
                trial_space[it] += radius*perp[i+1]*(it[i]-2)/2.0
                #print np.linalg.norm(radius*perp[i+1]*(it[i]-2)/2.0)
            trial_integral[it] = _parms['M'](sa, trial_space[it]) + _parms['M'](trial_space[it], sb)
            if trial_integral[it] < best_integral:
                best_integral = trial_integral[it]
                bestit = it
        # prepare new trial (center and radius) based on our best path
        if best_integral < np.infty:
            sm = trial_space[bestit]
            radius = radius/2
        else:
            print "no solution found"
        # tracing brings a performance penalty, it is turned off by default
        if _parms['trace_minpoint']:
            try:
                _parms['log_minpoint']
            except:
                _parms['log_minpoint'] = []
            log = deepcopy((sm, trial_space, trial_integral, radius))
            _parms['log_minpoint'].append(log)

    return sm


# utility procedure
def _strip_s(s, step):
    # strip uncalculated values from s
    i = 0
    s_temp = np.zeros((2**step+1, np.shape(s)[1]))
    for i in range(2**step+1):
        j = i*2**(_parms['steps']-step)
        s_temp[i] = s[j]
    return s_temp

def path_integral(s, step=False):
    """
    cva.solve.path_integral(s, step=False)

    Parameters
    ----------
    s : array_like
        This parameter specifies a path which is not necessarily minimal.
    step : int (optional)
        This parameter specifies the scope of the straddle operation.  The
        default False results in a path integral computation over all of s.

    Returns
    -------
    result : ndarray
        A value corresponding to the piecewise path summation of the curve
        defined in s.

    Notes
    -----
    none

    """
    if step:
        s = _strip_s(s, step)
    result = 0.0
    for i in range(s.shape[0]-1):
        result += _parms['M'](s[i], s[i+1])
    return result

def straddle(s, step):
    """
    cva.solve.straddle(s,step)

    An internal function called by cva.solve.run()

    Parameters
    ----------
    s : array_like
        This parameter specifies a path which is not necessarily minimal.
    step : int
        This parameter specifies the scope of the straddle operation.

    Returns
    -------
    s : ndarray
        On return s specifies a minimal path of 2**steps + 1 points.

    Notes
    -----
    The straddle operation uses minpoints to build convergent piecewise minimal
    paths.  This function is used primarily by cva.solve.run(), the primary
    entry point.  See cva.solve.run() for example usage.
    """
    try:
        N = _parms['N']
    except:
        N = len(s)-1
    incr = int(N/(2**step))
    for iteration in range(_parms['tp_straddles']):
        for k in range(1, int(N/incr), 2):
            a = (k-1)*incr
            b = (k+1)*incr
            s[int(k*N/(2**step))] = minpoint(s[a], s[b])
        for k in range(2, int(N/incr), 2):
            a = (k-1)*incr
            b = (k+1)*incr
            s[int(k*N/(2**step))] = minpoint(s[a], s[b])
        if _parms['trace_straddle']:
            try:
                _parms['log_straddle']
            except:
                _parms['log_straddle'] = []
            log = deepcopy((iter, s ))
            _parms['log_straddle'].append(log)
    return (s)

def refine(s, steps, silent):
    """
    cva.solve.refine(s, steps, silent)

    An internal function called by cva.solve.run()

    Parameters
    ----------
    s : array_like
        This parameter specifies a path.
    steps : int
        This parameter specifies the number of refinement operations to
        be performed.  Each refinement approximately doubles the number
        of points in the path.

    Returns
    -------
    s : ndarray
        On return s specifies a minimal path of 2**steps + 1 points.

    Notes
    -----
    The refinement operation uses straddles and minpoints to build
    convergent piecewise minimal paths of increasing length.  This function
    is used primarily by cva.solve.run(), the primary  entry point.
    See cva.solve.run() for example usage.
    """
    for step in range(1, steps+1):
        s = straddle(s, step)
        run_time = time.time() - _parms['start_time']
        if _parms['trace_refine']:
            try:
                _parms['log_refine']
            except:
                _parms['log_refine'] = []
            log = deepcopy((step, run_time, s ))
            _parms['log_refine'].append(log)
        if not silent:
            print "step %d:  path_integral = %.6f after %.3f seconds" % (step, path_integral(s, step), run_time)
    return s

def _choose_path(sa, sb):
    # for now we assume that the last parameter is periodic
    N = _parms['N']
    nparm = _parms['nparm']
    s = np.zeros((N+1, nparm))
    s[0] = sa
    s[N] = sb
    # we give the model a chance to declare its periodic axes

    # cause the model to report periodicity
    _parms['G'](sa)
    periodicity = cva.model.get_parm('periodicity')

    # check for a tuple of booleans
    # for now we only implement periodicity in the last parameter
    if periodicity[-1] == True:
        sm = (s[N]-s[0])/2.0 + s[0]
        dist = _parms['M'](sm, s[N])
        if s[0, nparm-1] < s[N, nparm-1]:
            sa_ext = deepcopy(s[0])
            sa_ext[nparm-1] += 1.0
            sm_ext = (s[N]-sa_ext)/2.0 + sa_ext
            dist_ext = _parms['M'](sm_ext, s[N])
            if dist_ext + EPS < dist:
                s[0, nparm-1] += 1.0
        else:
            sb_ext = deepcopy(s[N])
            sb_ext[nparm-1] += 1.0
            sm_ext = (sb_ext-s[0])/2.0 + s[0]
            dist_ext = _parms['M'](sm_ext, s[N])
            if dist_ext + EPS < dist:
                s[N, nparm-1] += 1.0
    return s

def run(sa, sb, steps=5, silent=False):
    """
    cva.solve.run(sa, sb, steps=5, silent=False)

    Parameters
    ----------
    sa : array_like
        This parameter contains a starting point in the parameter space.
    sb : array_like
        This parameter contains an ending point in the parameter space.
    steps : int, optional
        This parameter specifies the number of refinement steps to be
        executed.  Each step approximately doubles the number of points
        in the returned path.
    silent : bool, optional
        In the normal case, cva.solve.run() prints a runtime status
        report.  Setting silent = True will disable this reporting.

    Returns
    -------
    s : ndarray
        On return s contains a sequence of points in parameter space which
        define a minimal path for the given starting/ending points, metric,
        and model.  The length of s will be 2**(steps) + 1 points.

    Notes
    -----
    This is the primary entry point for the cva.solve module.  See also
    cva.solve.select().


    Examples
    --------
    import cva
    sa = (0.4,0.5)
    sb = (0.6,0.7)
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    path = cva.solve.run(sa,sb)

    In this example, the parameterization points sa and sb are mapped into
    their corresponding points on the surface of a unit sphere, and a
    33 point minimal curve is returned.
    """
    # we deduce the required parameters from the user's input
    # the length of the starting point sa is the dimension of our phase space
    N = 2**steps            # length of path array is N+1
    nparm = len(sa)
    ndim = len(sa)+1        # in this release we support the case of R^{N-1} surfaces in R^N space
    set_parm('start_time', time.time())
    set_parm('sa', np.asarray(sa))
    set_parm('sb', np.asarray(sb))
    set_parm('steps', steps)
    set_parm('N', N)
    set_parm('ndim', ndim)
    set_parm('nparm', nparm)
    set_parm('silent', silent)

    # we create a suitably sized path array and set its starting and ending points
    s = _choose_path(sa, sb)
    s = refine(s, steps, silent)
    return s


if __name__ == "__main__":

    print "running cva/solve.py"
