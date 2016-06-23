import cf
import numpy
import os
import itertools
import time
from operator import mul

def test(chunk_sizes=(17, 34, 60, 300, 1000000)):
    start_time = time.time()
    print '----------------------------------------------------------'
    print 'cf.Data'
    print '----------------------------------------------------------'
    original_chunksize = cf.CHUNKSIZE()

    for chunksize in chunk_sizes[::-1]:

        cf.CHUNKSIZE(chunksize)

        # ----------------------------------------------------------------
        # cf.Data.all
        # cf.Data.any
        # ----------------------------------------------------------------
        d = cf.Data(numpy.array([[0] * 1000]))
        assert(not d.any())
        assert(not d.all())
        
        d[-1,-1] = 1
        assert(d.any())
        assert(not d.all())
        
        d[...] = 1
        assert(d.any())
        assert(d.all())

        d[...] = cf.masked
        assert(not d.any())
        assert(d.all())

        print 'cf.Data.all passed', "pmshape =", d._pmshape
        print 'cf.Data.any passed', "pmshape =", d._pmshape

        # --------------------------------------------------------------------
        # cf.Data.array
        # cf.Data.varray
        # --------------------------------------------------------------------
        d = cf.Data(numpy.arange(10*15*19).reshape(10, 1, 15, 19), 'km')
        a = d.array
        a[0,0,0,0] = -999
        assert(d.array[0,0,0,0] == 0)
        print "cf.Data.array passed", "pmshape =", d._pmshape

        e = d.copy()
        v = e.varray
        v[0,0,0,0] = -999
        assert(e.array[0,0,0,0] == -999)
        print "cf.Data.varray passed", "pmshape =", d._pmshape

        # ----------------------------------------------------------------
        # cf.Data.asdatetime
        # cf.Data.asreftime
        # ----------------------------------------------------------------
        d = cf.Data([[1.93, 5.17]], 'days since 2000-12-29')
        assert(d.dtype == numpy.dtype(float))
        assert(d._isdt == False)
        d.asreftime(i=True)
        assert(d.dtype == numpy.dtype(float))
        assert(d._isdt == False)
        d.asdatetime(i=True)
        assert(d.dtype == numpy.dtype(object))
        assert(d._isdt == True)
        d.asdatetime(i=True)
        assert(d.dtype == numpy.dtype(object))
        assert(d._isdt == True)
        d.asreftime(i=True)
        assert(d.dtype == numpy.dtype(float))
        assert(d._isdt == False)
        print "cf.Data.asdatetime passed", "pmshape =", d._pmshape
        print "cf.Data.asreftime passed", "pmshape =", d._pmshape
        
        

        # --------------------------------------------------------------------
        # cf.Data.datum
        # --------------------------------------------------------------------
        d = cf.Data(5, 'metre')
        assert (d.datum()   == 5), "d.datum()=%s"   % d.datum()
        assert (d.datum(0)  == 5), "d.datum(0)=%s"  % d.datum()
        assert (d.datum(-1) == 5), "d.datum(-1)=%s" % d.datum()
        
        for d in [cf.Data([4, 5, 6, 1, 2, 3], 'metre'),
                  cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')]:
            assert (d.datum(0)  == 4), "d.datum(0)=%s"  % d.datum()
            assert (d.datum(-1) == 3), "d.datum(-1)=%s" % d.datum()
            for index in d.ndindex():
                assert (d.datum(index)  == d.array[index].item()), \
                    "d.datum(%s)=%s" % (index, d.datum())
                assert (d.datum(*index) == d.array[index].item()), \
                    "d.datum(%s)=%s" % (index, d.datum())
        #--- End: for
        
        d = cf.Data(5, 'metre')
        d[()] = cf.masked
        assert (d.datum()   is cf.masked), "d.datum()=%s"   % d.datum()
        assert (d.datum(0)  is cf.masked), "d.datum(0)=%s"  % d.datum()
        assert (d.datum(-1) is cf.masked), "d.datum(-1)=%s" % d.datum()

        d = cf.Data([[5]], 'metre')
        d[0, 0] = cf.masked
        assert (d.datum()        is cf.masked), "d.datum()=%s" % d.datum()  
        assert (d.datum(0)       is cf.masked), "d.datum(0)=%s" % d.datum() 
        assert (d.datum(-1)      is cf.masked), "d.datum(-1)=%s" % d.datum()
        assert (d.datum(0, 0)    is cf.masked), "d.datum(0, 0)=%s" % d.datum()  
        assert (d.datum(-1, 0)   is cf.masked), "d.datum(-1, 0)=%s" % d.datum() 
        assert (d.datum([0, 0])  is cf.masked), "d.datum([0, 0])=%s" % d.datum()
        assert (d.datum([0, -1]) is cf.masked), "d.datum([0, -1])=%s" % d.datum()
        assert (d.datum(-1, -1)  is cf.masked), "d.datum(-1, -1)=%s" % d.datum()

        print "cf.Data.datum passed", "pmshape =", d._pmshape

        # --------------------------------------------------------------------
        # cf.Data.flip
        # --------------------------------------------------------------------
        array = numpy.arange(24000).reshape(120, 200)
        d = cf.Data(array.copy(), 'metre')
        
        for axes, indices in zip((0, 1, [0, 1]),
                                 ((slice(None, None, -1), slice(None)),
                                  (slice(None)          , slice(None, None, -1)),
                                  (slice(None, None, -1), slice(None, None, -1)))
                                ):
            array = array[indices]
            d.flip(axes, i=True)
        #--- End: for
        assert(d.array == array).all(), "cf.Data.flip failed"

        print "cf.Data.flip passed", "pmshape =", d._pmshape

        # ----------------------------------------------------------------
        # cf.Data.sample_size
        # ----------------------------------------------------------------
        d = cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')
        assert(d.sample_size() == 6)
        d[1, 0] = cf.masked
        assert(d.sample_size() == cf.Data(50, '0.1'))
        print "cf.Data.sample_size passed", "pmshape =", d._pmshape
        
        # ----------------------------------------------------------------
        # cf.Data.min
        # ----------------------------------------------------------------
        d = cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')
        assert(d.min() == cf.Data(1, 'metre'))
        assert(d.min().datum() == 1)
        d[1, 0] = cf.masked
        assert(d.min() == 2)
        assert(d.min().datum() == 2)
        assert(d.min() == cf.Data(0.002, 'km'))
        print "cf.Data.min passed", "pmshape =", d._pmshape
        
        # ----------------------------------------------------------------
        # cf.Data.max
        # ----------------------------------------------------------------
        d = cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')
        assert(d.max() == cf.Data(6, 'metre'))
        assert(d.max().datum() == 6)
        d[0, 2] = cf.masked
        assert(d.max() == 5)
        assert(d.max().datum() == 5)
        assert(d.max() == cf.Data(0.005, 'km'))
        print "cf.Data.max passed", "pmshape =", d._pmshape
       
        # --------------------------------------------------------------------
        # cf.Data.ndindex
        # --------------------------------------------------------------------
        for d in (cf.Data(5, 'metre'),
                  cf.Data([4, 5, 6, 1, 2, 3], 'metre'),
                  cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')
                  ):
            for i, j in zip(d.ndindex(), numpy.ndindex(d.shape)):
                assert(i == j)
        #--- End: for
        print "cf.Data.ndindex passed", "pmshape =", d._pmshape
        
        # ----------------------------------------------------------------
        # cf.Data.roll
        # ----------------------------------------------------------------
        a = numpy.arange(10*15*19).reshape(10, 1, 15, 19)
        d = cf.Data(a)

        pmshape = d._pmshape

        e = d.roll(0,  4)
        e.roll(2, 120, i=True)
        e.roll(3, -77, i=True)

        a = numpy.roll(a,   4, 0)
        a = numpy.roll(a, 120, 2)
        a = numpy.roll(a, -77, 3)

        assert e.shape == a.shape
        assert (a == e.array).all()

        f = e.roll(3,   77)
        f.roll(2, -120, i=True)
        f.roll(0,   -4, i=True)

        assert f.shape == d.shape
        assert f.equals(d)

        print "cf.Data.roll passed", "pmshape =", pmshape

        # ----------------------------------------------------------------
        # cf.Data.swapaxes
        # ----------------------------------------------------------------
        a = numpy.arange(10*15*19).reshape(10, 1, 15, 19)
        d = cf.Data(a.copy())

        for i in range(-a.ndim, a.ndim):
            for j in range(-a.ndim, a.ndim):
                b = numpy.swapaxes(a.copy(), i, j)
                e = d.swapaxes(i, j)
                message = "cf.Data.swapaxes(%d, %d) failed" % (i, j)
                assert (b.shape == e.shape), message
                assert ((b == e.array).all()), message
            #--- End: for
        #--- End: for
        print "cf.Data.swapaxes passed", "pmshape =", d._pmshape
                
        # ----------------------------------------------------------------
        # cf.Data.transpose
        # ----------------------------------------------------------------
        a = numpy.arange(10*15*19).reshape(10, 1, 15, 19)
        d = cf.Data(a.copy())

        for indices in (range(a.ndim), range(-a.ndim, 0)):
            for axes in itertools.permutations(indices):
                a = numpy.transpose(a, axes)
                d.transpose(axes, i=True)
                message = 'cf.Data.transpose(%s) failed: d.shape=%s, a.shape=%s' % \
                    (axes, d.shape, a.shape)
                assert d.shape == a.shape, message
                assert (d.array == a).all(), message
            #--- End: for
        #--- End: for

        print "cf.Data.transpose passed", "pmshape =", d._pmshape
        
        # ----------------------------------------------------------------
        # cf.Data.unique
        # ----------------------------------------------------------------
        d = cf.Data([[4, 2, 1], [1, 2, 3]], 'metre')
        assert((d.unique == cf.Data([1, 2, 3, 4], 'metre')).all())
        d[1, -1] = cf.masked
        assert((d.unique == cf.Data([1, 2, 4], 'metre')).all())
        print "cf.Data.unique passed", "pmshape =", d._pmshape
        
        # ----------------------------------------------------------------
        # Broadcasting
        # ----------------------------------------------------------------
        A = [numpy.array(3),
             numpy.array( [3]),
             numpy.array( [3]).reshape(1, 1),
             numpy.array( [3]).reshape(1, 1, 1),
             numpy.arange(  5).reshape(5, 1),
             numpy.arange(  5).reshape(1, 5),
             numpy.arange(  5).reshape(1, 5, 1),
             numpy.arange(  5).reshape(5, 1, 1),
             numpy.arange(  5).reshape(1, 1, 5),
             numpy.arange( 25).reshape(1, 5, 5),
             numpy.arange( 25).reshape(5, 1, 5),
             numpy.arange( 25).reshape(5, 5, 1),
             numpy.arange(125).reshape(5, 5, 5),
             ]
        
        for a in A:
            for b in A:
                d = cf.Data(a)
                e = cf.Data(b)
                ab = a*b
                de = d*e

                message = 'cf.Data broadcasting failed: de.shape='+repr(de.shape)+ \
                    ',ab.shape='+repr(ab.shape)
                assert de.shape == ab.shape, message
                assert (de.array == ab).all(), message
            #--- End: for
        #--- End: for
        print "cf.Data broadcasting passed"
        
        # ----------------------------------------------------------------
        # __contains__
        # ----------------------------------------------------------------
        d = cf.Data([[0.0, 1,  2], [3, 4, 5]], units='m')
        x = 4 in d
        assert(x)
        x = 40 in d
        assert(not x)
        x = cf.Data(3) in d
        assert(x)
        x = cf.Data([[[[3]]]]) in d
        assert(x)
        value = d[1, 2]
        value.Units *= 2
        value.squeeze(0)
        x = value in d
        assert(x)
        x = numpy.array([[[2]]]) in d
        assert(x)
        print "cf.Data.__contains__ passed", "pmshape =", d._pmshape
        
        # ----------------------------------------------------------------
        # cf.Data.year
        # cf.Data.month
        # cf.Data.day
        # cf.Data.hour
        # cf.Data.minute
        # cf.Data.second
        # ----------------------------------------------------------------
        d = cf.Data([[1.93, 5.17]], 'days since 2000-12-29')
        assert(d.year.equals(cf.Data([[2000, 2001]])))
        assert(d.month.equals(cf.Data([[12, 1]])))
        assert(d.day.equals(cf.Data([[30, 3]])))
        assert(d.hour.equals(cf.Data([[22, 4]])))
        assert(d.minute.equals(cf.Data([[19, 4]])))
        assert(d.second.equals(cf.Data([[12, 48]])))
        
        d = cf.Data([[1.93, 5.17]], cf.Units('days since 2000-12-29', '360_day'))
        assert(d.year.equals(cf.Data([[2000, 2001]])))
        assert(d.month.equals(cf.Data([[12, 1]])))
        assert(d.day.equals(cf.Data([[30, 4]])))
        assert(d.hour.equals(cf.Data([[22, 4]])))
        assert(d.minute.equals(cf.Data([[19, 4]])))
        assert(d.second.equals(cf.Data([[12, 48]])))
        
        print 'cf.Data.year passed'  , "pmshape =", d._pmshape
        print 'cf.Data.month passed' , "pmshape =", d._pmshape
        print 'cf.Data.day passed'   , "pmshape =", d._pmshape
        print 'cf.Data.hour passed'  , "pmshape =", d._pmshape
        print 'cf.Data.minute passed', "pmshape =", d._pmshape
        print 'cf.Data.second passed', "pmshape =", d._pmshape
        
        # ----------------------------------------------------------------
        # Binary and unary operators
        # ----------------------------------------------------------------
        array=numpy.arange(3*4*5).reshape(3, 4, 5) + 1
      
        arrays =  (numpy.arange(3*4*5).reshape(3, 4, 5) + 1.0,
                   numpy.arange(3*4*5).reshape(3, 4, 5) + 1)

        for a0 in arrays:
            for a1 in arrays[::-1]:
                d = cf.Data(a0[(slice(None, None, -1),)*a0.ndim], 'metre')
                d.flip(i=True)
                x = cf.Data(a1, 'metre')

                assert((d +  x).equals(cf.Data(a0 +  a1, 'm' ), traceback=1)), '%s+%s'  % (repr(d), x)
                assert((d *  x).equals(cf.Data(a0 *  a1, 'm2'), traceback=1)), '%s*%s'  % (repr(d), x)
                assert((d /  x).equals(cf.Data(a0 /  a1, '1' ), traceback=1)), '%s/%s'  % (repr(d), x)
                assert((d -  x).equals(cf.Data(a0 -  a1, 'm' ), traceback=1)), '%s-%s'  % (repr(d), x)
                assert((d // x).equals(cf.Data(a0 // a1, '1' ), traceback=1)), '%s//%s' % (repr(d), x)
            
                assert(d.__truediv__(x).equals(cf.Data(array.__truediv__(array), '1'), traceback=1)), '%s.__truediv__(%s)' % (d, x)
                assert(d.__rtruediv__(x).equals(cf.Data(array.__rtruediv__(array), '1'), traceback=1)) , '%s.__rtruediv__(%s)' % (d, x)
                
                try:
                    d ** x
                except:
                    pass
                else:
                    assert (d**x).all(), '%s**%s' % (d, repr(x))

                print '%s {+, -, *, /, //, **, __truediv__, __rtruediv__} %s passed' % (d, x), "pmshape =", d._pmshape        
            #--- End: for                       
        #--- End: for                       
                
        for a0 in arrays:
            d = cf.Data(a0, 'metre')

            for x in (2, 2.0):
                assert((d +  x).equals(cf.Data(a0 +  x, 'm' ), traceback=1)), '%s+%s'  % (repr(d), x)
                assert((d *  x).equals(cf.Data(a0 *  x, 'm' ), traceback=1)), '%s*%s'  % (repr(d), x)
                assert((d /  x).equals(cf.Data(a0 /  x, 'm' ), traceback=1)), '%s/%s'  % (repr(d), x)
                assert((d -  x).equals(cf.Data(a0 -  x, 'm' ), traceback=1)), '%s-%s'  % (repr(d), x)
                assert((d // x).equals(cf.Data(a0 // x, 'm' ), traceback=1)), '%s//%s' % (repr(d), x)
                assert((d ** x).equals(cf.Data(a0 ** x, 'm2'), traceback=1)), '%s**%s' % (repr(d), x)

                assert(d.__truediv__(x).equals(cf.Data(a0.__truediv__(x), 'm'), traceback=1)), '%s.__truediv__(%s)' % (d, x)
                assert(d.__rtruediv__(x).equals(cf.Data(a0.__rtruediv__(x), 'm-1'), traceback=1)) , '%s.__rtruediv__(%s)' % (d, x)
      
                print '%s {+, -, *, /, //, **, __truediv__, __rtruediv__} %s passed' % (d, x), "pmshape =", d._pmshape                               
                
                assert((x +  d).equals(cf.Data(x +  a0, 'm'  ), traceback=1)), '%s+%s'  % (x, repr(d))
                assert((x *  d).equals(cf.Data(x *  a0, 'm'  ), traceback=1)), '%s*%s'  % (x, repr(d))
                assert((x /  d).equals(cf.Data(x /  a0, 'm-1'), traceback=1)), '%s/%s'  % (x, repr(d))
                assert((x -  d).equals(cf.Data(x -  a0, 'm'  ), traceback=1)), '%s-%s'  % (x, repr(d))
                assert((x // d).equals(cf.Data(x // a0, 'm-1'), traceback=1)), '%s//%s' % (x, repr(d))

                try:
                    x ** d
                except:
                    pass
                else:
                    assert (x**d).all(), '%s**%s' % (x, repr(d))

                print '%s {+, -, *, /, //, **} %s passed' % (x, repr(d)), "pmshape =", d._pmshape
            
                e = d.copy()
                a = a0.copy()
                e += x
                a += x
                assert(e.equals(cf.Data(a, 'm'), traceback=1)), '%s+=%s' % (repr(d), x)
                e = d.copy()
                a = a0.copy()
                e *= x
                a *= x
                assert(e.equals(cf.Data(a, 'm'), traceback=1)), '%s*=%s' % (repr(d), x)
                e = d.copy()
                a = a0.copy()
                e /= x
                a /= x
                assert(e.equals(cf.Data(a, 'm'), traceback=1)), '%s/=%s' % (repr(d), x)
                e = d.copy()
                a = a0.copy()
                e -= x
                a -= x
                assert(e.equals(cf.Data(a, 'm'), traceback=1)), '%s-=%s' % (repr(d), x)
                e = d.copy()
                a = a0.copy()
                e //= x
                a //= x
                assert(e.equals(cf.Data(a, 'm'), traceback=1)), '%s//=%s' % (repr(d), x)
                e = d.copy()
                a = a0.copy()
                e **= x
                a **= x
                assert(e.equals(cf.Data(a, 'm2'), traceback=1)), '%s**=%s' % (repr(d), x)
                e = d.copy()
                a = a0.copy()
                e.__itruediv__(x)
                a.__itruediv__(x)
                assert(e.equals(cf.Data(a, 'm'), traceback=1)), '%s.__itruediv__(%s)' % (d, x)
            
                print '%s {+=, -=, *=, /=, //=, **=, __itruediv__} %s passed' % (repr(d), x), "pmshape =", d._pmshape
            #--- End: for
            
            for x in (cf.Data(2, 'metre'), cf.Data(2.0, 'metre')):
                assert((d +  x).equals(cf.Data(a0 +  x.datum(), 'm' ), traceback=1))
                assert((d *  x).equals(cf.Data(a0 *  x.datum(), 'm2'), traceback=1))
                assert((d /  x).equals(cf.Data(a0 /  x.datum(), '1' ), traceback=1))
                assert((d -  x).equals(cf.Data(a0 -  x.datum(), 'm' ), traceback=1))
                assert((d // x).equals(cf.Data(a0 // x.datum(), '1' ), traceback=1))

                try:
                   d ** x
                except:
                    pass
                else:
                    assert (x**d).all(), '%s**%s' % (x, repr(d))

                assert(d.__truediv__(x).equals(cf.Data(a0.__truediv__(x.datum()), ''), traceback=1))
            
                print '%s {+, -, *, /, //, **, __truediv__} %s passed' % \
                    (repr(d), repr(x)), "pmshape =", d._pmshape
            #--- End: for
        #--- End: for
        
        # ----------------------------------------------------------------
        # cf.Data.__setitem__
        # ----------------------------------------------------------------
        for hardmask in (False, True):
            a = numpy.ma.arange(3000).reshape(50, 60)
            if hardmask:
                a.harden_mask()
            else:
                a.soften_mask()
                
            d = cf.Data(a.filled(), 'm')
            d.hardmask = hardmask

            for n, (j, i) in enumerate(((34, 23), (0, 0), (-1, -1),
                                        (slice(40, 50), slice(58, 60)),
                                        (Ellipsis, Ellipsis),
                                        )):
                n = -n-1
                for dvalue, avalue in ((n, n), (cf.masked, numpy.ma.masked), (n, n)):
                    message = "cf.Data[%s, %s]=%s failed" % (j, i, dvalue)
                    d[j, i] = dvalue
                    a[j, i] = avalue
                    assert (d.array == a).all() in (True, numpy.ma.masked), message
                    assert (d.mask.array == numpy.ma.getmaskarray(a)).all(), message
            #--- End: for

            a = numpy.ma.arange(3000).reshape(50, 60)
            if hardmask:
                a.harden_mask()
            else:
                a.soften_mask()

            d = cf.Data(a.filled(), 'm')
            d.hardmask = hardmask

            (j, i) = (slice(0, 2), slice(0, 3))
            array = numpy.array([[1, 2, 6],[3, 4, 5]])*-1
            for dvalue in (array,
                           numpy.ma.masked_where(array < -2, array),
                           array):
                message = "cf.Data[%s, %s]=%s failed" % (j, i, dvalue)
                d[j, i] = dvalue
                a[j, i] = dvalue
                assert (d.array == a).all() in (True, numpy.ma.masked), message
                assert (d.mask.array == numpy.ma.getmaskarray(a)).all(), message
            #--- End: for

            print 'cf.Data.__setitem__ passed: hardmask =',hardmask,', pmshape =', d._pmshape
        #--- End: for

        # ----------------------------------------------------------------
        # cf.Data._collapse SHAPE
        # ----------------------------------------------------------------
        a = numpy.arange(-100, 200., dtype=float).reshape(3, 4, 5, 5)
        ones = numpy.ones(a.shape, dtype=float)

        w = numpy.arange(1, 301., dtype=float).reshape(a.shape)
        w[-1, -1, ...] = w[-1, -1, ...]*2
        w /= w.min()
 
        d = cf.Data(a[(slice(None, None, -1),) * a.ndim].copy())
        d.flip(i=True)
        x = cf.Data(w.copy())

        axes_combinations = [axes
                             for n in range(1, a.ndim+1)
                             for axes in itertools.permutations(range(a.ndim), n)]

        shape = list(d.shape)
 
        def reshape_a(a, axes):
            new_order = [i for i in range(a.ndim) if i not in axes]
            new_order.extend(axes)
            b = numpy.transpose(a, new_order)
            new_shape = b.shape[:b.ndim-len(axes)]
            new_shape += (reduce(mul, b.shape[b.ndim-len(axes):]),)
            b = b.reshape(new_shape)
            return b
        #--- End: def

        for h in ('sample_size', 'sum', 'min', 'max', 'mean', 'var', 'sd',
                  'mid_range', 'range'):
            for axes in axes_combinations:
                e = getattr(d, h)(axes=axes, squeeze=False)
                
                shape = list(d.shape)
                for i in axes:                        
                    shape[i] = 1
                    
                shape = tuple(shape)
                assert e.shape == shape, \
                    "%s, axes=%s, not squeezed bad shape: %s != %s" % \
                    (h, axis, e.shape, shape)
            #--- End: for

            for axes in axes_combinations:
                e = getattr(d, h)(axes=axes, squeeze=True)
                shape = list(d.shape)
                for i in sorted(axes, reverse=True):                        
                    shape.pop(i)

                shape = tuple(shape)
                assert e.shape == shape, \
                    "%s, axes=%s, squeezed bad shape: %s != %s" % \
                    (h, axis, e.shape, shape)
            #--- End: for

            e = getattr(d, h)(squeeze=True)
            shape = ()
            assert e.shape == shape, \
                "%s, axes=%s, squeezed bad shape: %s != %s" % \
                (h, None, e.shape, shape)

            e = getattr(d, h)(squeeze=False)
            shape = (1,) * d.ndim
            assert e.shape == shape, \
                "%s, axes=%s, not squeezed bad shape: %s != %s" % \
                (h, None, e.shape, shape)

            print 'cf.Data.%s shape passed' % h, "pmshape =", d._pmshape
        #--- End: for

        # ---------------------------------------------------------------- 
        # cf.Data._collapse UNWEIGHTED UNMASKED
        # ----------------------------------------------------------------
        for h in ('sample_size', 'sum_of_weights', 'sum_of_weights2'):
            for axes in axes_combinations:
                b = reshape_a(ones, axes)
                b = b.sum(axis=-1)
                e = getattr(d, h)(axes=axes, squeeze=True)
                
                assert e.allclose(b, rtol=1e-05, atol=1e-08) , \
                    "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                    (h, axes, e.array, b, e.array-b)
            #--- End: for
            print 'cf.Data.%s unweighted, unmasked passed' % \
                h, "pmshape =", d._pmshape
        #--- End: for

        for np, h in zip((numpy.sum, numpy.amin, numpy.amax, numpy.mean),
                         (     'sum',     'min',     'max', 'mean')):
            for axes in axes_combinations:
                b = reshape_a(a, axes)
                b = np(b, axis=-1)                
                e = getattr(d, h)(axes=axes, squeeze=True)
                assert e.allclose(b, rtol=1e-05, atol=1e-08), \
                    "%s, axis=%s, unweighted, unmasked \ne=%s, \nb=%s, \ne-b=%s" % \
                    (h, axes, e.array, b, e.array-b)
            #--- End: for
            print 'cf.Data.%s unweighted, unmasked passed' % \
                h, "pmshape =", d._pmshape
        #--- End: for

        ddofs=(0, 1, 2)
        for np, h in zip((numpy.var, numpy.std),
                         ('var'    , 'sd')):
            for ddof in ddofs:
                for axes in axes_combinations:
                    b = reshape_a(a, axes)
                    b = np(b, axis=-1, ddof=ddof)                
                    e = getattr(d, h)(axes=axes, squeeze=True, ddof=ddof)
                    assert e.allclose(b, rtol=1e-05, atol=1e-08), \
                        "%s, axis=%s, unweighted, unmasked \ne=%s, \nb=%s, \ne-b=%s" % \
                        (h, axes, e.array, b, e.array-b)
                #--- End: for
            #--- End: for
            print 'cf.Data.%s unweighted, unmasked passed' % h, \
                "pmshape =", d._pmshape
        #--- End: for

        # ----------------------------------------------------------------
        # cf.Data._collapse WEIGHTED UNMASKED
        # ----------------------------------------------------------------
        for c, h in zip((w               , w*w), 
                        ('sum_of_weights', 'sum_of_weights2')):
            for axes in axes_combinations:
                b = reshape_a(c, axes)
                b = b.sum(axis=-1)                
                e = getattr(d, h)(axes=axes, weights=x, squeeze=True)
                assert e.allclose(b, rtol=1e-05, atol=1e-08) , \
                    "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                    (h, axes, e.array, b, e.array-b)
            #--- End: for
            print 'cf.Data.%s weighted, unmasked passed' % h, \
                "pmshape =", d._pmshape
        #--- End: for

        h = 'mean'
        for axes in axes_combinations:
            b = reshape_a(a, axes)
            v = reshape_a(w, axes)
            b = numpy.average(b, axis=-1, weights=v)
            e = getattr(d, h)(axes=axes, weights=x, squeeze=True)
            assert e.allclose(b, rtol=1e-05, atol=1e-08) , \
                "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                (h, axes, e.array, b, e.array-b)
        #--- End: for
        print 'cf.Data.%s weighted, unmasked passed' % h, \
            "pmshape =", d._pmshape
        
        ddofs = (0, 1, 2)
        f= 2
        for h in ('var', 'sd'):
            for axes in axes_combinations:                
                for ddof in ddofs:
                    b = reshape_a(a, axes)
                    v = reshape_a(w, axes)
                    
                    avg = numpy.average(b, axis=-1, weights=v)
                    if numpy.ndim(avg) < b.ndim:
                        avg = numpy.expand_dims(avg, -1)
    
                    b, sv = numpy.average((b-avg)**2, axis=-1, weights=v,
                                          returned=True)
                    b *= f*sv/(f*sv-ddof)
                    
                    if h == 'sd':
                        b **= 0.5

                    e = getattr(d, h)(axes=axes, weights=x, squeeze=True,
                                      ddof=ddof, a=f)

                    assert e.allclose(b, rtol=1e-05, atol=1e-08) , \
                        "%s, axis=%s, ddof=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                        (h, axes, ddof, e.array, b, e.array-b)
                #--- End: for
            #--- End: for
            print 'cf.Data.%s weighted, unmasked passed' % h, \
                "pmshape =", d._pmshape
        #--- End: for

        # ----------------------------------------------------------------
        # cf.Data._collapse UNWEIGHTED MASKED
        # ----------------------------------------------------------------
        a = numpy.ma.arange(-100, 200., dtype=float).reshape(3, 4, 5, 5)
        a[0, :, 2, 3] = numpy.ma.masked
        a[1, 2, 3, :] = numpy.ma.masked
        a[0, 3, :, 3] = numpy.ma.masked
        a[:, 1, 4, 4] = numpy.ma.masked
        
        ones = numpy.ma.array(ones)

        d = cf.Data(a.copy())

        for c, h in zip((ones            , ones), 
                        ('sum_of_weights', 'sum_of_weights2')):
            for axes in axes_combinations:
                c = c.copy()
                c.mask = a.mask
                b = reshape_a(c, axes)
                b = numpy.ma.asanyarray(b.sum(axis=-1))
                e = getattr(d, h)(axes=axes, squeeze=True)  

                assert (e.mask.array == b.mask).all(), \
                    "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" % \
                    (h, axes, e.mask.array, b.mask, e.mask.array==b.mask)
                assert e.allclose(b, rtol=1e-05, atol=1e-08) , \
                    "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                    (h, axes, e.array, b, e.array-b)
            #--- End: for
            print 'cf.Data.%s unweighted, masked passed' % h, \
                "pmshape =", d._pmshape
        #--- End: for

        for np, h in zip((numpy.ma.sum, numpy.ma.amin, numpy.ma.amax),
                         (     'sum',     'min',     'max')):
            for axes in axes_combinations:
                b = reshape_a(a, axes)
                b = np(b, axis=-1)                
                b = numpy.ma.asanyarray(b)
                e = getattr(d, h)(axes=axes, squeeze=True)

                assert (e.mask.array == b.mask).all(), \
                    "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" % \
                    (h, axes, e.mask.array, b.mask, e.mask.array==b.mask)
                assert e.allclose(b, rtol=1e-05, atol=1e-08), \
                    "%s, axis=%s, unweighted, unmasked \ne=%s, \nb=%s, \ne-b=%s" % \
                    (h, axes, e.array, b, e.array-b)
            #--- End: for
            print 'cf.Data.%s unweighted, masked passed' % \
                h, "pmshape =", d._pmshape
        #--- End: for
            
        h = 'mean'
        for axes in axes_combinations:
            b = reshape_a(a, axes)
            b = numpy.ma.average(b, axis=-1)
            b = numpy.ma.asanyarray(b)

            e = getattr(d, h)(axes=axes, squeeze=True)

            assert (e.mask.array == b.mask).all(), \
                "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" % \
                (h, axes, e.mask.array, b.mask, e.mask.array==b.mask)
            assert e.allclose(b, rtol=1e-05, atol=1e-08), \
                "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                (h, axes, e.array, b, e.array-b)
        #--- End: for
        print 'cf.Data.%s unweighted, masked passed' % h, \
            "pmshape =", d._pmshape
 
        ddofs = (0, 1, 2)
        f = 2
        for h in ('var', 'sd'):
            for axes in axes_combinations:                
                for ddof in ddofs:
                    e = getattr(d, h)(axes=axes, squeeze=True, ddof=ddof)

                    b = reshape_a(a, axes)

                    not_enough_data = numpy.ma.count(b, axis=-1) <= ddof

                    avg = numpy.ma.average(b, axis=-1)

                    if numpy.ndim(avg) < b.ndim:
                        avg = numpy.ma.expand_dims(avg, -1)

                    b, sv = numpy.ma.average((b-avg)**2, axis=-1, returned=True)

                    b = numpy.ma.where(not_enough_data, numpy.ma.masked, b)

                    b *= sv/(sv-ddof)
                    if h == 'sd':
                        b **= 0.5
                    b = numpy.ma.asanyarray(b)

                    e = getattr(d, h)(axes=axes, squeeze=True, ddof=ddof)
                    
                    assert (e.mask.array == b.mask).all(), \
                        "%s, axis=%s, ddof=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" % \
                        (h, axes, e.mask.array, b.mask, e.mask.array==b.mask)
                    assert e.allclose(b, rtol=1e-05, atol=1e-08) , \
                        "%s, axis=%s, ddof=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                        (h, axes, ddof, e.array, b, e.array-b)
                 #--- End: for
            #--- End: for
            print 'cf.Data.%s unweighted, masked passed' % h, \
                "pmshape =", d._pmshape
        #--- End: for


        # ----------------------------------------------------------------
        # cf.Data._collapse WEIGHTED MASKED
        # ----------------------------------------------------------------
        w = numpy.ma.array(w)

        for c, h in zip((w               , w*w), 
                        ('sum_of_weights', 'sum_of_weights2')):
            for axes in axes_combinations:
                c = c.copy()
                c.mask = a.mask
                b = reshape_a(c, axes)
                b = numpy.ma.asanyarray(b.sum(axis=-1))
                e = getattr(d, h)(axes=axes, weights=x, squeeze=True)  
                assert (e.mask.array == b.mask).all(), \
                    "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" % \
                    (h, axes, e.mask.array, b.mask, e.mask.array==b.mask)
                assert e.allclose(b, rtol=1e-05, atol=1e-08) , \
                    "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                    (h, axes, e.array, b, e.array-b)
            #--- End: for
            print 'cf.Data.%s weighted, masked passed' % h, \
                "pmshape =", d._pmshape
        #--- End: for

        h = 'mean'
        for axes in axes_combinations:
            b = reshape_a(a, axes)
            v = reshape_a(w, axes)
            b = numpy.ma.average(b, axis=-1, weights=v)
            b = numpy.ma.asanyarray(b)

            e = getattr(d, h)(axes=axes, weights=x, squeeze=True)

            assert (e.mask.array == b.mask).all(), \
                "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" % \
                (h, axes, e.mask.array, b.mask, e.mask.array==b.mask)
            assert e.allclose(b, rtol=1e-05, atol=1e-08), \
                "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                (h, axes, e.array, b, e.array-b)
        #--- End: for
        print 'cf.Data.%s weighted, masked passed' % h, "pmshape =", d._pmshape
 
        ddofs = (0, 1, 2)
        f = 2
        for h in ('var', 'sd'):
            for axes in axes_combinations:                
                for ddof in ddofs:
                    b = reshape_a(a, axes)
                    v = reshape_a(w, axes)

                    not_enough_data = numpy.ma.count(b, axis=-1) <= ddof

                    avg = numpy.ma.average(b, axis=-1, weights=v)
                    if numpy.ndim(avg) < b.ndim:
                        avg = numpy.ma.expand_dims(avg, -1)

                    b, sv = numpy.ma.average((b-avg)**2, axis=-1, weights=v,
                                             returned=True)

                    b = numpy.ma.where(not_enough_data, numpy.ma.masked, b)

                    b *= f*sv/(f*sv-ddof)
                    if h == 'sd':
                        b **= 0.5
                    b = numpy.ma.asanyarray(b)

                    e = getattr(d, h)(axes=axes, weights=x, squeeze=True,
                                      ddof=ddof, a=f)

                    assert (e.mask.array == b.mask).all(), \
                        "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" % \
                        (h, axes, e.mask.array, b.mask, e.mask.array==b.mask)
                    assert e.allclose(b, rtol=1e-05, atol=1e-08) , \
                        "%s, axis=%s, ddof=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                        (h, axes, ddof, e.array, b, e.array-b)
                 #--- End: for
            #--- End: for
            print 'cf.Data.%s weighted, masked passed' % h, \
                "pmshape =", d._pmshape
        #--- End: for

        print ''
        print 'cf.Data with chunk size %d passed' % chunksize
        print ''
    #--- End: for

    cf.CHUNKSIZE(original_chunksize)

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All cf.Data tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------'  
    print
#--- End: def

if __name__ == "__main__":
    test()
