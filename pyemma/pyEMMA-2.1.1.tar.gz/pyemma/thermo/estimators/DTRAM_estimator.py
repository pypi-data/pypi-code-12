# This file is part of PyEMMA.
#
# Copyright (c) 2015 Computational Molecular Biology Group, Freie Universitaet Berlin (GER)
#
# PyEMMA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import numpy as _np
from six.moves import range
from pyemma._base.estimator import Estimator as _Estimator
from pyemma.thermo import MEMM as _MEMM
from pyemma.msm import MSM as _MSM
from pyemma.util import types as _types
from pyemma.util.units import TimeUnit as _TimeUnit
from msmtools.estimation import largest_connected_set as _largest_connected_set
from thermotools import dtram as _dtram
from thermotools import wham as _wham
from thermotools import util as _util

__author__ = 'noe, wehmeyer'


class DTRAM(_Estimator, _MEMM):
    r""" Discrete Transition(-based) Reweighting Analysis Method

    Parameters
    ----------
    bias_energies_full : ndarray(K, n)
        bias_energies_full[j,i] is the bias energy for each discrete state i at thermodynamic
        state j.
    lag : int
        Integer lag time at which transitions are counted.
    maxiter : int, optional, default=10000
        The maximum number of self-consistent iterations before the estimator exits unsuccessfully.
    maxerr : float, optional, default=1E-15
        Convergence criterion based on the maximal free energy change in a self-consistent
        iteration step.
    dt_traj : str, optional, default='1 step'
        Description of the physical time corresponding to the lag. May be used by analysis
        algorithms such as plotting tools to pretty-print the axes. By default '1 step', i.e.
        there is no physical time unit.  Specify by a number, whitespace and unit. Permitted
        units are (* is an arbitrary string):

        |  'fs',   'femtosecond*'
        |  'ps',   'picosecond*'
        |  'ns',   'nanosecond*'
        |  'us',   'microsecond*'
        |  'ms',   'millisecond*'
        |  's',    'second*'
    save_convergence_info : int, optional, default=0
        Every save_convergence_info iteration steps, store the actual increment
        and the actual loglikelihood; 0 means no storage.
    init : str, optional, default=None
        Use a specific initialization for self-consistent iteration:

        | None:    use a hard-coded guess for free energies and Lagrangian multipliers
        | 'wham':  perform a short WHAM estimate to initialize the free energies
    TODO: count_mode, connectivity

    Example
    -------
    >>> from pyemma.thermo import DTRAM
    >>> import numpy as np
    >>> B = np.array([[0, 0],[0.5, 1.0]])
    >>> dtram = DTRAM(B, 1)
    >>> traj1 = np.array([[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,1,1,0,0,0]]).T
    >>> traj2 = np.array([[1,1,1,1,1,1,1,1,1,1],[0,1,0,1,0,1,1,0,0,1]]).T
    >>> dtram = dtram.estimate([traj1, traj2])
    >>> dtram.log_likelihood() # doctest: +ELLIPSIS
    -9.805...
    >>> dtram.count_matrices # doctest: +SKIP
    array([[[5, 1],
            [1, 2]],

           [[1, 4],
            [3, 1]]], dtype=int32)
    >>> dtram.stationary_distribution # doctest: +ELLIPSIS
    array([ 0.38...,  0.61...])
    >>> dtram.meval('stationary_distribution') # doctest: +ELLIPSIS
    [array([ 0.38...,  0.61...]), array([ 0.50...,  0.49...])]
    """
    def __init__(
        self, bias_energies_full, lag, count_mode='sliding', connectivity='largest',
        maxiter=10000, maxerr=1E-15, dt_traj='1 step', save_convergence_info=0, init=None):
        # set all parameters
        self.bias_energies_full = _types.ensure_ndarray(bias_energies_full, ndim=2, kind='numeric')
        self.lag = lag
        assert count_mode == 'sliding', 'Currently the only implemented count_mode is \'sliding\''
        self.count_mode = count_mode
        assert connectivity == 'largest', 'Currently the only implemented connectivity is \'largest\''
        self.connectivity = connectivity
        assert init in (None, 'wham'), 'Currently only None and \'wham\' are supported'
        self.init = init
        self.dt_traj = dt_traj
        self.maxiter = maxiter
        self.maxerr = maxerr
        self.save_convergence_info = save_convergence_info
        # set derived quantities
        self.nthermo, self.nstates_full = bias_energies_full.shape
        self.timestep_traj = _TimeUnit(dt_traj)
        # set iteration variables
        self.therm_energies = None
        self.conf_energies = None
        self.log_lagrangian_mult = None

    def _estimate(self, trajs):
        """
        Parameters
        ----------
        trajs : ndarray(T, 2) or list of ndarray(T_i, 2)
            Thermodynamic trajectories. Each trajectory is a (T_i, 2)-array
            with T_i time steps. The first column is the thermodynamic state
            index, the second column is the configuration state index.

        """
        # format input if needed
        if isinstance(trajs, _np.ndarray):
            trajs = [trajs]
        # validate input
        assert _types.is_list(trajs)
        for ttraj in trajs:
            _types.assert_array(ttraj, ndim=2, kind='numeric')
            assert _np.shape(ttraj)[1] >= 2

        # harvest transition counts
        self.count_matrices_full = _util.count_matrices(
            [_np.ascontiguousarray(t[:, :2]).astype(_np.intc) for t in trajs], self.lag,
            sliding=self.count_mode, sparse_return=False, nstates=self.nstates_full)
        # harvest state counts (for WHAM)
        self.state_counts_full = _util.state_counts(
            trajs, nthermo=self.nthermo, nstates=self.nstates_full)

        # restrict to connected set
        C_sum = self.count_matrices_full.sum(axis=0)
        # TODO: use improved cset
        cset = _largest_connected_set(C_sum, directed=True)
        self.active_set = cset
        # correct counts
        self.count_matrices = self.count_matrices_full[:, cset[:, _np.newaxis], cset]
        self.count_matrices = _np.require(
            self.count_matrices, dtype=_np.intc ,requirements=['C', 'A'])
        # correct bias matrix
        self.bias_energies = self.bias_energies_full[:, cset]
        self.bias_energies = _np.require(
            self.bias_energies, dtype=_np.float64 ,requirements=['C', 'A'])
        # correct state counts
        self.state_counts = self.state_counts_full[:, cset]
        self.state_counts = _np.require(self.state_counts, dtype=_np.intc ,requirements=['C', 'A'])

        # run initialisation
        if self.init is not None:
            if self.init == 'wham':
                self.therm_energies, self.conf_energies, _increments, _loglikelihoods = \
                    _wham.estimate(
                        self.state_counts, self.bias_energies,
                        maxiter=5000, maxerr=1.0E-8, save_convergence_info=0,
                        therm_energies=self.therm_energies, conf_energies=self.conf_energies)

        # run estimator
        self.therm_energies, self.conf_energies, self.log_lagrangian_mult, \
            self.increments, self.loglikelihoods = _dtram.estimate(
                self.count_matrices, self.bias_energies,
                maxiter=self.maxiter, maxerr=self.maxerr,
                log_lagrangian_mult=self.log_lagrangian_mult,
                conf_energies=self.conf_energies,
                save_convergence_info=self.save_convergence_info)

        # compute models
        models = [_dtram.estimate_transition_matrix(
            self.log_lagrangian_mult, self.bias_energies, self.conf_energies,
            self.count_matrices, _np.zeros(
                shape=self.conf_energies.shape, dtype=_np.float64), K) for K in range(self.nthermo)]
        self.model_active_set = [_largest_connected_set(msm, directed=False) for msm in models]
        models = [_np.ascontiguousarray(
            (msm[lcc, :])[:, lcc]) for msm, lcc in zip(models, self.model_active_set)]

        # set model parameters to self
        self.set_model_params(
            models=[_MSM(msm, dt_model=self.timestep_traj.get_scaled(self.lag)) for msm in models],
            f_therm=self.therm_energies, f=self.conf_energies)

        # done
        return self

    def log_likelihood(self):
        return _dtram.get_loglikelihood(
            self.count_matrices,
            _dtram.estimate_transition_matrices(
                self.log_lagrangian_mult,
                self.bias_energies,
                self.conf_energies,
                self.count_matrices,
                _np.zeros(shape=self.conf_energies.shape, dtype=_np.float64)))
