import tempfile
import os
import sys
import itertools
from operator import mul
import numpy
import cf
import unittest

class CoordinateTest(unittest.TestCase):
    print 'cf version', cf.__version__, 'running from', os.path.abspath(cf.__file__)

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]

    def test_Coordinate_squeeze(self):
        '''cf.Coordinate.squeeze'''
        print

        a = numpy.arange(89.5, -90, -1)
        b = numpy.empty(a.shape+(2,))
        b[:,0] = a+0.5
        b[:,1] = a-0.5

        c = cf.Coordinate(data=cf.Data(a), bounds=cf.Data(b))

        for chunksize in chunk_sizes[::-1]:
            cf.CHUNKSIZE(chunksize)
            self.assertTrue(c.equals(c.squeeze(), traceback=True))

        print "cf.Coordinate.squeeze passed", "pmshape =", c.Data._pmshape
    #--- End: def

    def test_Coordinate_roll(self):
        '''cf.Coordinate.roll'''
        print

        modulus = 10
        for a in (numpy.arange(modulus), numpy.arange(modulus)[::-1]):

            c = cf.DimensionCoordinate(data=cf.Data(a, 'km')) # Add bounds
            c.period(cf.Data(1000*modulus, 'm'))
            pmshape = c.Data._pmshape
            
            for offset in (-16, -10, -6, 0, 6, 10, 16, 20):
                d = c + offset                               
                for shift in range(offset-21, offset+22):
                    if d.direction():
                        centre = (d.datum(-1)//modulus)*modulus
                        a0 = d.datum(0) - (shift % modulus)
                        if a0 <= centre - modulus:
                            a0 += modulus
                        a1 = a0 + modulus
                        step = 1
                    else:
                        centre = (d.datum(0)//modulus)*modulus
                        a0 = d.datum(0) + (shift % modulus)
                        if a0 >= centre + modulus:
                            a0 -= modulus
                        a1 = a0 - modulus
                        step = -1

                    e = d.roll(0, shift).array
                    b = numpy.arange(a0, a1, step)
                    self.assertTrue(
                        (e == b).all(),
                        '%s, shift=%s (%s), %s, %s' % (d.array, shift, shift%modulus, e, b))
                #--- End: for
            #--- End: for
        #--- End: for
        print "cf.DimensionCoordinate.roll passed", "pmshape =", pmshape
    #--- End: def

    def test_Coordinate_flip(self):
        '''cf.Coordinate.flip'''
        print

        a = numpy.arange(89.5, -90, -1)
        b = numpy.empty(a.shape+(2,))
        b[:,0] = a+0.5
        b[:,1] = a-0.5

        c = cf.Coordinate(data=cf.Data(a), bounds=cf.Data(b))

        for chunksize in chunk_sizes[::-1]:
            cf.CHUNKSIZE(chunksize)
            d1 = c.flip()
            d1.flip(i=True)
            self.assertTrue(c.equals(d1, traceback=True))

        print "cf.Coordinate.flip passed", "pmshape =", c.Data._pmshape
    #--- End: def

    def test_Coordinate_transpose(self):
        '''cf.Coordinate.flip'''
        print

        a = numpy.arange(89.5, -90, -1)
        b = numpy.empty(a.shape+(2,))
        b[:,0] = a+0.5
        b[:,1] = a-0.5

        c = cf.Coordinate(data=cf.Data(a), bounds=cf.Data(b))

        for chunksize in chunk_sizes[::-1]:
            cf.CHUNKSIZE(chunksize)
            self.assertTrue(c.equals(c.transpose(), traceback=True))

        print "cf.Coordinate.transpose passed", "pmshape =", c.Data._pmshape
    #--- End: def

#--- End: class

if __name__ == '__main__':
    original_chunksize = cf.CHUNKSIZE()
    unittest.main()
    cf.CHUNKSIZE(original_chunksize)
