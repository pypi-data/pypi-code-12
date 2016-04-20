from __future__ import division, absolute_import, print_function

import sys
import warnings
import functools

import numpy as np
from numpy.core.multiarray_tests import array_indexing
from itertools import product
from numpy.testing import (
    TestCase, run_module_suite, assert_, assert_equal, assert_raises,
    assert_array_equal, assert_warns
)


try:
    cdll = np.ctypeslib.load_library('multiarray', np.core.multiarray.__file__)
    _HAS_CTYPE = True
except ImportError:
    _HAS_CTYPE = False


class TestIndexing(TestCase):
    def test_none_index(self):
        # `None` index adds newaxis
        a = np.array([1, 2, 3])
        assert_equal(a[None], a[np.newaxis])
        assert_equal(a[None].ndim, a.ndim + 1)

    def test_empty_tuple_index(self):
        # Empty tuple index creates a view
        a = np.array([1, 2, 3])
        assert_equal(a[()], a)
        assert_(a[()].base is a)
        a = np.array(0)
        assert_(isinstance(a[()], np.int_))

        # Regression, it needs to fall through integer and fancy indexing
        # cases, so need the with statement to ignore the non-integer error.
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', '', DeprecationWarning)
            a = np.array([1.])
            assert_(isinstance(a[0.], np.float_))

            a = np.array([np.array(1)], dtype=object)
            assert_(isinstance(a[0.], np.ndarray))

    def test_same_kind_index_casting(self):
        # Indexes should be cast with same-kind and not safe, even if
        # that is somewhat unsafe. So test various different code paths.
        index = np.arange(5)
        u_index = index.astype(np.uintp)
        arr = np.arange(10)

        assert_array_equal(arr[index], arr[u_index])
        arr[u_index] = np.arange(5)
        assert_array_equal(arr, np.arange(10))

        arr = np.arange(10).reshape(5, 2)
        assert_array_equal(arr[index], arr[u_index])

        arr[u_index] = np.arange(5)[:,None]
        assert_array_equal(arr, np.arange(5)[:,None].repeat(2, axis=1))

        arr = np.arange(25).reshape(5, 5)
        assert_array_equal(arr[u_index, u_index], arr[index, index])

    def test_empty_fancy_index(self):
        # Empty list index creates an empty array
        # with the same dtype (but with weird shape)
        a = np.array([1, 2, 3])
        assert_equal(a[[]], [])
        assert_equal(a[[]].dtype, a.dtype)

        b = np.array([], dtype=np.intp)
        assert_equal(a[[]], [])
        assert_equal(a[[]].dtype, a.dtype)

        b = np.array([])
        assert_raises(IndexError, a.__getitem__, b)

    def test_ellipsis_index(self):
        # Ellipsis index does not create a view
        a = np.array([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]])
        assert_equal(a[...], a)
        assert_(a[...].base is a)  # `a[...]` was `a` in numpy <1.9.)

        # Slicing with ellipsis can skip an
        # arbitrary number of dimensions
        assert_equal(a[0, ...], a[0])
        assert_equal(a[0, ...], a[0,:])
        assert_equal(a[..., 0], a[:, 0])

        # Slicing with ellipsis always results
        # in an array, not a scalar
        assert_equal(a[0, ..., 1], np.array(2))

        # Assignment with `(Ellipsis,)` on 0-d arrays
        b = np.array(1)
        b[(Ellipsis,)] = 2
        assert_equal(b, 2)

    def test_single_int_index(self):
        # Single integer index selects one row
        a = np.array([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]])

        assert_equal(a[0], [1, 2, 3])
        assert_equal(a[-1], [7, 8, 9])

        # Index out of bounds produces IndexError
        assert_raises(IndexError, a.__getitem__, 1 << 30)
        # Index overflow produces IndexError
        assert_raises(IndexError, a.__getitem__, 1 << 64)

    def test_single_bool_index(self):
        # Single boolean index
        a = np.array([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]])

        # Python boolean converts to integer
        # These are being deprecated (and test in test_deprecations)
        #assert_equal(a[True], a[1])
        #assert_equal(a[False], a[0])

        # Same with NumPy boolean scalar
        # Before DEPRECATE, this is an error (as always, but telling about
        # future change):
        assert_raises(IndexError, a.__getitem__, np.array(True))
        assert_raises(IndexError, a.__getitem__, np.array(False))
        # After DEPRECATE, this behaviour can be enabled:
        #assert_equal(a[np.array(True)], a[None])
        #assert_equal(a[np.array(False), a[None][0:0]])

    def test_boolean_indexing_onedim(self):
        # Indexing a 2-dimensional array with
        # boolean array of length one
        a = np.array([[ 0.,  0.,  0.]])
        b = np.array([ True], dtype=bool)
        assert_equal(a[b], a)
        # boolean assignment
        a[b] = 1.
        assert_equal(a, [[1., 1., 1.]])

    def test_boolean_assignment_value_mismatch(self):
        # A boolean assignment should fail when the shape of the values
        # cannot be broadcast to the subscription. (see also gh-3458)
        a = np.arange(4)

        def f(a, v):
            a[a > -1] = v

        assert_raises(ValueError, f, a, [])
        assert_raises(ValueError, f, a, [1, 2, 3])
        assert_raises(ValueError, f, a[:1], [1, 2, 3])

    def test_boolean_indexing_twodim(self):
        # Indexing a 2-dimensional array with
        # 2-dimensional boolean array
        a = np.array([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]])
        b = np.array([[ True, False,  True],
                      [False,  True, False],
                      [ True, False,  True]])
        assert_equal(a[b], [1, 3, 5, 7, 9])
        assert_equal(a[b[1]], [[4, 5, 6]])
        assert_equal(a[b[0]], a[b[2]])

        # boolean assignment
        a[b] = 0
        assert_equal(a, [[0, 2, 0],
                         [4, 0, 6],
                         [0, 8, 0]])

    def test_reverse_strides_and_subspace_bufferinit(self):
        # This tests that the strides are not reversed for simple and
        # subspace fancy indexing.
        a = np.ones(5)
        b = np.zeros(5, dtype=np.intp)[::-1]
        c = np.arange(5)[::-1]

        a[b] = c
        # If the strides are not reversed, the 0 in the arange comes last.
        assert_equal(a[0], 0)

        # This also tests that the subspace buffer is initialized:
        a = np.ones((5, 2))
        c = np.arange(10).reshape(5, 2)[::-1]
        a[b, :] = c
        assert_equal(a[0], [0, 1])

    def test_reversed_strides_result_allocation(self):
        # Test a bug when calculating the output strides for a result array
        # when the subspace size was 1 (and test other cases as well)
        a = np.arange(10)[:, None]
        i = np.arange(10)[::-1]
        assert_array_equal(a[i], a[i.copy('C')])

        a = np.arange(20).reshape(-1, 2)

    def test_uncontiguous_subspace_assignment(self):
        # During development there was a bug activating a skip logic
        # based on ndim instead of size.
        a = np.full((3, 4, 2), -1)
        b = np.full((3, 4, 2), -1)

        a[[0, 1]] = np.arange(2 * 4 * 2).reshape(2, 4, 2).T
        b[[0, 1]] = np.arange(2 * 4 * 2).reshape(2, 4, 2).T.copy()

        assert_equal(a, b)

    def test_too_many_fancy_indices_special_case(self):
        # Just documents behaviour, this is a small limitation.
        a = np.ones((1,) * 32)  # 32 is NPY_MAXDIMS
        assert_raises(IndexError, a.__getitem__, (np.array([0]),) * 32)

    def test_scalar_array_bool(self):
        # Numpy bools can be used as boolean index (python ones as of yet not)
        a = np.array(1)
        assert_equal(a[np.bool_(True)], a[np.array(True)])
        assert_equal(a[np.bool_(False)], a[np.array(False)])

        # After deprecating bools as integers:
        #a = np.array([0,1,2])
        #assert_equal(a[True, :], a[None, :])
        #assert_equal(a[:, True], a[:, None])
        #
        #assert_(not np.may_share_memory(a, a[True, :]))

    def test_everything_returns_views(self):
        # Before `...` would return a itself.
        a = np.arange(5)

        assert_(a is not a[()])
        assert_(a is not a[...])
        assert_(a is not a[:])

    def test_broaderrors_indexing(self):
        a = np.zeros((5, 5))
        assert_raises(IndexError, a.__getitem__, ([0, 1], [0, 1, 2]))
        assert_raises(IndexError, a.__setitem__, ([0, 1], [0, 1, 2]), 0)

    def test_trivial_fancy_out_of_bounds(self):
        a = np.zeros(5)
        ind = np.ones(20, dtype=np.intp)
        ind[-1] = 10
        assert_raises(IndexError, a.__getitem__, ind)
        assert_raises(IndexError, a.__setitem__, ind, 0)
        ind = np.ones(20, dtype=np.intp)
        ind[0] = 11
        assert_raises(IndexError, a.__getitem__, ind)
        assert_raises(IndexError, a.__setitem__, ind, 0)

    def test_nonbaseclass_values(self):
        class SubClass(np.ndarray):
            def __array_finalize__(self, old):
                # Have array finalize do funny things
                self.fill(99)

        a = np.zeros((5, 5))
        s = a.copy().view(type=SubClass)
        s.fill(1)

        a[[0, 1, 2, 3, 4], :] = s
        assert_((a == 1).all())

        # Subspace is last, so transposing might want to finalize
        a[:, [0, 1, 2, 3, 4]] = s
        assert_((a == 1).all())

        a.fill(0)
        a[...] = s
        assert_((a == 1).all())

    def test_subclass_writeable(self):
        d = np.rec.array([('NGC1001', 11), ('NGC1002', 1.), ('NGC1003', 1.)],
                         dtype=[('target', 'S20'), ('V_mag', '>f4')])
        ind = np.array([False,  True,  True], dtype=bool)
        assert_(d[ind].flags.writeable)
        ind = np.array([0, 1])
        assert_(d[ind].flags.writeable)
        assert_(d[...].flags.writeable)
        assert_(d[0].flags.writeable)

    def test_memory_order(self):
        # This is not necessary to preserve. Memory layouts for
        # more complex indices are not as simple.
        a = np.arange(10)
        b = np.arange(10).reshape(5,2).T
        assert_(a[b].flags.f_contiguous)

        # Takes a different implementation branch:
        a = a.reshape(-1, 1)
        assert_(a[b, 0].flags.f_contiguous)

    def test_scalar_return_type(self):
        # Full scalar indices should return scalars and object
        # arrays should not call PyArray_Return on their items
        class Zero(object):
            # The most basic valid indexing
            def __index__(self):
                return 0

        z = Zero()

        class ArrayLike(object):
            # Simple array, should behave like the array
            def __array__(self):
                return np.array(0)

        a = np.zeros(())
        assert_(isinstance(a[()], np.float_))
        a = np.zeros(1)
        assert_(isinstance(a[z], np.float_))
        a = np.zeros((1, 1))
        assert_(isinstance(a[z, np.array(0)], np.float_))
        assert_(isinstance(a[z, ArrayLike()], np.float_))

        # And object arrays do not call it too often:
        b = np.array(0)
        a = np.array(0, dtype=object)
        a[()] = b
        assert_(isinstance(a[()], np.ndarray))
        a = np.array([b, None])
        assert_(isinstance(a[z], np.ndarray))
        a = np.array([[b, None]])
        assert_(isinstance(a[z, np.array(0)], np.ndarray))
        assert_(isinstance(a[z, ArrayLike()], np.ndarray))

    def test_small_regressions(self):
        # Reference count of intp for index checks
        a = np.array([0])
        refcount = sys.getrefcount(np.dtype(np.intp))
        # item setting always checks indices in separate function:
        a[np.array([0], dtype=np.intp)] = 1
        a[np.array([0], dtype=np.uint8)] = 1
        assert_raises(IndexError, a.__setitem__,
                      np.array([1], dtype=np.intp), 1)
        assert_raises(IndexError, a.__setitem__,
                      np.array([1], dtype=np.uint8), 1)

        assert_equal(sys.getrefcount(np.dtype(np.intp)), refcount)

    def test_unaligned(self):
        v = (np.zeros(64, dtype=np.int8) + ord('a'))[1:-7]
        d = v.view(np.dtype("S8"))
        # unaligned source
        x = (np.zeros(16, dtype=np.int8) + ord('a'))[1:-7]
        x = x.view(np.dtype("S8"))
        x[...] = np.array("b" * 8, dtype="S")
        b = np.arange(d.size)
        #trivial
        assert_equal(d[b], d)
        d[b] = x
        # nontrivial
        # unaligned index array
        b = np.zeros(d.size + 1).view(np.int8)[1:-(np.intp(0).itemsize - 1)]
        b = b.view(np.intp)[:d.size]
        b[...] = np.arange(d.size)
        assert_equal(d[b.astype(np.int16)], d)
        d[b.astype(np.int16)] = x
        # boolean
        d[b % 2 == 0]
        d[b % 2 == 0] = x[::2]

    def test_tuple_subclass(self):
        arr = np.ones((5, 5))

        # A tuple subclass should also be an nd-index
        class TupleSubclass(tuple):
            pass
        index = ([1], [1])
        index = TupleSubclass(index)
        assert_(arr[index].shape == (1,))
        # Unlike the non nd-index:
        assert_(arr[index,].shape != (1,))

    def test_broken_sequence_not_nd_index(self):
        # See gh-5063:
        # If we have an object which claims to be a sequence, but fails
        # on item getting, this should not be converted to an nd-index (tuple)
        # If this object happens to be a valid index otherwise, it should work
        # This object here is very dubious and probably bad though:
        class SequenceLike(object):
            def __index__(self):
                return 0

            def __len__(self):
                return 1

            def __getitem__(self, item):
                raise IndexError('Not possible')

        arr = np.arange(10)
        assert_array_equal(arr[SequenceLike()], arr[SequenceLike(),])

        # also test that field indexing does not segfault
        # for a similar reason, by indexing a structured array
        arr = np.zeros((1,), dtype=[('f1', 'i8'), ('f2', 'i8')])
        assert_array_equal(arr[SequenceLike()], arr[SequenceLike(),])

    def test_indexing_array_weird_strides(self):
        # See also gh-6221
        # the shapes used here come from the issue and create the correct
        # size for the iterator buffering size.
        x = np.ones(10)
        x2 = np.ones((10, 2))
        ind = np.arange(10)[:, None, None, None]
        ind = np.broadcast_to(ind, (10, 55, 4, 4))

        # single advanced index case
        assert_array_equal(x[ind], x[ind.copy()])
        # higher dimensional advanced index
        zind = np.zeros(4, dtype=np.intp)
        assert_array_equal(x2[ind, zind], x2[ind.copy(), zind])


