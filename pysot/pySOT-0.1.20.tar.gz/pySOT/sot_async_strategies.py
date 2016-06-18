"""
.. module:: sot_async_strategies
   :synopsis: Parallel asynchronous SRBF optimization strategy
.. moduleauthor:: David Bindel <bindel@cornell.edu>
"""

from __future__ import print_function
import numpy as np
import math
from experimental_design import SymmetricLatinHypercube, LatinHypercube
from sampling_methods import CandidateDYCORS
from poap.strategy import BaseStrategy, Proposal, EvalRecord
import logging
from rbf_surfaces import CubicRBFSurface
from rbf_interpolant import RBFInterpolant
from utils import *
from rs_capped import *
# Get module-level logger
logger = logging.getLogger(__name__)


class AsyncStrategyNoConstraints(BaseStrategy):
    """Parallel asynchronous SRBF optimization strategy.

    In the asynchronous version of SRBF, workers are given function
    evaluations to start on as soon as they become available (unless
    the intial experiment design has been assigned but not completed).
    As evaluations are completed, different actions are taken depending
    on how recent they are.  A "fresh" value is one that was assigned
    since the last time the sampling radius was checked; an "old"
    value is one that was assigned before the last check of the sampling
    radius, but since the last restart; and an "ancient" value is one
    that was assigned before the last restart.  Only fresh values are
    used in adjusting the sampling radius.  Fresh or old values are
    used in determing the best point found since restart (used for
    the center point for sampling).  Any value can be incorporated into
    the response surface.  Sample points are chosen based on a merit
    function that depends not only on the response surface and the distance
    from any previous sample points, but also on the distance from any
    pending sample points.

    Once the budget of maxeval function evaluations have been assigned,
    no further evaluations are assigned to processors.  The code returns
    once all evaluations are completed.
    """

    def __init__(self, worker_id, data, response_surface, maxeval,
                 exp_design=None, sampling_method=None, extra=None):
        """Initialize the asynchronous SRBF optimization.

        Args:
            worker_id: ID of current worker/start in a multistart setting
            data: Problem parameter data structure
            fhat: Surrogate model object
            maxeval: Function evaluation budget
            design: Experimental design

        """
        self.worker_id = worker_id
        self.data = data
        self.fhat = response_surface
        if self.fhat is None:
            self.fhat = RBFInterpolant(surftype=CubicRBFSurface, maxp=maxeval)

        self.maxeval = maxeval
        self.extra = extra

        # Default to generate sampling points using Symmetric Latin Hypercube
        self.design = exp_design
        if self.design is None:
            if maxeval > 10*self.data.dim:
                self.design = SymmetricLatinHypercube(data.dim, 2*(data.dim+1))
            else:
                self.design = LatinHypercube(data.dim, data.dim+1)

        self.xrange = np.asarray(data.xup-data.xlow)

        # algorithm parameters
        self.sigma_min = 0.005  # w.r.t. unit box
        self.sigma_max = 0.2 	# w.r.t. unit box
        self.sigma_init = 0.2
        self.failtol = max(5, data.dim)
        self.succtol = 3

        # Budgeting state
        self.numeval = 0             # Number of completed fevals
        self.feval_budget = maxeval  # Remaining feval budget
        self.feval_pending = 0       # Number of outstanding fevals

        # Event indices
        self.ev_last = 0     # Last event index
        self.ev_adjust = 0   # Last sampling adjustment
        self.ev_restart = 0  # Last restart

        # Initial design info
        self.init_queue = []   # Unassigned points in initial experiment
        self.init_pending = 0  # Number of outstanding initial fevals

        # Sampler state
        self.sigma = 0         # Sampling radius
        self.status = 0        # Status counter
        self.xbest = None      # Current best x
        self.fbest = np.inf    # Current best f
        self.fbest_old = None  # Best f before this update
        self.avoid = {}        # Points to avoid

        # Set up search procedures and initialize
        self.search = sampling_method
        if self.search is None:
            self.search = CandidateDYCORS(data)

        self.check_input()

        # Start with first experimental design
        self.sample_initial()

    def check_input(self):
        assert not hasattr(self.data, "eval_ineq_constraints"), "Objective function has constraints,\n" \
            "AsyncStrategyNoConstraints can't handle constraints"
        assert not hasattr(self.data, "eval_eq_constraints"), "Objective function has constraints,\n" \
            "AsyncStrategyNoConstraints can't handle constraints"

    def proj_fun(self, x):
        return round_vars(self.data, x)

    def log_completion(self, record):
        """Record a completed evaluation to the log.

        :param record: Record of the function evaluation
        """
        xstr = np.array_str(record.params[0], max_line_width=np.inf,
                            precision=5, suppress_small=True)
        if record.feasible:
            logger.info("{} {:.3e} @ {}".format("True", record.value, xstr))
        else:
            logger.info("{} {:.3e} @ {}".format("False", record.value, xstr))

    def get_ev(self):
        """Get event identifier."""
        self.ev_last += 1
        return self.ev_last

    def adjust_step(self):
        """Adjust the sampling radius sigma.

        After succtol successful steps, we cut the sampling radius;
        after failtol failed steps, we double the sampling radius.

        Args:
            Fnew: Best function value in new step
            fbest: Previous best function evaluation
        """
        # Update marker for last adjustment
        self.ev_adjust = self.get_ev()
        # Check if we succeeded at significant improvement
        if self.fbest < self.fbest_old - 1e-3*math.fabs(self.fbest_old):
            self.status = max(1, self.status+1)
        else:
            self.status = min(-1, self.status-1)
        self.fbest_old = self.fbest

        # Check if step needs adjusting
        if self.status <= -self.failtol:
            self.status = 0
            self.sigma /= 2
            logger.info("Reducing sigma")
        if self.status >= self.succtol:
            self.status = 0
            self.sigma = min(2 * self.sigma, self.sigma_max)
            logger.info("Increasing sigma")

        # Check if we need to restart
        if self.sigma < self.sigma_min:
            self.ev_restart = self.get_ev()
            self.sample_initial()

    def sample_initial(self):
        """Generate and queue an initial experimental design."""
        if self.numeval == 0:
            logger.info("=== Start ===")
        else:
            logger.info("=== Restart ===")
        self.sigma = self.sigma_init
        self.status = 0
        self.fbest_old = None
        self.fbest = np.inf
        self.fhat.reset()

        # Generate experimental design
        def poised_for_interpolation(design):
            return self.fhat.poised_for_interpolation(self.proj_fun(from_unit_box(design, self.data)))

        start_sample = self.design.generate_points(poised_for_interpolation)
        assert start_sample.shape[1] == self.data.dim, \
            "Dimension mismatch between problem and experimental design"
        start_sample = from_unit_box(start_sample, self.data)
        if self.extra is not None:
            start_sample = np.vstack((start_sample, self.extra))

        self.init_pending = 0
        for j in range(start_sample.shape[0]):
            start_sample[j, :] = self.proj_fun(start_sample[j, :])  # Project onto feasible region
            self.init_queue.append(start_sample[j, :])

        self.search.init(start_sample, self.fhat, self.maxeval - self.numeval)

    def next_sample_point(self):
        """Generate the next adaptive sample point."""
        x = self.search.make_points(npts=1, xbest=self.xbest, sigma=self.sigma,
                                    proj_fun=self.proj_fun)
        return x

    def propose_action(self):
        """Propose an action."""
        if self.feval_budget == 0:
            if self.feval_pending == 0:
                return Proposal('terminate')
            return None
        elif self.init_queue:
            return self.init_proposal()
        elif self.init_pending > 0:
            return None
        else:
            return self.adapt_proposal()

    def make_proposal(self, x):
        """Create proposal and update counters and budgets."""
        proposal = Proposal('eval', x)
        self.feval_budget -= 1
        self.feval_pending += 1
        proposal.ev_id = self.get_ev()
        self.avoid[proposal.ev_id] = x
        return proposal

    # == Processing in initial phase ==

    def init_proposal(self):
        """Propose a point from the initial experimental design."""
        proposal = self.make_proposal(self.init_queue.pop())
        proposal.add_callback(self.on_initial_proposal)
        self.init_pending += 1
        return proposal

    def on_initial_proposal(self, proposal):
        """Handle accept/reject of proposal from initial design."""
        if proposal.accepted:
            self.on_initial_accepted(proposal)
        else:
            self.on_initial_rejected(proposal)

    def on_initial_accepted(self, proposal):
        """Handle proposal accept from initial design."""
        proposal.record.ev_id = proposal.ev_id
        proposal.record.add_callback(self.on_initial_update)

    def on_initial_rejected(self, proposal):
        """Handle proposal rejection from initial design."""
        self.feval_budget += 1
        self.feval_pending -= 1
        self.init_pending -= 1
        self.init_queue.append(proposal.args[0])

    def on_initial_update(self, record):
        """Handle update of feval from initial design."""
        if record.status == 'completed':
            self.on_initial_completed(record)
        elif record.is_done:
            self.on_initial_aborted(record)

    def on_initial_completed(self, record):
        """Handle successful completion of feval from initial design."""
        self.numeval += 1
        self.feval_pending -= 1
        self.init_pending -= 1
        self.fhat.add_point(record.params[0], record.value)
        del self.avoid[record.ev_id]
        record.worker_id = self.worker_id
        record.worker_numeval = self.numeval
        record.Fpred = None
        record.feasible = True
        if record.value < self.fbest:
            self.xbest = record.params[0]
            self.fbest = record.value
        self.log_completion(record)
        if self.init_pending == 0 and not self.init_queue:
            self.fbest_old = self.fbest

    def on_initial_aborted(self, record):
        """Handle aborted feval from initial design."""
        self.feval_budget += 1
        self.feval_pending -= 1
        self.init_pending -= 1
        self.init_queue.append(record.params)

    # == Processing in adaptive phase ==

    def adapt_proposal(self):
        """Propose a new point."""
        x = np.ravel(np.asarray(self.next_sample_point()))
        proposal = self.make_proposal(x)
        proposal.Fpred = self.fhat.eval(x)
        proposal.add_callback(self.on_adapt_proposal)
        return proposal

    def on_adapt_proposal(self, proposal):
        """Handle accept/reject of proposal from sampling phase."""
        if proposal.accepted:
            self.on_adapt_accept(proposal)
        else:
            self.on_adapt_reject(proposal)

    def on_adapt_accept(self, proposal):
        """Handle accepted proposal from sampling phase."""
        proposal.record.ev_id = proposal.ev_id
        proposal.record.Fpred = proposal.Fpred
        proposal.record.add_callback(self.on_adapt_update)

    def on_adapt_reject(self, proposal):
        """Handle rejected proposal from sampling phase."""
        self.feval_budget += 1
        self.feval_pending -= 1
        self.search.remove_point(self.avoid[proposal.ev_id])
        del self.avoid[proposal.ev_id]

    def on_adapt_update(self, record):
        """Handle update of feval from sampling phase."""
        if record.status == 'completed':
            self.on_adapt_completed(record)
        elif record.is_done:
            self.on_adapt_aborted(record)

    def on_adapt_completed(self, record):
        """Handle completion of feval from sampling phase."""
        self.numeval += 1
        self.feval_pending -= 1
        self.fhat.add_point(record.params[0], record.value)
        del self.avoid[record.ev_id]
        record.worker_id = self.worker_id
        record.worker_numeval = self.numeval
        record.feasible = True
        if record.ev_id >= self.ev_restart and record.value < self.fbest:
            self.xbest = record.params[0]
            self.fbest = record.value
        self.log_completion(record)
        if record.ev_id >= self.ev_adjust:
            self.adjust_step()

    def on_adapt_aborted(self, record):
        """Handle aborted feval from sampling phase."""
        self.feval_budget += 1
        self.feval_pending -= 1
        self.search.remove_point(self.avoid[record.ev_id])
        del self.avoid[record.ev_id]

    def rec_age(self, record):
        """Return whether a completed record is fresh, old, ancient."""
        if record.ev_id >= self.ev_adjust:
            return "Fresh"
        elif record.ev_id >= self.ev_restart:
            return "Old  "
        else:
            return "Ancient"


