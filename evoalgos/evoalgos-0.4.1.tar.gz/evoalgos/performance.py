"""Measures for the evaluation of algorithm performance."""

from evoalgos.individual import Individual
import evoalgos.sorting


def is_iterable(some_object):
    """Helper function to determine if an object is iterable."""
    try:
        iter(some_object)
    except TypeError:
        return False
    return True



class QualityIndicator(object):
    """Abstract base class for quality indicators."""

    def __init__(self):
        self.name = None


    def __str__(self):
        """Return the indicator's name."""
        if self.name is None:
            return self.__class__.__name__
        else:
            return self.name


    def assess(self, population):
        """Assess a set of individuals.

        This is an abstract method.

        Parameters
        ----------
        population : list of Individual
            The individuals to assess.

        """
        raise NotImplementedError("Assessment of population not implemented.")


    def assess_non_dom_front(self, front):
        """Assess a non-dominated front.

        This is an abstract method.

        Parameters
        ----------
        front : iterable
            An iterable of points or individuals with the special
            property that no one is dominated by any other regarding
            Pareto-dominance.

        """
        raise NotImplementedError("Assessment of non-dominated front not implemented.")



class HyperVolumeIndicator(QualityIndicator):
    """Abstract base class for hypervolume indicators.

    Measures the dominated hypervolume with regard to a reference point.
    Such indicators are Pareto-compliant.

    .. warning:: The time for calculating the hypervolume is exponential in
        the number of objectives.

    """
    do_maximize = True

    def __init__(self, reference_point):
        QualityIndicator.__init__(self)
        self.non_dom_sorting = evoalgos.sorting.NonDominatedSorting()
        leave_ref_point_as_is = not isinstance(reference_point, Individual)
        leave_ref_point_as_is |= reference_point is None
        leave_ref_point_as_is |= is_iterable(reference_point)
        if leave_ref_point_as_is:
            self.reference_point = reference_point
        else:
            self.reference_point = reference_point.objective_values


    def assess(self, population):
        """Assess a set of individuals.

        This method identifies the non-dominated front of the population
        and then assesses it with
        :func:`assess_non_dom_front`.

        Parameters
        ----------
        population : list of Individual
            The individuals to assess.

        Returns
        -------
        indicator_value : float
            A scalar evaluating this population.

        """
        first_front = self.non_dom_sorting.identify_best_group(population)
        indicator_value = self.assess_non_dom_front(first_front)
        return indicator_value



class FonsecaHyperVolume(HyperVolumeIndicator):
    """A hypervolume indicator implementation.

    The code is based on variant 3, version 1.2 of the C implementation
    of the algorithm in [Fonseca2006]_. A translation of the points was
    added so that the reference point is the origin, to obtain a slight
    speed improvement.

    References
    ----------
    .. [Fonseca2006] C. M. Fonseca, L. Paquete, M. Lopez-Ibanez. An improved
        dimension-sweep algorithm for the hypervolume indicator. In IEEE
        Congress on Evolutionary Computation, pages 1157-1163, Vancouver,
        Canada, July 2006.

    """
    def __init__(self, reference_point):
        """Constructor.

        Parameters
        ----------
        reference_point : iterable
            The reference point needed for the hypervolume computation.

        """
        HyperVolumeIndicator.__init__(self, reference_point)
        self.list = []


    def assess_non_dom_front(self, front):
        """Return the hypervolume dominated by a non-dominated front.

        Prior to the HV computation, front and reference point are
        translated so that the reference point is [0, ..., 0].

        Parameters
        ----------
        front : iterable
            An iterable of points or individuals with the special
            property that no one is dominated by any other regarding
            Pareto-dominance.

        Returns
        -------
        hypervolume : float
            The hypervolume dominated by these points.

        """
        def weakly_dominates(point, other):
            for i in range(len(point)):
                if point[i] > other[i]:
                    return False
            return True

        relevant_points = []
        reference_point = self.reference_point
        dim = len(reference_point)
        for point in front:
            if isinstance(point, Individual) or not is_iterable(point):
                point = point.objective_values
            # only consider points that dominate the reference point
            if weakly_dominates(point, reference_point):
                relevant_points.append(point)
        if any(reference_point):
            # shift points so that reference_point == [0, ..., 0]
            # this way the reference point doesn't have to be explicitly used
            # in the HV computation
            for j in range(len(relevant_points)):
                relevant_points[j] = [relevant_points[j][i] - reference_point[i] for i in range(dim)]
        self.preprocess(relevant_points)
        bounds = [-1.0e308] * dim
        hypervolume = self.hv_recursive(dim - 1, len(relevant_points), bounds)
        return hypervolume


    def hv_recursive(self, dim_index, length, bounds):
        """Recursive call to hypervolume calculation.

        This method should not be called directly. In contrast to
        [Fonseca2006]_, the code assumes that the reference point is
        [0, ..., 0]. This allows the avoidance of a few operations.

        """
        hvol = 0.0
        sentinel = self.list.sentinel
        if length == 0:
            return hvol
        elif dim_index == 0:
            # special case: only one dimension
            # why using hypervolume at all?
            return -sentinel.next[0].cargo[0]
        elif dim_index == 1:
            # special case: two dimensions, end recursion
            q = sentinel.next[1]
            h = q.cargo[0]
            p = q.next[1]
            while p is not sentinel:
                p_cargo = p.cargo
                hvol += h * (q.cargo[1] - p_cargo[1])
                if p_cargo[0] < h:
                    h = p_cargo[0]
                q = p
                p = q.next[1]
            hvol += h * q.cargo[1]
            return hvol
        else:
            remove = self.list.remove
            reinsert = self.list.reinsert
            hv_recursive = self.hv_recursive
            p = sentinel
            q = p.prev[dim_index]
            while q.cargo is not None:
                if q.ignore < dim_index:
                    q.ignore = 0
                q = q.prev[dim_index]
            q = p.prev[dim_index]
            while length > 1 and (q.cargo[dim_index] > bounds[dim_index] or q.prev[dim_index].cargo[dim_index] >= bounds[dim_index]):
                p = q
                remove(p, dim_index, bounds)
                q = p.prev[dim_index]
                length -= 1
            q_area = q.area
            q_cargo = q.cargo
            q_prev_dim_index = q.prev[dim_index]
            if length > 1:
                hvol = q_prev_dim_index.volume[dim_index] + q_prev_dim_index.area[dim_index] * (q_cargo[dim_index] - q_prev_dim_index.cargo[dim_index])
            else:
                q_area[0] = 1
                q_area[1:dim_index + 1] = [q_area[i] * -q_cargo[i] for i in range(dim_index)]
            q.volume[dim_index] = hvol
            if q.ignore >= dim_index:
                q_area[dim_index] = q_prev_dim_index.area[dim_index]
            else:
                q_area[dim_index] = hv_recursive(dim_index - 1, length, bounds)
                if q_area[dim_index] <= q_prev_dim_index.area[dim_index]:
                    q.ignore = dim_index
            while p is not sentinel:
                p_cargo_dim_index = p.cargo[dim_index]
                hvol += q.area[dim_index] * (p_cargo_dim_index - q.cargo[dim_index])
                bounds[dim_index] = p_cargo_dim_index
                reinsert(p, dim_index, bounds)
                length += 1
                q = p
                p = p.next[dim_index]
                q.volume[dim_index] = hvol
                if q.ignore >= dim_index:
                    q.area[dim_index] = q.prev[dim_index].area[dim_index]
                else:
                    q.area[dim_index] = hv_recursive(dim_index - 1, length, bounds)
                    if q.area[dim_index] <= q.prev[dim_index].area[dim_index]:
                        q.ignore = dim_index
            hvol -= q.area[dim_index] * q.cargo[dim_index]
            return hvol


    def preprocess(self, front):
        """Set up the list data structure needed for calculation."""
        dimensions = len(self.reference_point)
        node_list = MultiList(dimensions)
        nodes = [MultiList.Node(dimensions, point) for point in front]
        for i in range(dimensions):
            self.sort_by_dim(nodes, i)
            node_list.extend(nodes, i)
        self.list = node_list


    @staticmethod
    def sort_by_dim(nodes, i):
        """Sort the list of nodes by the i-th value of the contained points."""
        def sort_key(node):
            return node.cargo[i]

        nodes.sort(key=sort_key)



