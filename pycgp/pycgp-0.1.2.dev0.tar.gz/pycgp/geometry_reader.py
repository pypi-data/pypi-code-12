import h5py
import numpy as np
from scipy.sparse import csr_matrix
from os.path import expanduser

from .topological_point_set import TopologicalPointSet


class GeometryReader:
    def __init__(self, filename, verbose=False):

        fn  = expanduser(filename)
        self.geometry_file = h5py.File(fn, 'r')
        self.verbose = verbose

        self._max_labels = self._data('max-labels')
        self._shape = self._data('segmentation-shape')
        self._part_counter = [self._data('parts-counters-%d' % (i + 1))
                              for i in range(3)]
        self._bounds = [self._data('neighborhood-%d' % i) for i in range(3)]

        # inverse mapping for "bounded_by" query
        self._bounded_by = [None]*4
        for cell_order in range(1, 4):
            n_elements = self._max_labels[cell_order]
            bounds = self._bounds[cell_order - 1]
            labels = np.arange(1, bounds.shape[1] + 1)
            labels = np.repeat(np.reshape(labels, (1, -1)), bounds.shape[0],
                               axis=0)
            self._bounded_by[cell_order] = csr_matrix(
                (labels.ravel(), (bounds.ravel(), labels.ravel())),
                shape=(n_elements + 1, bounds.shape[1] + 1))
        # read in number-of-bins attribute
        self._n_bins = self.geometry_file.attrs['number-of-bins']

    def max_label(self, cell_order):
        self._check_precondition(cell_order, None, (0, 1, 2, 3))
        return self._max_labels[cell_order]

    def size(self, cell_order, label):
        self._check_precondition(cell_order, label, (0, 1, 2, 3))
        if cell_order == 0:
            return 1
        sizes = [self._sets_data(cell_order, label, part).shape[1]
                 for part in range(self._num_parts(cell_order, label))]
        return np.sum(sizes)

    def shape(self):
        return self._shape

    def zero_set(self, label):
        self._check_precondition(0, label, (0,))
        point_data = self._sets_data(0, label).T
        return TopologicalPointSet(0, point_data)

    def one_set(self, label):
        self._check_precondition(1, label, (1,))
        return TopologicalPointSet(1, self._point_data(1, label))

    def two_set(self, label):
        self._check_precondition(2, label, (2,))
        return TopologicalPointSet(2, self._point_data(2, label))

    def three_set(self, label):
        self._check_precondition(3, label, (3,))
        return TopologicalPointSet(3, self._point_data(3, label))

    def topological_point_set(self, cell_order, label):
        self._check_precondition(cell_order, label, (1, 2, 3))
        return TopologicalPointSet(cell_order, self._point_data(cell_order, label))

    def bounds(self, cell_order, label):
        self._check_precondition(cell_order, label, (0, 1, 2))
        neighbors = self._bounds[cell_order][:, label - 1]
        return np.setdiff1d(neighbors, [0])

    def bounded_by(self, cell_order, label):
        self._check_precondition(cell_order, label, (1, 2, 3))
        return self._bounded_by[cell_order][label].data

    def adjacent(self, cell_order, label):
        self._check_precondition(cell_order, label, (1, 2, 3))
        adjacent = np.unique(
            [adj_label for bound_label in self.bounded_by(cell_order, label)
             for adj_label in self.bounds(cell_order-1, bound_label)])
        return np.setdiff1d(adjacent, label)

    def _data(self, group):
        try:
            return np.array(self.geometry_file[group])
        except:
            if self.verbose:
                print('WARNING: group "%s" not found in %s' % (group, self.geometry_file.filename))
            return np.array([]).reshape((0,0))

    def _sets_data(self, cell_order, label, part_number=None):
        bin_number = self._bin_number(label)
        group = '%d-sets/bin-%d/%d' % (cell_order, bin_number, label)
        if part_number is not None:
            group = '%s-%d' % (group, part_number + 1)
        return np.array(self.geometry_file[group])

    def _point_data(self, cell_order, label):
        data = self._sets_data(cell_order, label, 0)
        for part in range(1, self._num_parts(cell_order, label)):
            sets_data = self._sets_data(cell_order, label, part)
            data = np.concatenate((data, sets_data), axis=1)
        return data.T

    def _num_parts(self, cell_order, label):
        return self._part_counter[cell_order - 1][label - 1]

    def _bin_number(self, label):
        return label % self._n_bins

    def _check_precondition(self, cell_order, label, valid_cell_order):
        assert cell_order in valid_cell_order, \
            '"cell_order" must be in %s, but %d given' % (valid_cell_order, cell_order)
        assert label == None or label > 0 and label <= self._max_labels[cell_order], \
            '"label" must be in [0,...,%d], but %d given' % (self._max_labels[cell_order], label)
