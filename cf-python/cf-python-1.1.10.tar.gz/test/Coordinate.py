import tempfile
import os
import sys
import itertools
from operator import mul
import numpy
import time
import cf

def test(chunk_sizes=(17, 34, 300, 100000)):

    start_time = time.time()
    print '----------------------------------------------------------'
    print 'cf.Coordinate'
    print '----------------------------------------------------------'
    original_chunksize = cf.CHUNKSIZE()

    for chunksize in chunk_sizes[::-1]:

        cf.CHUNKSIZE(chunksize)

        a = numpy.arange(89.5, -90, -1)
        b = numpy.empty(a.shape+(2,))
        b[:,0] = a+0.5
        b[:,1] = a-0.5

        c = cf.Coordinate(data=cf.Data(a), bounds=cf.Data(b))

        assert(c.equals(c.squeeze(), traceback=True))
        print "cf.Coordinate.squeeze passed", "pmshape =", c.Data._pmshape
    
        assert(c.equals(c.transpose(), traceback=True))
        print "cf.Coordinate.transpose passed", "pmshape =", c.Data._pmshape
    
        d1 = c.flip()
        d1.flip(i=True)
        assert(c.equals(d1, traceback=True))
        print "cf.Coordinate.flip passed", "pmshape =", c.Data._pmshape
    
        # ------------------------------------------------------------
        # cf.DimensionCoordinate.roll
        # ------------------------------------------------------------
        modulus = 10
        for a in (numpy.arange(modulus), numpy.arange(modulus)[::-1]):

            c = cf.DimensionCoordinate(data=cf.Data(a, 'km'))
            c.cyclic(cf.Data(1000*modulus, 'm'))
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
#                    print e, '\n', b, '\n'
                    assert (e == b).all(), '%s, shift=%s (%s), %s, %s' % (d.array, shift, shift%modulus, e, b)
                #--- End: for
            #--- End: for
        #--- End: for
        print "cf.DimensionCoordinate.roll passed", "pmshape =", pmshape

    #--- End: for

    # Reset chunk size
    cf.CHUNKSIZE(original_chunksize)

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All cf.Coordinate tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------' 
    print
#--- End: def

if __name__ == "__main__":
    test()