class MultiList:
    """A special data structure needed by :class:`FonsecaHyperVolume`.

    It consists of several doubly linked lists that share common nodes. So,
    every node has multiple predecessors and successors, one in every list.

    """
    class Node:

        def __init__(self, num_lists, cargo=None):
            self.cargo = cargo
            self.next = [None] * num_lists
            self.prev = [None] * num_lists
            self.ignore = 0
            self.area = [0.0] * num_lists
            self.volume = [0.0] * num_lists

        def __str__(self):
            return str(self.cargo)


    def __init__(self, num_lists):
        """Constructor.

        Builds `num_lists` doubly linked lists.

        """
        self.num_lists = num_lists
        self.sentinel = MultiList.Node(num_lists)
        self.sentinel.next = [self.sentinel] * num_lists
        self.sentinel.prev = [self.sentinel] * num_lists


    def __str__(self):
        """Return a string representation of this data structure."""
        strings = []
        for i in range(self.num_lists):
            current_list = []
            node = self.sentinel.next[i]
            while node != self.sentinel:
                current_list.append(str(node))
                node = node.next[i]
            strings.append(str(current_list))
        string_repr = ""
        for string in strings:
            string_repr += string + "\n"
        return string_repr


    def __len__(self):
        """Return the number of lists that are included in this MultiList."""
        return self.num_lists


    def get_length(self, i):
        """Return the length of the i-th list."""
        length = 0
        sentinel = self.sentinel
        node = sentinel.next[i]
        while node != sentinel:
            length += 1
            node = node.next[i]
        return length


    def append(self, node, index):
        """Append a node to the end of the list at the given index."""
        last_but_one = self.sentinel.prev[index]
        node.next[index] = self.sentinel
        node.prev[index] = last_but_one
        # set the last element as the new one
        self.sentinel.prev[index] = node
        last_but_one.next[index] = node


    def extend(self, nodes, index):
        """Extend the list at the given index with the nodes."""
        sentinel = self.sentinel
        for node in nodes:
            last_but_one = sentinel.prev[index]
            node.next[index] = sentinel
            node.prev[index] = last_but_one
            # set the last element as the new one
            sentinel.prev[index] = node
            last_but_one.next[index] = node


    def remove(self, node, index, bounds):
        """Remove and return node from all lists in [0, index[."""
        for i in range(index):
            predecessor = node.prev[i]
            successor = node.next[i]
            predecessor.next[i] = successor
            successor.prev[i] = predecessor
            if bounds[i] > node.cargo[i]:
                bounds[i] = node.cargo[i]
        return node


    def reinsert(self, node, index, bounds):
        """Reinsert a node back into its previous position.

        Inserts node at the position it had in all lists in [0, index[
        before it was removed. This method assumes that the next and
        previous nodes of the node that is reinserted are in the list.

        """
        for i in range(index):
            node.prev[i].next[i] = node
            node.next[i].prev[i] = node
            if bounds[i] > node.cargo[i]:
                bounds[i] = node.cargo[i]
