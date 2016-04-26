import unittest
try:
    import mock
except ImportError: # pragma: no cover
    from unittest import mock
import numpy
import math
from ..blocked import *
from ..full import init

class TestBlocked(unittest.TestCase):

    def setUp(self):
        self.bdm = BlockDiagonalMatrix((2, 1), (2, 1))

    def tearDown(self):
        pass

    def assert_allclose(self, this, ref):
        for t, r in zip(this, ref):
            numpy.testing.assert_allclose(t, r)

    def test_rowdim(self):
        self.assertTupleEqual(self.bdm.nrow, (2, 1))

    def test_coldim(self):
        self.assertTupleEqual(self.bdm.ncol, (2, 1))

    def test_row_offset(self):
        self.assertTupleEqual(self.bdm.irow, (0, 2))

    def test_col_offset(self):
        self.assertTupleEqual(self.bdm.icol, (0, 2))

    def test_incompatible_dim_raises(self):
        self.assertRaises(AssertionError, BlockDiagonalMatrix, (1, 2), (3,))

    def test_str(self):
        self.assertEqual(str(self.bdm), """
Block 1

 (2, 2) 
              Column   1    Column   2

Block 2

 (1, 1) 
              Column   1
""")


    def test_init(self):
        self.bdm[0][:, :] = [[1, 3], [2, 4]]
        self.bdm[1][:, :] = [[5]]
        bdm = BlockDiagonalMatrix.init([[1, 2], [3, 4]], [[5]])
        numpy.testing.assert_allclose(bdm.subblock[0], self.bdm.subblock[0])
        numpy.testing.assert_allclose(bdm.subblock[1], self.bdm.subblock[1])


    def test_init_from_array_dimension_error(self):
        with self.assertRaises(AssertionError):
            bdm = BlockDiagonalMatrix.init_from_array(
                [1, 2, 3], (2, 1), (2, 1)
                )

    def test_init_from_array(self):
        self.bdm[0][:, :] = [[0, 2], [1, 3]]
        self.bdm[1][:, :] = [[4]]
        bdm = BlockDiagonalMatrix.init_from_array(range(5), (2, 1), (2, 1))
        numpy.testing.assert_allclose(bdm.subblock[0], self.bdm.subblock[0])
        numpy.testing.assert_allclose(bdm.subblock[1], self.bdm.subblock[1])

    def test_blocked_ravel(self):
        bdm = BlockDiagonalMatrix.init_from_array(range(5), (2, 1), (2, 1))
        numpy.testing.assert_allclose(bdm.ravel(order='F'), range(5))
        

    def test_unblock(self):
        blocked = BlockDiagonalMatrix((2, 1), (2, 1))
        blocked[0][:, :] = ((1, 2), (3, 4))
        blocked[1][:, :] = ((5,),)
        unblocked = [[1, 2, 0], [3, 4, 0], [0, 0, 5]]
        numpy.testing.assert_allclose(blocked.unblock(), unblocked)

    def test_pack(self):
        blocked = BlockDiagonalMatrix((2, 1), (2, 1))
        blocked[0][:, :] = ((1, 2), (2, 1))
        blocked[1][:, :] = ((5,),)
        packed = [[1, 2, 1], [5]]
        self.assert_allclose(blocked.pack().subblock, packed)
        

    def test_unit(self):
        ref = [[[1, 0], [0, 1]], [[1]]]
        blocked_unit = unit((2, 1))
        self.assert_allclose(blocked_unit, ref)

    def test_mul(self):
        self.bdm[0][:, :] = [[0, 1], [2, 3]]
        self.bdm[1][:, :] = [[2]]
        self.assert_allclose(self.bdm*self.bdm, [[[2, 3], [6, 11]], [[4]]])

    def test_rmul(self):
        self.bdm[0][:, :] = [[0, 1], [2, 3]]
        self.bdm[1][:, :] = [[2]]
        self.assert_allclose(2*self.bdm, [[[0, 2], [4, 6]], [[4]]])

    def test_add(self):
        self.bdm[0][:, :] = [[0, 1], [2, 3]]
        self.bdm[1][:, :] = [[2]]
        self.assert_allclose(self.bdm + self.bdm, [[[0, 2], [4, 6]], [[4]]])

    def test_sub(self):
        self.bdm[0][:, :] = [[0, 1], [2, 3]]
        self.bdm[1][:, :] = [[2]]
        self.assert_allclose(self.bdm - self.bdm, [[[0, 0], [0, 0]], [[0]]])

    def test_neg(self):
        self.bdm[0][:, :] = [[0, 1], [2, 3]]
        self.bdm[1][:, :] = [[2]]
        self.assert_allclose(-self.bdm, [[[0, -1], [-2, -3]], [[-2]]])

    def test_div(self):
        self.bdm[0][:, :] = [[0, 1], [2, 3]]
        self.bdm[1][:, :] = [[2]]
        self.assert_allclose(self.bdm/self.bdm, [[[1, 0], [0, 1]], [[1]]])

    def test_scalar_div(self):
        self.bdm[0][:, :] = [[0, 1], [2, 3]]
        self.bdm[1][:, :] = [[2]]
        self.assert_allclose(self.bdm/2, [[[0, .5], [1, 1.5]], [[1]]])

    def test_rdiv(self):
        self.bdm[0][:, :] = [[0, 1], [2, 3]]
        self.bdm[1][:, :] = [[2]]
        self.assert_allclose(1/self.bdm, [[[-1.5, 0.5], [1, 0]], [[0.5]]])

    def test_sqrt(self):
        self.bdm[0][:, :] = [[4, 0], [0, 4]]
        self.bdm[1][:, :] = [[9]]
        self.assert_allclose(self.bdm.sqrt(), [[[2, 0], [0, 2]], [[3]]])

    def test_isqrt(self):
        self.bdm[0][:, :] = [[4, 0], [0, 4]]
        self.bdm[1][:, :] = [[9]]
        self.assert_allclose(self.bdm.invsqrt(), [[[.5, 0], [0, .5]], [[1./3]]])

    def test_eigvec(self):
        self.bdm[0][:, :] = [[4, 0], [0, 4]]
        self.bdm[1][:, :] = [[9]]
        u, v = self.bdm.eigvec()
        self.assert_allclose(u, [4, 9])
        self.assert_allclose(v, [[[1, 0], [0, 1]], [[1]]])

    def test_transpose(self):
        self.bdm[0][:, :] = [[1, 2], [3, 4]]
        bdm_T = self.bdm.T()
        self.assert_allclose(bdm_T[0], [[1, 3], [2, 4]])

    def test_get_columns(self):
        self.bdm[0][:, :] = [[1, 2], [3, 4]]
        subset = self.bdm.get_columns((1, 0))
        self.assert_allclose(subset[0], [1, 3])

    def test_func(self):
        self.bdm[0][:, :] = [[1, 0], [0, 16]]
        self.bdm[1][:, :] = [[25]]
        self.assert_allclose(self.bdm.func(math.sqrt), [[[1, 0], [0, 4]], [[5]]])

    @mock.patch.object(numpy.random, 'random')
    def test_blocked_random(self, mock_random):
        M = BlockDiagonalMatrix([2], [2]).random()
        self.assertTrue(mock_random.calls, 2)

    def test_tr(self):
        M = BlockDiagonalMatrix([2, 1], [2, 1])
        M.subblock[0][0, 0] = 3
        M.subblock[0][1, 1] = 2
        M.subblock[1][0, 0] = 1
        self.assertEqual(M.tr(), 6.0)

    def test_qr_Q(self):
        A = BlockDiagonalMatrix([3], [3])
        A.subblock[0] = init([[12, 6, -4], [-51, 167, 24], [4, -68, -41]])
        Q, R = A.qr()
        numpy.testing.assert_almost_equal(Q[0], 
            -init([[6./7, 3./7, -2./7], [-69./175, 158./175, 6./35], [-58./175, 6./175, -33./35]])
            )
    def test_qr_R(self):
        A = BlockDiagonalMatrix([3], [3])
        A.subblock[0] = init([[12, 6, -4], [-51, 167, 24], [4, -68, -41]])
        Q, R = A[0].qr()
        numpy.testing.assert_almost_equal(R, 
            -init([[14, 0, 0], [21, 175, 0], [-14, -70, 35]])
            )
        numpy.testing.assert_almost_equal(A[0], Q*R)

    def test_gram_schmidt(self):
        S = BlockDiagonalMatrix([2], [2])
        v = BlockDiagonalMatrix([2], [2])
        Delta = 0.1
        S.subblock[0] = init([[1.0, Delta], [Delta, 1.0]])
        v.subblock[0] = init([[1.0, 0.0], [0.0, 1.0]])
        u = v.GS(S)
        u_ref = init([[1.0, 0.0], [-Delta/math.sqrt(1-Delta**2), 1.0/math.sqrt(1-Delta**2)]])
        numpy.testing.assert_almost_equal(u[0], u_ref)
        
class BlockedTriangularTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_str(self):
        bt = triangular((2, 1))
        self.assertEqual(str(bt), """
Block 1

    0.00000000
    0.00000000    0.00000000

Block 2

    0.00000000
"""
        ) 

    def test_init(self):
        bt = triangular.init([[1., 2., 3.], [4.]])
        numpy.testing.assert_almost_equal(bt.subblock[0], [1., 2., 3.])
        numpy.testing.assert_almost_equal(bt.subblock[1], [4.])

    @mock.patch.object(numpy.random, 'random')
    def test_blocked_random(self, mock_random):
        M = triangular([3, 2]).random()
        self.assertTrue(mock_random.calls, 2)
        
    def test_add(self):
        bt = triangular.init([[1., 2., 3.], [4.]])
        bt = bt + bt
        numpy.testing.assert_almost_equal(bt.subblock[0], [2., 4., 6.])
        numpy.testing.assert_almost_equal(bt.subblock[1], [8.])

    def test_sub(self):
        bt = triangular.init([[1., 2., 3.], [4.]])
        bt = bt - bt
        numpy.testing.assert_almost_equal(bt.subblock[0], [0., 0., 0.])
        numpy.testing.assert_almost_equal(bt.subblock[1], [0.])

    def test_unpack(self):
        bt = triangular.init([[1., 2., 3.], [4.]])
        ubt = bt.unpack()
        numpy.testing.assert_almost_equal(ubt.subblock[0], [[1, 2], [2, 3]])
        numpy.testing.assert_almost_equal(ubt.subblock[1], [[4]])

    def test_unblock(self):
        bt = triangular.init([[1., 2., 3.], [4.]])
        ubl = bt.unblock()
        numpy.testing.assert_almost_equal(ubl, [1., 2., 3., 0., 0., 4.])


if __name__ == "__main__": # pragma: no cover
    unittest.main()