class AsyncStrategyPenalty(AsyncStrategyNoConstraints):
    """Parallel synchronous optimization strategy with non-bound constraints.

    This is an extension of SyncStrategyNoConstraints that also works with
    bound constraints. We currently only allow inequality constraints, since
    the candidate based methods don't work well with equality constraints.
    We also assume that the constraints are cheap to evaluate, i.e., so that
    it is easy to check if a given point is feasible. More strategies that
    can handle expensive constraints will be added.

    We use a penalty method in the sense that we try to minimize:

    .. math::
        f(x) + \\mu \\sum_j (\\max(0, g_j(x))^2

    where :math:`g_j(x) \\leq 0` are cheap inequality constraints. As a
    measure of promising function values we let all infeasible points have
    the value of the feasible candidate point with the worst function value,
    since large penalties makes it impossible to distinguish between feasible
    points.

    When it comes to the value of :math:`\\mu`, just choose a very large value.


    """

    def __init__(self, worker_id, data, response_surface, maxeval,
                 exp_design=None, sampling_method=None, extra=None,
                 penalty=1e6):

        """Initialize the optimization strategy.

        :param worker_id: Start ID in a multistart setting
        :param data: Problem parameter data structure
        :param response_surface: Surrogate model object
        :param maxeval: Function evaluation budget
        :param exp_design: Experimental design
        :param sampling_method: Sampling method for finding
            points to evaluate
        :param extra: Points to be added to the experimental design
        :param penalty: Penalty for violating constraints
        """

        # Evals wrapper for penalty method
        def penalty_evals(fhat, xx):
            penalty = self.penalty_fun(xx).T
            vals = fhat.evals(xx)
            if xx.shape[0] > 1:
                ind = (np.where(penalty <= 0.0)[0]).T
                if ind.shape[0] > 1:
                    ind2 = (np.where(penalty > 0.0)[0]).T
                    ind3 = np.argmax(np.squeeze(vals[ind]))
                    vals[ind2] = vals[ind3]
                    return vals
            return vals + penalty

        # Derivs wrapper for penalty method
        def penalty_derivs(fhat, xx):
            x = np.atleast_2d(xx)
            constraints = np.array(self.data.eval_ineq_constraints(x))
            dconstraints = self.data.deriv_ineq_constraints(x)
            constraints[np.where(constraints < 0.0)] = 0.0
            return np.atleast_2d(fhat.deriv(xx)) + \
                2 * self.penalty * np.sum(
                    constraints * np.rollaxis(dconstraints, 2), axis=2).T

        AsyncStrategyNoConstraints.__init__(self,  worker_id, data,
                                           RSPenalty(response_surface, penalty_evals, penalty_derivs),
                                           maxeval, exp_design,
                                           sampling_method, extra)

        self.penalty = penalty

    def check_input(self):
        assert hasattr(self.data, "eval_ineq_constraints"), "Objective function has no inequality constraints"
        assert not hasattr(self.data, "eval_eq_constraints"), "Objective function has equality constraints,\n" \
            "AsyncStrategyPenalty can't handle equality constraints"

    def penalty_fun(self, xx):
        """Computes the penalty for constraint violation

        :param xx: Points to compute the penalty for
        :return: Penalty for constraint violations
        """

        vec = np.array(self.data.eval_ineq_constraints(xx))
        vec[np.where(vec < 0.0)] = 0.0
        vec **= 2
        return self.penalty * np.asmatrix(np.sum(vec, axis=1))

    def on_initial_completed(self, record):
        """Handle successful completion of feval from initial design."""
        x = np.zeros((1, record.params[0].shape[0]))
        x[0, :] = record.params[0]
        penalty = self.penalty_fun(x)[0, 0]
        if penalty > 0.0:
            record.feasible = False
        else:
            record.feasible = True
        self.log_completion(record)
        self.numeval += 1
        self.feval_pending -= 1
        self.init_pending -= 1
        self.fhat.add_point(record.params[0], record.value)
        del self.avoid[record.ev_id]
        record.worker_id = self.worker_id
        record.worker_numeval = self.numeval
        record.Fpred = None
        if record.value + penalty < self.fbest:
            self.xbest = record.params[0]
            self.fbest = record.value + penalty
        if self.init_pending == 0 and not self.init_queue:
            self.fbest_old = self.fbest

    def on_adapt_completed(self, record):
        """Handle completion of feval from sampling phase."""
        x = np.zeros((1, record.params[0].shape[0]))
        x[0, :] = record.params[0]
        penalty = self.penalty_fun(x)[0, 0]
        if penalty > 0.0:
            record.feasible = False
        else:
            record.feasible = True
        self.log_completion(record)
        self.numeval += 1
        self.feval_pending -= 1
        self.fhat.add_point(record.params[0], record.value)
        del self.avoid[record.ev_id]
        record.worker_id = self.worker_id
        record.worker_numeval = self.numeval
        if record.ev_id >= self.ev_restart and record.value + penalty < self.fbest:
            self.xbest = record.params[0]
            self.fbest = record.value + penalty
        if record.ev_id >= self.ev_adjust:
            self.adjust_step()


