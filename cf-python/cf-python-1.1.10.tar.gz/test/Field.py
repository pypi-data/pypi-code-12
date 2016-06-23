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
    print 'cf.Field'
    print '----------------------------------------------------------'
    original_chunksize = cf.CHUNKSIZE()

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "test_file.nc")

    for chunksize in chunk_sizes[::-1]:

        cf.CHUNKSIZE(chunksize)

        f = cf.read(filename)[0]

        h = f.copy()
        h.transpose((1, 2, 0), i=True)
        h.transpose((2, 0, 1), i=True)
        h.transpose(('grid_longitude', 'atmos', 'grid_latitude'), i=True)
        h.transpose(('atmos', 'grid_latitude', 'grid_longitude'), i=True)
        assert(cf.equals(f, h, traceback=True))
        print "cf.Field.tranpose passed", "pmshape =", f.Data._pmshape
        
        h.flip((1, 0), i=True)
        h.flip((1, 0), i=True)
        h.flip(0, i=True)
        h.flip(1, i=True)
        h.flip([0, 1], i=True)
        assert(cf.equals(f, h, traceback=True))
        print "cf.Field.flip passed", "pmshape =", f.Data._pmshape
        

#        squeeze=True
#        
#        w = f.cm('area').copy()
#        w /= 10000.
#        w.transpose(i=True)
#        w = w.array
#        w = w.reshape(f.array.shape)
#        
#        w=None
#        x=None
#        
#        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
#                                "test_file.nc")
#        f = cf.read(filename, squeeze=squeeze)[0]
#                      
#        h = 'mean'
                        
        
        #for axis in [None] + range(f.ndim):
        #    b = numpy.average(f.array, axis=axis, weights=w)
        #    e = f.collapse('mean', axes=axis, weights=x)
        #    assert e.shape == b.shape, "%s, axis=%s, %s, %s" % (h, axis, e.shape, a.shape)
        #    assert e.allclose(b, rtol=1e-05, atol=1e-08) , "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % (h, axis, e.array, b, e.array-b)rt#
        #        #--- End: for
        
        
        
        # Match
        
        
        f = cf.read(filename)[0]
        f.long_name = 'qwerty'
#        print f
        all_kwargs = (
        {'inverse': False}, 
        {'inverse': False, 'match': 'eastward_wind'},
        {'inverse': False, 'match': {'long_name': 'qwerty'}},
        {'inverse': False, 'match': {None: 'east'}},
        {'inverse': False, 'match': 'east'},
        {'inverse': False, 'match': {None: 'east.*'}, 'regex': True},
        {'inverse': False, 'match': 'east.*', 'regex': True},
        {'inverse': False, 'match': cf.eq('east.*', regex=True)},
        {'inverse': False, 'match': {None: cf.eq('east.*', regex=True)}},
        {'inverse': False, 'match': {None: 'east', 'long_name': 'qwe'}},
        {'inverse': False, 'match': {None: 'east', 'long_name': 'qwe'}, 'match_all': False},
        {'inverse': False, 'match': {None: 'east', 'long_name': 'asd'}, 'match_all': False},
        #
        {'inverse': True, 'match': {None: 'east', 'long_name': 'asd'},},
        )
        for kwargs in all_kwargs:
#            print kwargs
            assert f.match(**kwargs), "f.match(**%s) failed" % kwargs
            kwargs['inverse'] = not kwargs['inverse']
            assert not f.match(**kwargs), "f.match(**%s) failed" % kwargs
        #--- End: for
        print "cf.Field.match passed", "pmshape =", f.Data._pmshape
        
#        axes_combinations = [axes
#                             for n in range(1, f.ndim+1)
#                             for axes in itertools.permutations(range(f.ndim), n)]
#
#        data_axes = f.data_axes()
#
#        d = f.data.copy()
#
#        for h in ('sum', 'min', 'max', 'mean', 'sd', 'var', 'mid_range', 'range'):
#            for axes in axes_combinations:
#                b = getattr(d, h)(axes=axes, squeeze=True)
#                axes2 = [data_axes[i] for i in axes]
#                e = f.collapse(h, axes=axes2).data
#                assert e.allclose(b, rtol=1e-05, atol=1e-08), \
#                    "%s, axis=%s, unweighted, unmasked \ne=%s, \nb=%s, \ne-b=%s" % \
#                    (h, axes, e.array, b, e.array-b)
#            #--- End: for
#            print "cf.Field.collapse '%s' unweighted, unmasked passed" % \
#                h, "pmshape =", f.Data._pmshape
#        #--- End: for

    #--- End: for

    # Reset chunk size
    cf.CHUNKSIZE(original_chunksize)

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All cf.Field tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------' 
    print
#--- End: def

if __name__ == "__main__":
    test()