class TestFieldIndexing(TestCase):
    def test_scalar_return_type(self):
        # Field access on an array should return an array, even if it
        # is 0-d.
        a = np.zeros((), [('a','f8')])
        assert_(isinstance(a['a'], np.ndarray))
        assert_(isinstance(a[['a']], np.ndarray))


class TestBroadcastedAssignments(TestCase):
    def assign(self, a, ind, val):
        a[ind] = val
        return a

    def test_prepending_ones(self):
        a = np.zeros((3, 2))

        a[...] = np.ones((1, 3, 2))
        # Fancy with subspace with and without transpose
        a[[0, 1, 2], :] = np.ones((1, 3, 2))
        a[:, [0, 1]] = np.ones((1, 3, 2))
        # Fancy without subspace (with broadcasting)
        a[[[0], [1], [2]], [0, 1]] = np.ones((1, 3, 2))

    def test_prepend_not_one(self):
        assign = self.assign
        s_ = np.s_

        a = np.zeros(5)

        # Too large and not only ones.
        assert_raises(ValueError, assign, a, s_[...],  np.ones((2, 1)))

        with warnings.catch_warnings():
            # Will be a ValueError as well.
            warnings.simplefilter("error", DeprecationWarning)
            assert_raises(DeprecationWarning, assign, a, s_[[1, 2, 3],],
                          np.ones((2, 1)))
            assert_raises(DeprecationWarning, assign, a, s_[[[1], [2]],],
                          np.ones((2,2,1)))

    def test_simple_broadcasting_errors(self):
        assign = self.assign
        s_ = np.s_

        a = np.zeros((5, 1))
        assert_raises(ValueError, assign, a, s_[...], np.zeros((5, 2)))
        assert_raises(ValueError, assign, a, s_[...], np.zeros((5, 0)))

        assert_raises(ValueError, assign, a, s_[:, [0]], np.zeros((5, 2)))
        assert_raises(ValueError, assign, a, s_[:, [0]], np.zeros((5, 0)))

        assert_raises(ValueError, assign, a, s_[[0], :], np.zeros((2, 1)))

    def test_index_is_larger(self):
        # Simple case of fancy index broadcasting of the index.
        a = np.zeros((5, 5))
        a[[[0], [1], [2]], [0, 1, 2]] = [2, 3, 4]

        assert_((a[:3, :3] == [2, 3, 4]).all())

    def test_broadcast_subspace(self):
        a = np.zeros((100, 100))
        v = np.arange(100)[:,None]
        b = np.arange(100)[::-1]
        a[b] = v
        assert_((a[::-1] == v).all())


