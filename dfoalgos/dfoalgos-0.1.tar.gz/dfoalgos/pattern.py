"""
This module contains pattern search algorithms.
"""

from collections import deque

from optproblems.base import ResourcesExhausted, Individual, Stalled

from dfoalgos.base import Observable, lexicographic_sort_key
from dfoalgos.base import create_standard_basis


class PatternSearch(Observable):
    """A synchronous implementation of pattern search.

    This implementation uses a double-ended queue
    (:class:`collections.deque`) to store the pattern. In case of
    opportunistic behavior (accepting the first improvement), the elements
    in the deque are cycled so that the successful direction is at the
    front of the pattern, and thus is the first tried direction in the next
    iteration. The original order of directions is always retained.

    """
    def __init__(self, problem,
                 start_point,
                 step_size,
                 shrink_factor=0.5,
                 pattern=None,
                 opportunistic=True,
                 max_iterations=float("inf"),
                 xtol=None,
                 ftol=None,
                 individual_factory=None,
                 sort_key=None,
                 verbosity=1):
        """Constructor.

        Parameters
        ----------
        problem : optproblems.Problem
            An optimization problem.
        start_point : list
            The starting point for the optimization.
        step_size : float
            The initial step size.
        shrink_factor : float, optional
            This value must be larger than 0 and smaller than 1. It is
            multiplied with the step size in iterations where no
            improvement is found.
        pattern : sequence, optional
            A sequence of direction vectors. To guarantee convergence to a
            stationary point, this  must be a positive basis of the real
            coordinate space. By default, a maximal positive basis is
            generated. The provided sequence is not modified. Its elements
            are copied into another container.
        opportunistic : bool, optional
            If True (default), the first improvement is accepted and the
            execution jumps to the next iteration. Additionally, the
            successful direction is cycled to the first position in the
            pattern. If False, the whole pattern is evaluated in every
            iteration ("best improvement").
        max_iterations : int, optional
            A potential budget restriction on the number of iterations.
            Default is unlimited.
        xtol : float, optional
            The algorithm stops when the maximal absolute deviation in all
            dimensions of the search space between the best and the last
            ``len(pattern)`` evaluated solutions drops below this value. By
            default, this criterion is off.
        ftol : float, optional
            The algorithm stops when the absolute difference of objective
            values between the best individual and the worst of the last
            ``len(pattern)`` evaluated solutions drops below this value.
            This criterion can only be used with scalar objective values. By
            default, this criterion is off.
        individual_factory : callable, optional
            A callable taking a point as argument. It must return an object
            with two member attributes `phenome` and `objective_values`. The
            `phenome` contains the solution, while `objective_values` is set
            to None. By default, :class:`optproblems.base.Individual` is
            used.
        sort_key : callable, optional
            A sort key for ranking the individuals. By default,
            :func:`dfoalgos.base.lexicographic_sort_key` is used.
        verbosity : int, optional
            A value of 0 means quiet, 1 means some information is printed
            to standard out on start and termination of this algorithm.

        """
        Observable.__init__(self)
        self.problem = problem
        assert step_size > 0.0
        self.step_size = step_size
        assert shrink_factor > 0.0 and shrink_factor < 1.0
        self.shrink_factor = shrink_factor
        if pattern is None:
            pattern = create_standard_basis(len(start_point))
        self.pattern = deque(pattern)
        self.opportunistic = opportunistic
        self.remaining_iterations = max_iterations
        self.xtol = xtol
        self.ftol = ftol
        if individual_factory is None:
            individual_factory = Individual
        self.individual_factory = individual_factory
        self.best_individual = individual_factory(start_point)
        self.previous_best_individual = self.best_individual
        if sort_key is None:
            sort_key = lexicographic_sort_key
        self.sort_key = sort_key
        self.verbosity = verbosity
        self.iteration = 0
        self.last_termination = None
        self.improvement_found = False
        self.offspring = []
        self.recently_evaluated_buffer = deque(maxlen=len(self.pattern))
        self.num_shrinks = 0


    def __str__(self):
        """Return the algorithm's name."""
        return self.__class__.__name__


    def run(self):
        """Run the algorithm.

        The :func:`step<dfoalgos.pattern.PatternSearch.step>` function is
        called in a loop. The algorithm stops when a :class:`StopIteration`
        exception is caught or when the stopping criterion evaluates to
        True.

        Returns
        -------
        best_individual : Individual
            The best individual found so far, according to the sort key.

        """
        # shortcuts
        stopping_criterion = self.stopping_criterion
        step = self.step
        if self.verbosity > 0:
            print(str(self) + " running on problem " + str(self.problem))
        try:
            if self.best_individual.objective_values is None:
                self._evaluate([self.best_individual])
            while not stopping_criterion():
                step()
        except StopIteration as instance:
            self.last_termination = instance
            if self.verbosity > 0:
                print(instance)
        if self.verbosity > 0:
            print("Algorithm terminated")
        min_candidates = [self.best_individual]
        for ind in self.offspring:
            if ind.objective_values is not None:
                min_candidates.append(ind)
        return min(min_candidates, key=self.sort_key)


    def stopping_criterion(self):
        """Check if optimization should go on.

        The algorithm halts when this method returns True or raises an
        exception.

        Raises
        ------
        ResourcesExhausted
            when number of iterations reaches maximum
        Stalled
            when the `xtol` or `ftol` criteria trigger

        """
        if self.remaining_iterations <= 0:
            raise ResourcesExhausted("iterations")
        xtol = self.xtol
        buffer = self.recently_evaluated_buffer
        if xtol is not None and len(buffer) == buffer.maxlen:
            best_phenome = self.best_individual.phenome
            max_diff = 0.0
            for individual in buffer:
                for phene, best_phene in zip(individual.phenome, best_phenome):
                    diff = abs(phene - best_phene)
                    if diff > max_diff:
                        max_diff = diff
            if max_diff <= xtol:
                raise Stalled("xtol")
        ftol = self.ftol
        if ftol is not None and len(buffer) == buffer.maxlen:
            best_objective = self.best_individual.objective_values
            max_diff = 0.0
            for individual in buffer:
                diff = abs(individual.objective_values - best_objective)
                if diff > max_diff:
                    max_diff = diff
            if max_diff <= ftol:
                raise Stalled("ftol")
        return False


    def _evaluate(self, individuals):
        """Objective function evaluation.

        This method delegates the evaluation to the problem instance. The
        evaluated individuals are recorded in a buffer of size
        ``len(pattern)``. The buffer is used to evaluate the stopping
        criteria `xtol` and `ftol`.

        """
        if len(individuals) == 1:
            self.problem.evaluate(individuals[0])
        else:
            self.problem.batch_evaluate(individuals)
        self.recently_evaluated_buffer.extend(individuals)


    def update_best_individual(self, new_best):
        """Set a new current best individual.

        Before the current best is overwritten, it is saved in
        the attribute `previous_best_individual`. The success is also marked
        by setting `improvement_found` to True.

        """
        self.previous_best_individual = self.best_individual
        self.best_individual = new_best
        self.improvement_found = True


    def update_pattern_and_step_size(self):
        """Reduce the step size by multiplying with `shrink_factor`."""
        self.step_size *= self.shrink_factor


    def step(self):
        """Perform one optimization step.

        Raises
        ------
        Stalled
            when none of the generated points differ from the current best
            or previous best solution

        """
        pattern = self.pattern
        sort_key = self.sort_key
        best_sort_key = sort_key(self.best_individual)
        individual_factory = self.individual_factory
        current_best_phenome = self.best_individual.phenome
        prev_best_phenome = self.previous_best_individual.phenome
        dim = len(current_best_phenome)
        self.improvement_found = False
        self.offspring = []
        candidates = []
        pattern_indices = []
        for index, direction in enumerate(pattern):
            new_vector = [current_best_phenome[i] + self.step_size * direction[i] for i in range(dim)]
            if new_vector != prev_best_phenome and new_vector != current_best_phenome:
                candidates.append(individual_factory(new_vector))
                pattern_indices.append(index)
        num_new_candidates = len(candidates)
        if num_new_candidates == 0:
            # step size has fallen below floating point precision
            raise Stalled("collapsed pattern")
        if self.opportunistic:
            for index, candidate in zip(pattern_indices, candidates):
                self._evaluate([candidate])
                self.offspring.append(candidate)
                if sort_key(candidate) < best_sort_key:
                    self.update_best_individual(candidate)
                    # try the successful direction first in next generation
                    pattern.rotate(-index)
                    #pattern.insert(0, pattern.pop(index))
                    break
        else:
            self.offspring.extend(candidates)
            self._evaluate(candidates)
            for candidate in candidates:
                if sort_key(candidate) < best_sort_key:
                    self.update_best_individual(candidate)
        self.notify_observers()
        if not self.improvement_found:
            self.update_pattern_and_step_size()
        self.iteration += 1
        self.remaining_iterations -= 1
