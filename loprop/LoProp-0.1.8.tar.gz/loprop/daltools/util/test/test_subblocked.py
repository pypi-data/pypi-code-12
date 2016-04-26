import unittest
import numpy
from ..subblocked import matrix as SubBlockedMatrix


class NewTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_str(self):
        asb = SubBlockedMatrix([2,1], [2,1])
        print(asb)
        self.assertEqual(str(asb), """
Block (1,1)

 (2, 2) 
              Column   1    Column   2

Block (1,2)

 (2, 1) 
              Column   1

Block (2,1)

 (1, 2) 
              Column   1    Column   2

Block (2,2)

 (1, 1) 
              Column   1
"""
        )


    def test_tranpose_diagonal_block(self):
        A = SubBlockedMatrix([2], [2])
        A.subblock[0][0][:, :] = [[1., 2.], [3., 4]]
        AT = A.T()
        numpy.testing.assert_allclose(AT.subblock[0][0], [[1., 3.], [2., 4.]])

    def test_tranpose_offdiagonal_block(self):
        A = SubBlockedMatrix([1, 2], [1, 2])
        A.subblock[0][1][:, :] = [[1., 2.]]
        AT = A.T()
        numpy.testing.assert_allclose(AT.subblock[1][0], [[1.], [2.]])

    def test_mul(self):
        A = SubBlockedMatrix([2, 1], [2, 1])
        A.subblock[0][0][:, :] = [[1., 0.], [0., 1.]]
        A.subblock[1][1][:, :] = 1.0

        A2 = A*A
        numpy.testing.assert_allclose(A2.subblock[0][0], A2.subblock[0][0])

    def test_random(self):
        A = SubBlockedMatrix([2], [2])
        numpy.random.seed(0)
        A.random()
        numpy.testing.assert_allclose(A.subblock[0][0], [
            [ 0.5488135 ,  0.71518937],
            [ 0.60276338,  0.54488318]
           ])

    def test_unblock(self):
        A = SubBlockedMatrix([2], [2])
        numpy.random.seed(0)
        A.random()
        Afull = A.unblock()
        numpy.testing.assert_allclose(Afull, [
            [ 0.5488135 ,  0.71518937],
            [ 0.60276338,  0.54488318]
           ])


if __name__ == "__main__": #pragma: no cover
    unittest.main()