class TestSubclasses(TestCase):
    def test_basic(self):
        class SubClass(np.ndarray):
            pass

        s = np.arange(5).view(SubClass)
        assert_(isinstance(s[:3], SubClass))
        assert_(s[:3].base is s)

        assert_(isinstance(s[[0, 1, 2]], SubClass))
        assert_(isinstance(s[s > 0], SubClass))

    def test_matrix_fancy(self):
        # The matrix class messes with the shape. While this is always
        # weird (getitem is not used, it does not have setitem nor knows
        # about fancy indexing), this tests gh-3110
        m = np.matrix([[1, 2], [3, 4]])

        assert_(isinstance(m[[0,1,0], :], np.matrix))

        # gh-3110. Note the transpose currently because matrices do *not*
        # support dimension fixing for fancy indexing correctly.
        x = np.asmatrix(np.arange(50).reshape(5,10))
        assert_equal(x[:2, np.array(-1)], x[:2, -1].T)

    def test_finalize_gets_full_info(self):
        # Array finalize should be called on the filled array.
        class SubClass(np.ndarray):
            def __array_finalize__(self, old):
                self.finalize_status = np.array(self)
                self.old = old

        s = np.arange(10).view(SubClass)
        new_s = s[:3]
        assert_array_equal(new_s.finalize_status, new_s)
        assert_array_equal(new_s.old, s)

        new_s = s[[0,1,2,3]]
        assert_array_equal(new_s.finalize_status, new_s)
        assert_array_equal(new_s.old, s)

        new_s = s[s > 0]
        assert_array_equal(new_s.finalize_status, new_s)
        assert_array_equal(new_s.old, s)

