import cf
import numpy
import os
import time

def test(chunk_sizes=(17, 34, 60, 300, 100000)):
    start_time = time.time()

    print '----------------------------------------------------------'
    print 'cf.collapse'
    print '----------------------------------------------------------'
    # Save original chunksize
    original_chunksize = cf.CHUNKSIZE()

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "test_file.nc")

    for squeeze in (True, False):
        for missing_data in (True, False):
            for chunk in chunk_sizes:
            
                cf.CHUNKSIZE(chunk)
                
                f = cf.read(filename, squeeze=squeeze)[0]
                
                parameters = 'CHUNKSIZE=%s, missing_data=%s, squeeze=%s' % \
                    (cf.CHUNKSIZE(), missing_data, squeeze)            

                if missing_data:
                    for i in range(9):
                        f.subspace[..., [i, 9-i], i] = cf.masked
        
                print f
                print f.array                    
                print f.Data.dumpd()
                
                w = f.cm('area')
                w /= 10000.
                w = w.copy()
                w.transpose()
                w = w.array
                w = w.reshape(f.array.shape)
                if numpy.ma.is_masked(f.array):
                    w = numpy.ma.array(w, mask=f.array.mask)
                assert(w.shape == f.array.shape)
                print repr(f)
                print '--------------------------------------------------------------------'
                print 'Unweighted collapse, %s' % parameters
                print '--------------------------------------------------------------------'
                    
                method='mean'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights=None)
                    expected = numpy.ma.average(f.array, axis=axis)
                    assert numpy.ma.allclose(c.array.flatten(), expected), '%s %s %s\n%s\n%s' % (method, axes, axis, c.array, expected)
                    print "Unweighted %s over %s passed" % (method, repr(axes))
                        
                method='maximum'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights=None)
                    expected = numpy.ma.amax(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Unweighted %s over %s passed" % (method, repr(axes))
                        
                method='minimum'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights=None)
                    expected = numpy.ma.amin(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Unweighted %s over %s passed" % (method, repr(axes))
                  
                method='mid_range'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights=None)
                    expected = numpy.ma.ptp(f.array, axis=axis) / 2.0
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Unweighted %s over %s passed" % (method, repr(axes))
                
                method='sum'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights=None)
                    expected = numpy.ma.sum(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Unweighted %s over %s passed" % (method, repr(axes))
                
                method='variance'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights=None)
                    expected = numpy.ma.var(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Unweighted biased %s over %s passed" % (method, repr(axes))
                
                method='variance'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights=None, biased=False)
                    expected = numpy.ma.var(f.array, axis=axis, ddof=1)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Unweighted unbiased %s over %s passed" % (method, repr(axes))
                
                method='standard_deviation'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights=None)
                    expected = numpy.ma.std(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Unweighted biased %s over %s passed" % (method, repr(axes))
                
                method='standard_deviation'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights=None, biased=False)
                    expected = numpy.ma.std(f.array, axis=axis, ddof=1)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Unweighted unbiased %s over %s passed" % (method, repr(axes))
                
                print '--------------------------------------------------------------------'
                print 'Weighted collapse, %s' % parameters
                print '--------------------------------------------------------------------'
                    
                method='maximum'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY')
                    expected = numpy.ma.amax(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted %s over %s passed" % (method, repr(axes))
                        
                method='minimum'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY')
                    expected = numpy.ma.amin(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted %s over %s passed" % (method, repr(axes))
                  
                method='mid_range'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY')
                    expected = numpy.ma.ptp(f.array, axis=axis) / 2.0
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted %s over %s passed" % (method, repr(axes))
                
                method='sum'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY')
                    expected = numpy.ma.sum(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted %s over %s passed" % (method, repr(axes))
                
                method='mean'
                #for axes, axis in zip(('grid_latitude', 'grid_longitude',
                #                       ['grid_longitude', 'grid_latitude'], None),
                #                      (-2, -1, None, None)):
                #    print f
                #    print 'AXES=', axes
                #    print  f.Data._axes
                #    print 'f.shape=', f.shape
                #    print 'f.array=', f.array
                #    print 'w.shape=', w.shape
                #    print 'w=', w
                #    print f.cm().array
                #    c = cf.collapse(f, method, axes=axes, weights='XY')
                #    expected = numpy.ma.average(f.array, weights=w, axis=axis)
                #    print 'c.array=', c.array
                #    print 'n=', expected
                #    assert numpy.ma.allclose(c.array.flatten(), expected), 'weighted %s %s %s\n%s\n%s' % (method, axes, axis, c.array, expected)
                #    print "Weighted %s over %s passed" % (method, repr(axes))
        
#                method='mean'
#                for axes, axis, y in zip(('grid_latitude', 'grid_longitude',
#                                          ['grid_longitude', 'grid_latitude'], None),
#                                         (-2, -1, None, None),
#                                         ('grid_lat', 'grid_longitude',
#                                          ('grid_long', 'grid_latitude'),
#                                          ('X', 'grid_latitude'))):
#                    c = cf.collapse(f, method, axes=axes, weights=y)
#                    expected = numpy.ma.average(f.array, weights=w, axis=axis)
#                    assert numpy.ma.allclose(c.array.flatten(), expected), 'weighted %s %s %s\n%s\n%s' % (method, axes, axis, c.array, expected)
#                    print "Weighted %s over %s passed" % (method, repr(axes))
#        
#                method='variance'
#                for axes, axis in zip(('grid_latitude', 'grid_longitude',
#                                       ['grid_longitude', 'grid_latitude'], None),
#                                      (-2, -1, None, None)):
#                    c = cf.collapse(f, method, axes=axes, weights='XY') 
#                    mean, sw = numpy.ma.average(f.array, weights=w, returned=True, axis=axis)
#                    if axis is not None:
#                        mean = numpy.expand_dims(mean, axis)
#                    expected = numpy.ma.average((f.array-mean)**2, weights=w, axis=axis)
#                    assert(numpy.ma.allclose(c.array.flatten(), expected))
#                    print "Weighted %s over %s passed" % (method, repr(axes))
#        
#                method='variance'
#                for axes, axis in zip(('grid_latitude', 'grid_longitude',
#                                       ['grid_longitude', 'grid_latitude'], None),
#                                      (-2, -1, None, None)):
#                    c = cf.collapse(f, method, axes=axes, weights='XY', biased=False) 
#                    mean, sw = numpy.ma.average(f.array, weights=w, returned=True, axis=axis)
##                    print 'mean=', mean
##                    print 'sw=', sw
#                    if axis is not None:
#                        mean = numpy.expand_dims(mean, axis)
#                    variance = numpy.ma.average((f.array-mean)**2, weights=w, axis=axis)
#                    sw2      = numpy.ma.sum(w**2, axis=axis)
#                    expected = (sw**2/((sw**2)-sw2))*variance 
##                    print 'sw2=', sw2
##                    print 'variance=', variance
##                    print  c.array
##                    print expected
#                    assert(numpy.ma.allclose(c.array.flatten(), expected))
#                    print "Weighted unbiased %s over %s passed" % (method, repr(axes))
#        
#                method='standard_deviation'
#                for axes, axis in zip(('grid_latitude', 'grid_longitude',
#                                       ['grid_longitude', 'grid_latitude'], None),
#                                      (-2, -1, None, None)):
#                    c = cf.collapse(f, method, axes=axes, weights='XY') 
#                    mean, sw = numpy.ma.average(f.array, weights=w, returned=True, axis=axis)
#                    if axis is not None:
#                        mean = numpy.expand_dims(mean, axis)
#                    variance = numpy.ma.average((f.array-mean)**2, weights=w, axis=axis)
#                    expected = variance**0.5
#                    assert(numpy.ma.allclose(c.array.flatten(), expected))
#                    print "Weighted %s over %s passed" % (method, repr(axes))
#        
#                method='standard_deviation'
#                for axes, axis in zip(('grid_latitude', 'grid_longitude',
#                                       ['grid_longitude', 'grid_latitude'], None),
#                                      (-2, -1, None, None)):
#                    c = cf.collapse(f, method, axes=axes, weights='XY', biased=False) 
#                    mean, sw = numpy.ma.average(f.array, weights=w, returned=True, axis=axis)
#                    sw2      = numpy.ma.sum(w**2, axis=axis)
#                    if axis is not None:
#                        mean = numpy.expand_dims(mean, axis)
#                    variance = numpy.ma.average((f.array-mean)**2, weights=w, axis=axis)
#                    variance *= sw**2/(sw**2-sw2)
#                    expected = variance**0.5
#                    assert(numpy.ma.allclose(c.array.flatten(), expected))
#                    print "Weighted unbiased %s over %s passed" % (method, repr(axes))
        
                print '--------------------------------------------------------------------'
                print 'Weighted collapse, no cell measure, %s' % parameters
                print '--------------------------------------------------------------------'
        
                cm = f.remove_item('area')
        
                wlat = cf.tools.collapse.calc_weights(f.item('grid_latitude'),
                                                      infer_bounds=True).array
                wlon = cf.tools.collapse.calc_weights(f.item('grid_longitude'),
                                                      infer_bounds=True).array
        
                w0 = wlat.reshape(10, 1)
                w1 = wlon.reshape( 1, 9)
                w = w0*w1
                w = w.reshape(f.array.shape)
                assert(w.shape == f.array.shape)
              
                if numpy.ma.is_masked(f.array):
                    w = numpy.ma.array(w, mask=f.array.mask)
        
                method='maximum'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY')
                    expected = numpy.ma.amax(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, %s over %s passed" % (method, repr(axes))
                        
                method='minimum'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY')
                    expected = numpy.ma.amin(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, %s over %s passed" % (method, repr(axes))
                  
                method='mid_range'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY')
                    expected = numpy.ma.ptp(f.array, axis=axis) / 2.0
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, %s over %s passed" % (method, repr(axes))
                
                method='sum'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY')
                    expected = numpy.ma.sum(f.array, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, %s over %s passed" % (method, repr(axes))
                
                method='mean'
                for axes, axis, x in zip(('grid_latitude', 'grid_longitude',
                                          ['grid_longitude', 'grid_latitude'], None),
                                         (-2, -1, None, None),
                                         (wlat, wlon, w, w)):
                    c = cf.collapse(f, method, axes=axes, weights='XY')
                    expected = numpy.ma.average(f.array, weights=x, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, %s over %s passed" % (method, repr(axes))
        
                method='mean'
                for axes, axis, x, y in zip(('grid_latitude', 'grid_longitude',
                                             ['grid_longitude', 'grid_latitude'], None),
                                            (-2, -1, None, None),
                                            (wlat, wlon, w, w),
                                            ('Y', 'X', 'XY', 'YX')):
                    c = cf.collapse(f, method, axes=axes, weights=y)
                    expected = numpy.ma.average(f.array, weights=x, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, %s over %s passed" % (method, repr(axes))
        
                method='mean'
                for axes, axis, x, y in zip(('grid_latitude', 'grid_longitude',
                                             ['grid_longitude', 'grid_latitude'], None),
                                            (-2, -1, None, None),
                                            (wlat, wlon, w, w),
                                            ('grid_latitude', 'grid_longitude',
                                             ('grid_longitude', 'grid_latitude'),
                                             ('X', 'grid_latitude'))):
                    c = cf.collapse(f, method, axes=axes, weights=y)
                    expected = numpy.ma.average(f.array, weights=x, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, %s over %s passed" % (method, repr(axes))
        
                method='variance'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY') 
                    mean, sw = numpy.ma.average(f.array, weights=w, returned=True, axis=axis)
                    if axis is not None:
                        mean = numpy.expand_dims(mean, axis)
                    expected = numpy.ma.average((f.array-mean)**2, weights=w, axis=axis)
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, %s over %s passed" % (method, repr(axes))
        
                method='variance'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY', biased=False) 
                    mean, sw = numpy.ma.average(f.array, weights=w, returned=True, axis=axis)
#                    print 'mean=', mean
#                    print 'sw=', sw
                    if axis is not None:
                        mean = numpy.expand_dims(mean, axis)
                    variance = numpy.ma.average((f.array-mean)**2, weights=w, axis=axis)
                    sw2      = numpy.ma.sum(w**2, axis=axis)
                    expected = (sw**2/((sw**2)-sw2))*variance 
#                    print 'sw2=', sw2
#                    print 'variance=', variance
#                    print  c.array
#                    print expected
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, unbiased %s over %s passed" % (method, repr(axes))
        
                method='standard_deviation'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY') 
                    mean, sw = numpy.ma.average(f.array, weights=w, returned=True, axis=axis)
                    if axis is not None:
                        mean = numpy.expand_dims(mean, axis)
                    variance = numpy.ma.average((f.array-mean)**2, weights=w, axis=axis)
                    expected = variance**0.5
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, %s over %s passed" % (method, repr(axes))
        
                method='standard_deviation'
                for axes, axis in zip(('grid_latitude', 'grid_longitude',
                                       ['grid_longitude', 'grid_latitude'], None),
                                      (-2, -1, None, None)):
                    c = cf.collapse(f, method, axes=axes, weights='XY', biased=False) 
                    mean, sw = numpy.ma.average(f.array, weights=w, returned=True, axis=axis)
                    sw2      = numpy.ma.sum(w**2, axis=axis)
                    if axis is not None:
                        mean = numpy.expand_dims(mean, axis)
                    variance = numpy.ma.average((f.array-mean)**2, weights=w, axis=axis)
                    variance *= sw**2/(sw**2-sw2)
                    expected = variance**0.5
                    assert(numpy.ma.allclose(c.array.flatten(), expected))
                    print "Weighted, no cell measure, unbiased %s over %s passed" % (method, repr(axes))
        
                #axes=['grid_longitude', 'grid_latitude']
                #c = cf.collapse(f, 'mean', axes=axes, weights='XY')
                #
                #expected = numpy.ma.average(f.array, weights=w)
                #assert(numpy.ma.allclose(c.array.flatten(), expected))
                #print "Weighted mean over %s (no cell measure) passed" % repr(axes)
                #
                #cell_methods='grid_longitude: mean grid_latitude: max'
                #c = cf.collapse(f, cell_methods, weights='XY')
                #d = cf.collapse(f, 'mean', axes='grid_longitude', weights='XY')
                #expected = cf.collapse(d, 'max', axes='grid_latitude', weights='XY').array
                #assert(numpy.ma.allclose(c.array.flatten(), expected))
                #print "Weighted mean, max over %s (no cell measure) passed" % repr(cell_methods)
                #
                #f.domain.insert_cm(cm, axes=['dim1', 'dim0'])
                #
                #axes=['grid_longitude', 'grid_latitude']
                #c = cf.collapse(f, 'mean', axes=axes, weights='XY')
                #expected = numpy.ma.average(f.array, weights=w)
                #assert(numpy.ma.allclose(c.array.flatten(), expected))
                #print "Weighted mean over %s (with cell measure) passed" % repr(axes)
                #
                #axes=None
                #c = cf.collapse(f, 'variance', weights='XY')
                #mean, sw = numpy.ma.average(f.array, weights=w, returned=True)          
                #expected = numpy.ma.sum(w*(f.array-mean)**2)/sw #numpy.ma.sum(w)
                #assert(numpy.ma.allclose(c.array.flatten(), expected))
                #print "Weighted biased variance over %s passed" % repr(axes)
                #
                #axes=None
                #c = cf.collapse(f, 'variance', weights='XY', biased=False)
                #mean, sw = numpy.ma.average(f.array, weights=w, returned=True)
                #sw2 = numpy.sum(w**2)
                #expected = (sw/(sw**2-sw2))*numpy.sum(w*((f.array-mean)**2))
                #expected = (sw**2/(sw**2-sw2))*numpy.ma.average((f.array-mean)**2, weights=w)
                #assert(numpy.ma.allclose(c.array.flatten(), expected))
                #print "Weighted unbiased variance over %s passed" % repr(axes)
                #
                #print '--------------------------------------------------------------------'
                #print 'Cell measures weighted collapse'
                #print '--------------------------------------------------------------------'
                #
                #axes=['grid_longitude', 'grid_latitude']
                #c = cf.collapse(f, 'mean', axes=axes, weights='XY')
                #w = f.cm('area').copy()
                #w.transpose()
                #w = w.array
                #expected = numpy.ma.average(f.array, weights=w)
                #assert(numpy.ma.allclose(c.array.flatten(), expected))
                #print "Cell measures weighted mean over %s passed" % repr(axes)
                
                f.cell_methods = cf.CellMethods('grid_longitude: mean grid_latitude: maximum')
            #--- End: for
        #--- End: for
    #--- End: for
      
    # Reset chunk size
    cf.CHUNKSIZE(original_chunksize)

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All cf.collapse tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------' 
    print 
#--- End: def

if __name__ == "__main__":
    test()