class AsyncStrategyProjection(AsyncStrategyNoConstraints):
    """Parallel synchronous optimization strategy with non-bound constraints.
    It uses a supplied method to project proposed points onto the feasible
    region in order to always evaluate feasible points which is useful in
    situations where it is easy to project onto the feasible region and where
    the objective function is nonsensical for infeasible points.

    This is an extension of SyncStrategyNoConstraints that also works with
    bound constraints.
    """

    def __init__(self, worker_id, data, response_surface, maxeval, nsamples,
                 exp_design=None, sampling_method=None, extra=None,
                 proj_fun=None):
        """Initialize the optimization strategy.

        :param worker_id: Start ID in a multistart setting
        :param data: Problem parameter data structure
        :param response_surface: Surrogate model object
        :param maxeval: Function evaluation budget
        :param exp_design: Experimental design
        :param sampling_method: Sampling method for finding
            points to evaluate
        :param extra: Points to be added to the experimental design
        :param proj_fun: Projection operator
        """

        self.projection = proj_fun

        AsyncStrategyNoConstraints.__init__(self,  worker_id, data,
                                            response_surface, maxeval,
                                            exp_design, sampling_method,
                                            extra)

    def check_input(self):
        assert hasattr(self.data, "eval_ineq_constraints") or \
            hasattr(self.data, "eval_eq_constraints"), \
            "Objective function has no constraints"

    def proj_fun(self, x):
        for i in range(x.shape[0]):
            x[i, :] = self.projection(x[i, :])
        return x