class TestFancingIndexingCast(TestCase):
    def test_boolean_index_cast_assign(self):
        # Setup the boolean index and float arrays.
        shape = (8, 63)
        bool_index = np.zeros(shape).astype(bool)
        bool_index[0, 1] = True
        zero_array = np.zeros(shape)

        # Assigning float is fine.
        zero_array[bool_index] = np.array([1])
        assert_equal(zero_array[0, 1], 1)

        # Fancy indexing works, although we get a cast warning.
        assert_warns(np.ComplexWarning,
                     zero_array.__setitem__, ([0], [1]), np.array([2 + 1j]))
        assert_equal(zero_array[0, 1], 2)  # No complex part

        # Cast complex to float, throwing away the imaginary portion.
        assert_warns(np.ComplexWarning,
                     zero_array.__setitem__, bool_index, np.array([1j]))
        assert_equal(zero_array[0, 1], 0)

class TestFancyIndexingEquivalence(TestCase):
    def test_object_assign(self):
        # Check that the field and object special case using copyto is active.
        # The right hand side cannot be converted to an array here.
        a = np.arange(5, dtype=object)
        b = a.copy()
        a[:3] = [1, (1,2), 3]
        b[[0, 1, 2]] = [1, (1,2), 3]
        assert_array_equal(a, b)

        # test same for subspace fancy indexing
        b = np.arange(5, dtype=object)[None, :]
        b[[0], :3] = [[1, (1,2), 3]]
        assert_array_equal(a, b[0])

        # Check that swapping of axes works.
        # There was a bug that made the later assignment throw a ValueError
        # do to an incorrectly transposed temporary right hand side (gh-5714)
        b = b.T
        b[:3, [0]] = [[1], [(1,2)], [3]]
        assert_array_equal(a, b[:, 0])

        # Another test for the memory order of the subspace
        arr = np.ones((3, 4, 5), dtype=object)
        # Equivalent slicing assignment for comparison
        cmp_arr = arr.copy()
        cmp_arr[:1, ...] = [[[1], [2], [3], [4]]]
        arr[[0], ...] = [[[1], [2], [3], [4]]]
        assert_array_equal(arr, cmp_arr)
        arr = arr.copy('F')
        arr[[0], ...] = [[[1], [2], [3], [4]]]
        assert_array_equal(arr, cmp_arr)

    def test_cast_equivalence(self):
        # Yes, normal slicing uses unsafe casting.
        a = np.arange(5)
        b = a.copy()

        a[:3] = np.array(['2', '-3', '-1'])
        b[[0, 2, 1]] = np.array(['2', '-1', '-3'])
        assert_array_equal(a, b)

        # test the same for subspace fancy indexing
        b = np.arange(5)[None, :]
        b[[0], :3] = np.array([['2', '-3', '-1']])
        assert_array_equal(a, b[0])


