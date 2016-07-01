"""
This module contains simplex search algorithms.
"""

from optproblems.base import ResourcesExhausted, Individual, Stalled

from dfoalgos.base import Observable, scale, displace, center_of_mass
from dfoalgos.base import lexicographic_sort_key


class SimplexSearch(Observable):
    """Abstract base class for simplex search algorithms."""

    def __init__(self, problem,
                 initial_simplex,
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
        initial_simplex : list
            The points of the initial simplex.
        max_iterations : int, optional
            A potential budget restriction on the number of iterations.
            Default is unlimited.
        xtol : float, optional
            The algorithm stops when the maximal absolute deviation in all
            dimensions of the search space between the best and all other
            points in the simplex drops below this value. By default,
            this criterion is off.
        ftol : float, optional
            The algorithm stops when the absolute difference of objective
            values between the best and worst individual in the simplex
            drops below this value. This criterion can only be used with
            scalar objective values. By default, this criterion is off.
        individual_factory : callable, optional
            A callable taking a point as argument. It must return an object
            with two member attributes `phenome` and `objective_values`. The
            `phenome` contains the solution, while `objective_values` is set
            to None. By default, :class:`optproblems.base.Individual` is
            used.
        sort_key : callable, optional
            A sort key for ranking the individuals in the simplex. By
            default, :func:`dfoalgos.base.lexicographic_sort_key` is used.
        verbosity : int, optional
            A value of 0 means quiet, 1 means some information is printed
            to standard out on start and termination of this algorithm.

        """
        Observable.__init__(self)
        self.problem = problem
        self.simplex = list(initial_simplex)
        self.max_iterations = max_iterations
        self.xtol = xtol
        self.ftol = ftol
        if individual_factory is None:
            individual_factory = Individual
        self.individual_factory = individual_factory
        if sort_key is None:
            sort_key = lexicographic_sort_key
        self.sort_key = sort_key
        self.verbosity = verbosity
        self.iteration = 0
        self.remaining_iterations = max_iterations
        self.last_termination = None
        self.offspring = []
        self.num_expansion_failures = 0
        self.num_expansions = 0
        self.num_outside_failures = 0
        self.num_outside_operations = 0
        self.num_shrinks = 0


    def __str__(self):
        """Return the algorithm's name."""
        return self.__class__.__name__


    def calc_mean_point(self, individuals):
        """Calculate the mean point for reflection."""
        phenomes = [ind.phenome for ind in individuals]
        return center_of_mass(phenomes)


    def update_simplex(self, new_simplex):
        """Overwrite the current simplex with a new one.

        Parameters
        ----------
        new_simplex : list of Individual
            The new solutions.

        """
        self.simplex = new_simplex


    def scale(self, individuals, fixed_ind, factor):
        """Scale individuals by a given factor.

        This method unwraps the points, delegates to :func:`scale`, and
        then again wraps the scaled points in individuals with the
        individual factory.

        Parameters
        ----------
        individuals : iterable of Individual
            The individuals containing the points to scale.
        fixed_ind : Individual
            The individual containing the fixed point of the transformation.
        factor : float
            The scale factor.

        Returns
        -------
        scaled_individuals : list of Individual
            List containing scaled individuals.

        """
        individual_factory = self.individual_factory
        points = [ind.phenome for ind in individuals]
        fixed_point = fixed_ind.phenome
        scaled_points = scale(points, fixed_point, factor)
        return [individual_factory(p) for p in scaled_points]


    def run(self):
        """Run the algorithm.

        The :func:`step<dfoalgos.simplex.SimplexSearch.step>` function is
        called in a loop. The algorithm stops when a :class:`StopIteration`
        exception is caught or when the stopping criterion evaluates to
        True.

        Returns
        -------
        best_individual : Individual
            The best individual of the simplex according to the sort key.

        """
        # shortcuts
        individual_factory = self.individual_factory
        stopping_criterion = self.stopping_criterion
        step = self.step
        if self.verbosity > 0:
            print(str(self) + " running on problem " + str(self.problem))
        try:
            for i, point in enumerate(self.simplex):
                individual = individual_factory(point)
                individual.age = 1
                self.simplex[i] = individual
            unevaluated = []
            for individual in self.simplex:
                if individual.objective_values is None:
                    unevaluated.append(individual)
            self.problem.batch_evaluate(unevaluated)
            while not stopping_criterion():
                step()
        except StopIteration as instance:
            self.last_termination = instance
            if self.verbosity > 0:
                print(instance)
        if self.verbosity > 0:
            print("Algorithm terminated")
        min_candidates = []
        for ind in self.simplex + self.offspring:
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
            when the `xtol` or `ftol` criteria trigger or the simplex
            contains a duplicate point

        """
        if self.remaining_iterations <= 0:
            raise ResourcesExhausted("iterations")
        self.simplex.sort(key=self.sort_key)
        simplex = self.simplex
        xtol = self.xtol
        if xtol is not None:
            best_phenome = simplex[0].phenome
            max_diff = 0.0
            for individual in simplex[1:]:
                for phene, best_phene in zip(individual.phenome, best_phenome):
                    diff = abs(phene - best_phene)
                    if diff > max_diff:
                        max_diff = diff
            if max_diff <= xtol:
                raise Stalled("xtol")
        ftol = self.ftol
        if ftol is not None:
            best_objective = simplex[0].objective_values
            max_diff = 0.0
            for individual in simplex[1:]:
                diff = abs(individual.objective_values - best_objective)
                if diff > max_diff:
                    max_diff = diff
            if max_diff <= ftol:
                raise Stalled("ftol")
        for i, individual in enumerate(simplex):
            for j in range(i + 1, len(simplex)):
                if individual.phenome == simplex[j].phenome:
                    raise Stalled("collapsed simplex")
        return False


    def step(self):
        """Perform one optimization step.

        This is an abstract method. Overwrite in your own simplex search
        implementation.

        """
        raise NotImplementedError()



class SpendleySimplexSearch(SimplexSearch):
    """Fixed-shape, variable-size simplex search.

    This algorithm is regarded as the oldest simplex search around. It was
    introduced by [Spendley1962]_, who were also the first to propose the
    basic reflection operation. This implementation follows the description
    of [Gurson2000]_ (pp. 13-23), which extends the original algorithm with
    a shrink operation and generalizes it to more than two dimensions.

    References
    ----------
    .. [Spendley1962] W. Spendley, G. R. Hext, and F. R. Himsworth (1962).
        Sequential Application of Simplex Designs in Optimisation and
        Evolutionary Operation. Technometrics, Vol. 4, No. 4, pp. 441-461.
    .. [Gurson2000] Adam P. Gurson (2000). Simplex Search Behavior in
        Nonlinear Optimization. Honors thesis.
        http://www.cs.wm.edu/~va/CS495/gurson.pdf

    """
    def __init__(self, problem,
                 initial_simplex,
                 shrink_factor=0.5,
                 max_age=None,
                 **kwargs):
        """Constructor.

        Parameters
        ----------
        problem : optproblems.Problem
            An optimization problem.
        initial_simplex : list
            The points of the initial simplex.
        shrink_factor : float, optional
            The parameter for the shrink operation.
        max_age : int, optional
            A shrink operation is triggered when the best individual's age
            reaches `max_age`. The default is ``len(initial_simplex)``.
        kwargs
            Arbitrary keyword arguments, passed to the super class.

        """
        SimplexSearch.__init__(self, problem, initial_simplex, **kwargs)
        self.shrink_factor = shrink_factor
        if max_age is None:
            max_age = len(initial_simplex)
        self.max_age = max_age
        self.previous_new_ind = None


    def step(self):
        """Perform one optimization step."""
        self.offspring = []
        individual_factory = self.individual_factory
        sort_key = self.sort_key
        self.simplex.sort(key=sort_key)
        # potential shrink
        if self.simplex[0].age > self.max_age:
            shrunk_individuals = self.scale(self.simplex[1:],
                                            self.simplex[0],
                                            self.shrink_factor)
            self.offspring.extend(shrunk_individuals)
            self.problem.batch_evaluate(shrunk_individuals)
            self.update_simplex([self.simplex[0]] + shrunk_individuals)
            self.simplex.sort(key=sort_key)
            for ind in self.simplex:
                ind.age = 1
            self.num_shrinks += 1
        # determine point to reflect
        if self.simplex[-1] is self.previous_new_ind:
            point_to_reflect = self.simplex[-2].phenome
            replace_index = -2
            remaining_simplex = self.simplex[:-2] + [self.simplex[-1]]
        else:
            point_to_reflect = self.simplex[-1].phenome
            replace_index = -1
            remaining_simplex = self.simplex[:-1]
        # reflect
        mean_point = self.calc_mean_point(remaining_simplex)
        new_point = displace(mean_point, point_to_reflect, 1.0)
        new_individual = individual_factory(new_point)
        self.offspring.append(new_individual)
        self.problem.evaluate(new_individual)
        self.simplex[replace_index] = new_individual
        # update ages
        if sort_key(new_individual) < sort_key(self.simplex[0]):
            for ind in self.simplex:
                ind.age = 1
        else:
            new_individual.age = 0
            for ind in self.simplex:
                ind.age += 1
        self.update_simplex(self.simplex)
        self.previous_new_ind = new_individual
        self.notify_observers()
        self.iteration += 1
        self.remaining_iterations -= 1



class NelderMeadSimplexSearch(SimplexSearch):
    """The simplex search by Nelder and Mead.

    This algorithm was proposed by [Nelder1965]_. It adapts the simplex
    shape to the landscape by expansion and contration operations. This
    algorithm is fast also on ill-conditioned problems, but may converge to
    a non-stationary point.

    References
    ----------
    .. [Nelder1965] Nelder, J.A. and Mead, R. (1965). A simplex method for
        function minimization, The Computer Journal, Vol. 7, No. 4,
        pp. 308-313. https://dx.doi.org/10.1093/comjnl/7.4.308

    """
    def __init__(self, problem,
                 initial_simplex,
                 reflection_factor=1.0,
                 expansion_factor=2.0,
                 contraction_factor=0.5,
                 shrink_factor=0.5,
                 **kwargs):
        """Constructor.

        Parameters
        ----------
        problem : optproblems.Problem
            An optimization problem.
        initial_simplex : list
            The points of the initial simplex.
        reflection_factor : float, optional
            The parameter used for reflection.
        expansion_factor : float, optional
            The parameter used for expansion.
        contraction_factor : float, optional
            The parameter used for inside and outside contraction.
        shrink_factor : float, optional
            The parameter for the shrink operation.
        kwargs
            Arbitrary keyword arguments, passed to the super class.

        """
        SimplexSearch.__init__(self, problem, initial_simplex, **kwargs)
        assert reflection_factor > 0.0
        assert expansion_factor >= 1.0
        assert contraction_factor > 0.0 and contraction_factor < 1.0
        assert shrink_factor > 0.0 and shrink_factor < 1.0
        self.reflection_factor = reflection_factor
        self.expansion_factor = expansion_factor
        self.contraction_factor = contraction_factor
        self.shrink_factor = shrink_factor


    def _expansion(self, new_individual, mean_point, worst_point):
        """Private method to carry out the expansion step."""
        expanded_point = displace(mean_point,
                                  worst_point,
                                  self.reflection_factor * self.expansion_factor)
        expanded_individual = self.individual_factory(expanded_point)
        self.offspring.append(expanded_individual)
        self.problem.evaluate(expanded_individual)
        if self.sort_key(expanded_individual) < self.sort_key(new_individual):
            self.simplex[-1] = expanded_individual
            success = True
        else:
            self.simplex[-1] = new_individual
            success = False
        self.update_simplex(self.simplex)
        return success


    def step(self):
        """Perform one optimization step."""
        self.offspring = []
        individual_factory = self.individual_factory
        sort_key = self.sort_key
        self.simplex.sort(key=sort_key)
        worst_point = self.simplex[-1].phenome
        problem = self.problem
        refl_factor = self.reflection_factor
        cont_factor = self.contraction_factor
        # reflect
        mean_point = self.calc_mean_point(self.simplex[:-1])
        new_individual = individual_factory(displace(mean_point,
                                                     worst_point,
                                                     refl_factor))
        self.offspring.append(new_individual)
        problem.evaluate(new_individual)
        new_sort_key = sort_key(new_individual)
        if new_sort_key < sort_key(self.simplex[0]) and self.expansion_factor > 1.0:
            expansion_success = self._expansion(new_individual, mean_point, worst_point)
            self.num_expansion_failures += not expansion_success
            self.num_expansions += 1
        elif new_sort_key < sort_key(self.simplex[-2]):
            # new point is not the worst in the new simplex
            # => next iteration
            self.simplex[-1] = new_individual
            self.update_simplex(self.simplex)
        else:
            do_inside_shrink = True
            if new_sort_key < sort_key(self.simplex[-1]):
                # outside contraction
                contracted_point = displace(mean_point,
                                            worst_point,
                                            refl_factor * cont_factor)
                contracted_individual = individual_factory(contracted_point)
                self.offspring.append(contracted_individual)
                problem.evaluate(contracted_individual)
                self.num_outside_operations += 1
                if sort_key(contracted_individual) <= sort_key(new_individual):
                    self.simplex[-1] = contracted_individual
                    self.update_simplex(self.simplex)
                    do_inside_shrink = False
                else:
                    self.num_outside_failures += 1
            else:
                # inside contraction
                contracted_point = displace(mean_point, worst_point, -cont_factor)
                contracted_individual = individual_factory(contracted_point)
                self.offspring.append(contracted_individual)
                problem.evaluate(contracted_individual)
                if sort_key(contracted_individual) < sort_key(self.simplex[-1]):
                    self.simplex[-1] = contracted_individual
                    self.update_simplex(self.simplex)
                    do_inside_shrink = False
            if do_inside_shrink:
                shrunk_individuals = self.scale(self.simplex[1:],
                                                self.simplex[0],
                                                self.shrink_factor)
                self.offspring.extend(shrunk_individuals)
                problem.batch_evaluate(shrunk_individuals)
                self.update_simplex([self.simplex[0]] + shrunk_individuals)
                self.num_shrinks += 1
        self.notify_observers()
        self.iteration += 1
        self.remaining_iterations -= 1