class TestMultiIndexingAutomated(TestCase):
    """
     These test use code to mimic the C-Code indexing for selection.

     NOTE: * This still lacks tests for complex item setting.
           * If you change behavior of indexing, you might want to modify
             these tests to try more combinations.
           * Behavior was written to match numpy version 1.8. (though a
             first version matched 1.7.)
           * Only tuple indices are supported by the mimicking code.
             (and tested as of writing this)
           * Error types should match most of the time as long as there
             is only one error. For multiple errors, what gets raised
             will usually not be the same one. They are *not* tested.
    """

    def setUp(self):
        self.a = np.arange(np.prod([3, 1, 5, 6])).reshape(3, 1, 5, 6)
        self.b = np.empty((3, 0, 5, 6))
        self.complex_indices = ['skip', Ellipsis,
            0,
            # Boolean indices, up to 3-d for some special cases of eating up
            # dimensions, also need to test all False
            np.array(False),
            np.array([True, False, False]),
            np.array([[True, False], [False, True]]),
            np.array([[[False, False], [False, False]]]),
            # Some slices:
            slice(-5, 5, 2),
            slice(1, 1, 100),
            slice(4, -1, -2),
            slice(None, None, -3),
            # Some Fancy indexes:
            np.empty((0, 1, 1), dtype=np.intp),  # empty and can be broadcast
            np.array([0, 1, -2]),
            np.array([[2], [0], [1]]),
            np.array([[0, -1], [0, 1]], dtype=np.dtype('intp').newbyteorder()),
            np.array([2, -1], dtype=np.int8),
            np.zeros([1]*31, dtype=int),  # trigger too large array.
            np.array([0., 1.])]  # invalid datatype
        # Some simpler indices that still cover a bit more
        self.simple_indices = [Ellipsis, None, -1, [1], np.array([True]), 'skip']
        # Very simple ones to fill the rest:
        self.fill_indices = [slice(None, None), 0]

    def _get_multi_index(self, arr, indices):
        """Mimic multi dimensional indexing.

        Parameters
        ----------
        arr : ndarray
            Array to be indexed.
        indices : tuple of index objects

        Returns
        -------
        out : ndarray
            An array equivalent to the indexing operation (but always a copy).
            `arr[indices]` should be identical.
        no_copy : bool
            Whether the indexing operation requires a copy. If this is `True`,
            `np.may_share_memory(arr, arr[indicies])` should be `True` (with
            some exceptions for scalars and possibly 0-d arrays).

        Notes
        -----
        While the function may mostly match the errors of normal indexing this
        is generally not the case.
        """
        in_indices = list(indices)
        indices = []
        # if False, this is a fancy or boolean index
        no_copy = True
        # number of fancy/scalar indexes that are not consecutive
        num_fancy = 0
        # number of dimensions indexed by a "fancy" index
        fancy_dim = 0
        # NOTE: This is a funny twist (and probably OK to change).
        # The boolean array has illegal indexes, but this is
        # allowed if the broadcast fancy-indices are 0-sized.
        # This variable is to catch that case.
        error_unless_broadcast_to_empty = False

        # We need to handle Ellipsis and make arrays from indices, also
        # check if this is fancy indexing (set no_copy).
        ndim = 0
        ellipsis_pos = None  # define here mostly to replace all but first.
        for i, indx in enumerate(in_indices):
            if indx is None:
                continue
            if isinstance(indx, np.ndarray) and indx.dtype == bool:
                no_copy = False
                if indx.ndim == 0:
                    raise IndexError
                # boolean indices can have higher dimensions
                ndim += indx.ndim
                fancy_dim += indx.ndim
                continue
            if indx is Ellipsis:
                if ellipsis_pos is None:
                    ellipsis_pos = i
                    continue  # do not increment ndim counter
                raise IndexError
            if isinstance(indx, slice):
                ndim += 1
                continue
            if not isinstance(indx, np.ndarray):
                # This could be open for changes in numpy.
                # numpy should maybe raise an error if casting to intp
                # is not safe. It rejects np.array([1., 2.]) but not
                # [1., 2.] as index (same for ie. np.take).
                # (Note the importance of empty lists if changing this here)
                indx = np.array(indx, dtype=np.intp)
                in_indices[i] = indx
            elif indx.dtype.kind != 'b' and indx.dtype.kind != 'i':
                raise IndexError('arrays used as indices must be of integer (or boolean) type')
            if indx.ndim != 0:
                no_copy = False
            ndim += 1
            fancy_dim += 1

        if arr.ndim - ndim < 0:
            # we can't take more dimensions then we have, not even for 0-d arrays.
            # since a[()] makes sense, but not a[(),]. We will raise an error
            # later on, unless a broadcasting error occurs first.
            raise IndexError

        if ndim == 0 and None not in in_indices:
            # Well we have no indexes or one Ellipsis. This is legal.
            return arr.copy(), no_copy

        if ellipsis_pos is not None:
            in_indices[ellipsis_pos:ellipsis_pos+1] = [slice(None, None)] * (arr.ndim - ndim)

        for ax, indx in enumerate(in_indices):
            if isinstance(indx, slice):
                # convert to an index array
                indx = np.arange(*indx.indices(arr.shape[ax]))
                indices.append(['s', indx])
                continue
            elif indx is None:
                # this is like taking a slice with one element from a new axis:
                indices.append(['n', np.array([0], dtype=np.intp)])
                arr = arr.reshape((arr.shape[:ax] + (1,) + arr.shape[ax:]))
                continue
            if isinstance(indx, np.ndarray) and indx.dtype == bool:
                if indx.shape != arr.shape[ax:ax+indx.ndim]:
                    raise IndexError

                try:
                    flat_indx = np.ravel_multi_index(np.nonzero(indx),
                                    arr.shape[ax:ax+indx.ndim], mode='raise')
                except:
                    error_unless_broadcast_to_empty = True
                    # fill with 0s instead, and raise error later
                    flat_indx = np.array([0]*indx.sum(), dtype=np.intp)
                # concatenate axis into a single one:
                if indx.ndim != 0:
                    arr = arr.reshape((arr.shape[:ax]
                                  + (np.prod(arr.shape[ax:ax+indx.ndim]),)
                                  + arr.shape[ax+indx.ndim:]))
                    indx = flat_indx
                else:
                    # This could be changed, a 0-d boolean index can
                    # make sense (even outside the 0-d indexed array case)
                    # Note that originally this is could be interpreted as
                    # integer in the full integer special case.
                    raise IndexError
            else:
                # If the index is a singleton, the bounds check is done
                # before the broadcasting. This used to be different in <1.9
                if indx.ndim == 0:
                    if indx >= arr.shape[ax] or indx < -arr.shape[ax]:
                        raise IndexError
            if indx.ndim == 0:
                # The index is a scalar. This used to be two fold, but if fancy
                # indexing was active, the check was done later, possibly
                # after broadcasting it away (1.7. or earlier). Now it is always
                # done.
                if indx >= arr.shape[ax] or indx < - arr.shape[ax]:
                    raise IndexError
            if len(indices) > 0 and indices[-1][0] == 'f' and ax != ellipsis_pos:
                # NOTE: There could still have been a 0-sized Ellipsis
                # between them. Checked that with ellipsis_pos.
                indices[-1].append(indx)
            else:
                # We have a fancy index that is not after an existing one.
                # NOTE: A 0-d array triggers this as well, while
                # one may expect it to not trigger it, since a scalar
                # would not be considered fancy indexing.
                num_fancy += 1
                indices.append(['f', indx])

        if num_fancy > 1 and not no_copy:
            # We have to flush the fancy indexes left
            new_indices = indices[:]
            axes = list(range(arr.ndim))
            fancy_axes = []
            new_indices.insert(0, ['f'])
            ni = 0
            ai = 0
            for indx in indices:
                ni += 1
                if indx[0] == 'f':
                    new_indices[0].extend(indx[1:])
                    del new_indices[ni]
                    ni -= 1
                    for ax in range(ai, ai + len(indx[1:])):
                        fancy_axes.append(ax)
                        axes.remove(ax)
                ai += len(indx) - 1  # axis we are at
            indices = new_indices
            # and now we need to transpose arr:
            arr = arr.transpose(*(fancy_axes + axes))

        # We only have one 'f' index now and arr is transposed accordingly.
        # Now handle newaxis by reshaping...
        ax = 0
        for indx in indices:
            if indx[0] == 'f':
                if len(indx) == 1:
                    continue
                # First of all, reshape arr to combine fancy axes into one:
                orig_shape = arr.shape
                orig_slice = orig_shape[ax:ax + len(indx[1:])]
                arr = arr.reshape((arr.shape[:ax]
                                    + (np.prod(orig_slice).astype(int),)
                                    + arr.shape[ax + len(indx[1:]):]))

                # Check if broadcasting works
                if len(indx[1:]) != 1:
                    res = np.broadcast(*indx[1:])  # raises ValueError...
                else:
                    res = indx[1]
                # unfortunately the indices might be out of bounds. So check
                # that first, and use mode='wrap' then. However only if
                # there are any indices...
                if res.size != 0:
                    if error_unless_broadcast_to_empty:
                        raise IndexError
                    for _indx, _size in zip(indx[1:], orig_slice):
                        if _indx.size == 0:
                            continue
                        if np.any(_indx >= _size) or np.any(_indx < -_size):
                                raise IndexError
                if len(indx[1:]) == len(orig_slice):
                    if np.product(orig_slice) == 0:
                        # Work around for a crash or IndexError with 'wrap'
                        # in some 0-sized cases.
                        try:
                            mi = np.ravel_multi_index(indx[1:], orig_slice, mode='raise')
                        except:
                            # This happens with 0-sized orig_slice (sometimes?)
                            # here it is a ValueError, but indexing gives a:
                            raise IndexError('invalid index into 0-sized')
                    else:
                        mi = np.ravel_multi_index(indx[1:], orig_slice, mode='wrap')
                else:
                    # Maybe never happens...
                    raise ValueError
                arr = arr.take(mi.ravel(), axis=ax)
                arr = arr.reshape((arr.shape[:ax]
                                    + mi.shape
                                    + arr.shape[ax+1:]))
                ax += mi.ndim
                continue

            # If we are here, we have a 1D array for take:
            arr = arr.take(indx[1], axis=ax)
            ax += 1

        return arr, no_copy

    def _check_multi_index(self, arr, index):
        """Check a multi index item getting and simple setting.

        Parameters
        ----------
        arr : ndarray
            Array to be indexed, must be a reshaped arange.
        index : tuple of indexing objects
            Index being tested.
        """
        # Test item getting
        try:
            mimic_get, no_copy = self._get_multi_index(arr, index)
        except Exception:
            prev_refcount = sys.getrefcount(arr)
            assert_raises(Exception, arr.__getitem__, index)
            assert_raises(Exception, arr.__setitem__, index, 0)
            assert_equal(prev_refcount, sys.getrefcount(arr))
            return

        self._compare_index_result(arr, index, mimic_get, no_copy)

    def _check_single_index(self, arr, index):
        """Check a single index item getting and simple setting.

        Parameters
        ----------
        arr : ndarray
            Array to be indexed, must be an arange.
        index : indexing object
            Index being tested. Must be a single index and not a tuple
            of indexing objects (see also `_check_multi_index`).
        """
        try:
            mimic_get, no_copy = self._get_multi_index(arr, (index,))
        except Exception:
            prev_refcount = sys.getrefcount(arr)
            assert_raises(Exception, arr.__getitem__, index)
            assert_raises(Exception, arr.__setitem__, index, 0)
            assert_equal(prev_refcount, sys.getrefcount(arr))
            return

        self._compare_index_result(arr, index, mimic_get, no_copy)

    def _compare_index_result(self, arr, index, mimic_get, no_copy):
        """Compare mimicked result to indexing result.
        """
        arr = arr.copy()
        indexed_arr = arr[index]
        assert_array_equal(indexed_arr, mimic_get)
        # Check if we got a view, unless its a 0-sized or 0-d array.
        # (then its not a view, and that does not matter)
        if indexed_arr.size != 0 and indexed_arr.ndim != 0:
            assert_(np.may_share_memory(indexed_arr, arr) == no_copy)
            # Check reference count of the original array
            if no_copy:
                # refcount increases by one:
                assert_equal(sys.getrefcount(arr), 3)
            else:
                assert_equal(sys.getrefcount(arr), 2)

        # Test non-broadcast setitem:
        b = arr.copy()
        b[index] = mimic_get + 1000
        if b.size == 0:
            return  # nothing to compare here...
        if no_copy and indexed_arr.ndim != 0:
            # change indexed_arr in-place to manipulate original:
            indexed_arr += 1000
            assert_array_equal(arr, b)
            return
        # Use the fact that the array is originally an arange:
        arr.flat[indexed_arr.ravel()] += 1000
        assert_array_equal(arr, b)

    def test_boolean(self):
        a = np.array(5)
        assert_equal(a[np.array(True)], 5)
        a[np.array(True)] = 1
        assert_equal(a, 1)
        # NOTE: This is different from normal broadcasting, as
        # arr[boolean_array] works like in a multi index. Which means
        # it is aligned to the left. This is probably correct for
        # consistency with arr[boolean_array,] also no broadcasting
        # is done at all
        self._check_multi_index(self.a, (np.zeros_like(self.a, dtype=bool),))
        self._check_multi_index(self.a, (np.zeros_like(self.a, dtype=bool)[..., 0],))
        self._check_multi_index(self.a, (np.zeros_like(self.a, dtype=bool)[None, ...],))

    def test_multidim(self):
        # Automatically test combinations with complex indexes on 2nd (or 1st)
        # spot and the simple ones in one other spot.
        with warnings.catch_warnings():
            # This is so that np.array(True) is not accepted in a full integer
            # index, when running the file separately.
            warnings.filterwarnings('error', '', DeprecationWarning)
            warnings.filterwarnings('error', '', np.VisibleDeprecationWarning)

            def isskip(idx):
                return isinstance(idx, str) and idx == "skip"

            for simple_pos in [0, 2, 3]:
                tocheck = [self.fill_indices, self.complex_indices,
                           self.fill_indices, self.fill_indices]
                tocheck[simple_pos] = self.simple_indices
                for index in product(*tocheck):
                    index = tuple(i for i in index if not isskip(i))
                    self._check_multi_index(self.a, index)
                    self._check_multi_index(self.b, index)

        # Check very simple item getting:
        self._check_multi_index(self.a, (0, 0, 0, 0))
        self._check_multi_index(self.b, (0, 0, 0, 0))
        # Also check (simple cases of) too many indices:
        assert_raises(IndexError, self.a.__getitem__, (0, 0, 0, 0, 0))
        assert_raises(IndexError, self.a.__setitem__, (0, 0, 0, 0, 0), 0)
        assert_raises(IndexError, self.a.__getitem__, (0, 0, [1], 0, 0))
        assert_raises(IndexError, self.a.__setitem__, (0, 0, [1], 0, 0), 0)

    def test_1d(self):
        a = np.arange(10)
        with warnings.catch_warnings():
            warnings.filterwarnings('error', '', np.VisibleDeprecationWarning)
            for index in self.complex_indices:
                self._check_single_index(a, index)


class TestCApiAccess(TestCase):
    def test_getitem(self):
        subscript = functools.partial(array_indexing, 0)

        # 0-d arrays don't work:
        assert_raises(IndexError, subscript, np.ones(()), 0)
        # Out of bound values:
        assert_raises(IndexError, subscript, np.ones(10), 11)
        assert_raises(IndexError, subscript, np.ones(10), -11)
        assert_raises(IndexError, subscript, np.ones((10, 10)), 11)
        assert_raises(IndexError, subscript, np.ones((10, 10)), -11)

        a = np.arange(10)
        assert_array_equal(a[4], subscript(a, 4))
        a = a.reshape(5, 2)
        assert_array_equal(a[-4], subscript(a, -4))

    def test_setitem(self):
        assign = functools.partial(array_indexing, 1)

        # Deletion is impossible:
        assert_raises(ValueError, assign, np.ones(10), 0)
        # 0-d arrays don't work:
        assert_raises(IndexError, assign, np.ones(()), 0, 0)
        # Out of bound values:
        assert_raises(IndexError, assign, np.ones(10), 11, 0)
        assert_raises(IndexError, assign, np.ones(10), -11, 0)
        assert_raises(IndexError, assign, np.ones((10, 10)), 11, 0)
        assert_raises(IndexError, assign, np.ones((10, 10)), -11, 0)

        a = np.arange(10)
        assign(a, 4, 10)
        assert_(a[4] == 10)

        a = a.reshape(5, 2)
        assign(a, 4, 10)
        assert_array_equal(a[-1], [10, 10])


if __name__ == "__main__":
    run_module_suite()
