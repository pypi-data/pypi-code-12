import cf
import numpy
import os
import itertools
import time
from operator import mul
import unittest
import inspect

def reshape_array(a, axes):
    new_order = [i for i in range(a.ndim) if i not in axes]
    new_order.extend(axes)
    b = numpy.transpose(a, new_order)
    new_shape = b.shape[:b.ndim-len(axes)]
    new_shape += (reduce(mul, b.shape[b.ndim-len(axes):]),)
    b = b.reshape(new_shape)
    return b
#--- End: def

class DataTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')

    chunk_sizes = (17, 34, 300, 100000)[::-1]
    original_chunksize = cf.CHUNKSIZE()

    test_only = ()
#    test_only = ('NOTHING!!!!!')
#    test_only = ('test_Data__collapse_UNWEIGHTED_MASKED',)
#    test_only = ('test_Data__collapse_UNWEIGHTED_UNMASKED',)
#    test_only = ('test_Data__collapse_WEIGHTED_UNMASKED',)
#    test_only = ('test_Data__collapse_WEIGHTED_MASKED',)
#    test_only = ('test_Data_any',)
#    test_only = ('test_Data_mean',)
#    test_only = ('test_Data_sums_of_weights',)
#    test_only = ('test_Data_sample_size','test_Data_sd_var')
#    test_only = ('test_Data_sd_var',)
#    test_only = ('test_Data___setitem__',)
#    test_only = ('test_Data_ceil', 'test_Data_floor', 'test_Data_trunc', 'test_Data_rint')
#    test_only = ('test_Data_array', 'test_Data_varray', 'test_Data_dtarray',)
#    test_only = ('test_dumpd_loadd',)
#    test_only = ('test_Data_year_month_day_hour_minute_second',)
#    test_only =  ('test_Data_BINARY_AND_UNARY_OPERATORS',)
#    test_only =  ('test_Data_clip',)

    # Variables for _collapse
    a = numpy.arange(-100, 200., dtype=float).reshape(3, 4, 5, 5) 

    w = numpy.arange(1, 301., dtype=float).reshape(a.shape)
    w[-1, -1, ...] = w[-1, -1, ...]*2
    w /= w.min() 

    ones = numpy.ones(a.shape, dtype=float)
    
    ma = numpy.ma.arange(-100, 200., dtype=float).reshape(3, 4, 5, 5)
    ma[0, :, 2, 3] = numpy.ma.masked
    ma[1, 2, 3, :] = numpy.ma.masked
    ma[0, 3, :, 3] = numpy.ma.masked
    ma[:, 1, 4, 4] = numpy.ma.masked

    mw = numpy.ma.array(w)

    mones = numpy.ma.array(ones, mask=ma.mask)
   
    axes_combinations = [axes
                         for n in range(1, a.ndim+1)
                         for axes in itertools.permutations(range(a.ndim), n)]

    def test_Data___contains__(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
            d = cf.Data([[0.0, 1,  2], [3, 4, 5]], units='m')
            self.assertTrue(4 in d)
            self.assertFalse(40 in d)
            self.assertTrue(cf.Data(3) in d)
            self.assertTrue(cf.Data([[[[3]]]]) in d)
            value = d[1, 2]
            value.Units *= 2
            value.squeeze(0)
            self.assertTrue(value in d)
            self.assertTrue(numpy.array([[[2]]]) in d)
#            print "pmshape =", d._pmshape

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data___setitem__(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
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
                                            (Ellipsis, slice(None)),
                                            (slice(None), Ellipsis),
                                        )):
                    n = -n-1
                    for dvalue, avalue in ((n, n), (cf.masked, numpy.ma.masked), (n, n)):
                        message = "cf.Data[%s, %s]=%s failed" % (j, i, dvalue)
                        d[j, i] = dvalue
                        a[j, i] = avalue
                        self.assertTrue((d.array == a).all() in (True, numpy.ma.masked), message)
                        self.assertTrue((d.mask.array == numpy.ma.getmaskarray(a)).all(), message)
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
                    message = 'cf.Data[%s, %s]=%s failed' % (j, i, dvalue)
                    d[j, i] = dvalue
                    a[j, i] = dvalue
                    self.assertTrue((d.array == a).all() in (True, numpy.ma.masked), message)
                    self.assertTrue((d.mask.array == numpy.ma.getmaskarray(a)).all(), message)
                #--- End: for
#                print 'hardmask =',hardmask,', pmshape =', d._pmshape
            #--- End: for

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_all(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data(numpy.array([[0] * 1000]))
            self.assertTrue(not d.all())            
            d[-1,-1] = 1
            self.assertFalse(d.all())            
            d[...] = 1
            self.assertTrue(d.all())        
            d[...] = cf.masked
            self.assertTrue(d.all())

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_any(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data(numpy.array([[0] * 1000]))
            self.assertFalse(d.any())        
            d[-1,-1] = 1
            self.assertTrue(d.any())            
            d[...] = 1
            self.assertTrue(d.any())
            d[...] = cf.masked
            self.assertFalse(d.any())

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_array(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        # Scalar numeric array
        d = cf.Data(9, 'km')
        a = d.array
        self.assertTrue(a.shape == ())
        self.assertTrue(a == numpy.array(9))
        d[...] = cf.masked
        a = d.array
        self.assertTrue(a.shape == ())
        self.assertTrue(a[()] is numpy.ma.masked)

        # Non-scalar numeric array
        b = numpy.arange(10*15*19).reshape(10, 1, 15, 19)
        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)
            d = cf.Data(b, 'km')
            a = d.array
            a[0,0,0,0] = -999
            a2 = d.array
            self.assertTrue(a2[0,0,0,0] == 0)
            self.assertTrue(a2.shape == b.shape)
            self.assertTrue((a2 == b).all())
            self.assertFalse((a2 == a).all())

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_clip(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        c0 = -53.234
        c1 = 34.345456567

        a = self.a + 0.34567
        ac = numpy.clip(a, c0, c1)

        for chunksize in self.chunk_sizes: 
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data(a, 'km')
            e = d.clip(c0, c1)
            self.assertTrue((e.array == ac).all())
            e = d.clip(c0*1000, c1*1000, units='m')
            self.assertTrue((e.array == ac).all())
            d.clip(c0*100, c1*100, units='10m', i=True)
            self.assertTrue(d.allclose(ac, rtol=1e-05, atol=1e-08))
        #--- End: for

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_dtarray(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        # Scalar array
        for d in [cf.Data(11292.5, 'days since 1970-1-1'),
                  cf.Data('2000-12-1 12:00', dt=True)]:
            a = d.dtarray
            self.assertTrue(a.shape == ())
            self.assertTrue(a == numpy.array(cf.dt('2000-12-1 12:00')))
            a = d.array
            self.assertTrue(a.shape == ())
            self.assertTrue(a == 11292.5)
            a = d.dtarray
            a = d.array
            self.assertTrue(a.shape == ())
            self.assertTrue(a == 11292.5)

        # Non-scalar array
        for d in [cf.Data([[11292.5, 11293.5]], 'days since 1970-1-1'),
                  cf.Data([['2000-12-1 12:00', '2000-12-2 12:00']], dt=True)]:
            a = d.dtarray
            a = d.array
            self.assertTrue((a == [[11292.5, 11293.5]]).all())
            a = d.dtarray
            a = d.array
            self.assertTrue((a == [[11292.5, 11293.5]]).all())
            a = d.dtarray
            self.assertTrue((a == numpy.array([[cf.dt('2000-12-1 12:00'),
                                                cf.dt('2000-12-2 12:00')]])).all())
    #--- End: def

    def test_Data_asdatetime_asreftime(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data([[1.93, 5.17]], 'days since 2000-12-29')
            self.assertTrue(d.dtype == numpy.dtype(float))
            self.assertFalse(d._isdt)
            d.asreftime(i=True)
            self.assertTrue(d.dtype == numpy.dtype(float))
            self.assertFalse(d._isdt)
            d.asdatetime(i=True)
            self.assertTrue(d.dtype == numpy.dtype(object))
            self.assertTrue(d._isdt)
            d.asdatetime(i=True)
            self.assertTrue(d.dtype == numpy.dtype(object))
            self.assertTrue(d._isdt)
            d.asreftime(i=True)
            self.assertTrue(d.dtype == numpy.dtype(float))
            self.assertFalse(d._isdt)
#            print "pmshape =", d._pmshape

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_ceil(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for x in (1, -1):
            a = 0.9 * x * self.a
            c = numpy.ceil(a)
            
            for chunksize in self.chunk_sizes:   
                cf.CHUNKSIZE(chunksize)          
                d = cf.Data(a)
                d.ceil(i=True)
                self.assertTrue(d.shape == c.shape)
                self.assertTrue((d.array == c).all())
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_floor(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for x in (1, -1):
            a = 0.9 * x * self.a
            c = numpy.floor(a)

            for chunksize in self.chunk_sizes:   
                cf.CHUNKSIZE(chunksize)          
                d = cf.Data(a)
                d.floor(i=True)
                self.assertTrue(d.shape == c.shape)
                self.assertTrue((d.array == c).all())
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_trunc(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for x in (1, -1):
            a = 0.9 * x * self.a
            c = numpy.trunc(a)
            
            for chunksize in self.chunk_sizes:   
                cf.CHUNKSIZE(chunksize)          
                d = cf.Data(a)
                d.trunc(i=True)
                self.assertTrue(d.shape == c.shape)
                self.assertTrue((d.array == c).all())
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_rint(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for x in (1, -1):
            a = 0.9 * x * self.a
            c = numpy.rint(a)
            
            for chunksize in self.chunk_sizes:   
                cf.CHUNKSIZE(chunksize)          
                d = cf.Data(a)
                d.rint(i=True)
                self.assertTrue(d.shape == c.shape)
                self.assertTrue((d.array == c).all())
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_round(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for decimals in range(-8, 8):
            a = self.a + 0.34567
            c = numpy.round(a, decimals=decimals)
                
            for chunksize in self.chunk_sizes:   
                cf.CHUNKSIZE(chunksize)          
                d = cf.Data(a)
                d.round(decimals=decimals, i=True)
                self.assertTrue(d.shape == c.shape)
                self.assertTrue((d.array == c).all())
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_datum(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data(5, 'metre')
            self.assertTrue(d.datum()   == 5)
            self.assertTrue(d.datum(0)  == 5)
            self.assertTrue(d.datum(-1) == 5)
            
            for d in [cf.Data([4, 5, 6, 1, 2, 3], 'metre'),
                      cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')]:
                self.assertTrue(d.datum(0)  == 4)
                self.assertTrue(d.datum(-1) == 3)
                for index in d.ndindex():
                    self.assertTrue(d.datum(index)  == d.array[index].item())
                    self.assertTrue(d.datum(*index) == d.array[index].item())
            #--- End: for
            
            d = cf.Data(5, 'metre')
            d[()] = cf.masked
            self.assertTrue(d.datum()   is cf.masked)
            self.assertTrue(d.datum(0)  is cf.masked)
            self.assertTrue(d.datum(-1) is cf.masked)
    
            d = cf.Data([[5]], 'metre')
            d[0, 0] = cf.masked
            self.assertTrue(d.datum()        is cf.masked)
            self.assertTrue(d.datum(0)       is cf.masked)
            self.assertTrue(d.datum(-1)      is cf.masked)
            self.assertTrue(d.datum(0, 0)    is cf.masked)
            self.assertTrue(d.datum(-1, 0)   is cf.masked)
            self.assertTrue(d.datum([0, 0])  is cf.masked)
            self.assertTrue(d.datum([0, -1]) is cf.masked)
            self.assertTrue(d.datum(-1, -1)  is cf.masked)
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_flip(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            array = numpy.arange(24000).reshape(120, 200)
            d = cf.Data(array.copy(), 'metre')
            
            for axes, indices in zip(
                    (0, 1, [0, 1]),
                    ((slice(None, None, -1), slice(None)),
                     (slice(None)          , slice(None, None, -1)),
                     (slice(None, None, -1), slice(None, None, -1)))
            ):
                array = array[indices]
                d.flip(axes, i=True)
            #--- End: for
            self.assertTrue((d.array == array).all())
#            print 'mshape =', d._pmshape
        #--- End: def
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_max(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')
            self.assertTrue(d.max() == cf.Data(6, 'metre'))
            self.assertTrue(d.max().datum() == 6)
            d[0, 2] = cf.masked
            self.assertTrue(d.max() == 5)
            self.assertTrue(d.max().datum() == 5)
            self.assertTrue(d.max() == cf.Data(0.005, 'km'))
#            print 'pmshape =', d._pmshape
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_min(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')
            self.assertTrue(d.min() == cf.Data(1, 'metre'))
            self.assertTrue(d.min().datum() == 1)
            d[1, 0] = cf.masked
            self.assertTrue(d.min() == 2)
            self.assertTrue(d.min().datum() == 2)
            self.assertTrue(d.min() == cf.Data(0.002, 'km'))
#            print 'pmshape =', d._pmshape

        cf.CHUNKSIZE(self.original_chunksize)
     #--- End: def

    def test_Data_ndindex(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            for d in (cf.Data(5, 'metre'),
                      cf.Data([4, 5, 6, 1, 2, 3], 'metre'),
                      cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')
                      ):
                for i, j in zip(d.ndindex(), numpy.ndindex(d.shape)):
                    self.assertTrue(i == j)
            #--- End: for
#            print 'pmshape =', d._pmshape
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def
        
    def test_Data_roll(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            a = numpy.arange(10*15*19).reshape(10, 1, 15, 19)
            d = cf.Data(a)

            pmshape = d._pmshape

            e = d.roll(0,  4)
            e.roll(2, 120, i=True)
            e.roll(3, -77, i=True)
            
            a = numpy.roll(a,   4, 0)
            a = numpy.roll(a, 120, 2)
            a = numpy.roll(a, -77, 3)
            
            self.assertTrue(e.shape == a.shape)
            self.assertTrue((a == e.array).all())
            
            f = e.roll(3,   77)
            f.roll(2, -120, i=True)
            f.roll(0,   -4, i=True)
            
            self.assertTrue(f.shape == d.shape)
            self.assertTrue(f.equals(d))
            
#            print 'pmshape =', pmshape
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_sample_size(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data([[4, 5, 6], [1, 2, 3]], 'metre')
            self.assertTrue(d.sample_size() == 6)
            d[1, 0] = cf.masked
            self.assertTrue(d.sample_size() == cf.Data(50, '0.1'))

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_swapaxes(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            a = numpy.arange(10*15*19).reshape(10, 1, 15, 19)
            d = cf.Data(a.copy())
     
            for i in range(-a.ndim, a.ndim):
                for j in range(-a.ndim, a.ndim):
                    b = numpy.swapaxes(a.copy(), i, j)
                    e = d.swapaxes(i, j)
                    message = 'cf.Data.swapaxes(%d, %d) failed' % (i, j)
                    self.assertTrue(b.shape == e.shape, message)
                    self.assertTrue((b == e.array).all(), message)
                #--- End: for
            #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def
                
    def test_Data_transpose(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            a = numpy.arange(10*15*19).reshape(10, 1, 15, 19)
            d = cf.Data(a.copy())

            for indices in (range(a.ndim), range(-a.ndim, 0)):
                for axes in itertools.permutations(indices):
                    a = numpy.transpose(a, axes)
                    d.transpose(axes, i=True)
                    message = 'cf.Data.transpose(%s) failed: d.shape=%s, a.shape=%s' % \
                              (axes, d.shape, a.shape)
                    self.assertTrue(d.shape == a.shape, message)
                    self.assertTrue((d.array == a).all(), message)
                #--- End: for
            #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def
        
    def test_Data_unique(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return
            
        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data([[4, 2, 1], [1, 2, 3]], 'metre')
            self.assertTrue((d.unique() == cf.Data([1, 2, 3, 4], 'metre')).all())
            d[1, -1] = cf.masked
            self.assertTrue((d.unique() == cf.Data([1, 2, 4], 'metre')).all())

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_varray(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        # Scalar array
        d = cf.Data(9, 'km')
        d.hardmask = False
        a = d.varray
        self.assertTrue(a.shape == ())
        self.assertTrue(a == numpy.array(9))
        d[...] = cf.masked
        a = d.varray
        self.assertTrue(a.shape == ())
        self.assertTrue(a[()] is numpy.ma.masked)
        a[()] = 18
        self.assertTrue(a == numpy.array(18))

        b = numpy.arange(10*15*19).reshape(10, 1, 15, 19)
        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            d = cf.Data(b, 'km')
            e = d.copy()
            v = e.varray
            v[0,0,0,0] = -999
            v = e.varray
            self.assertTrue(v[0,0,0,0] == -999)
            self.assertTrue(v.shape == b.shape)
            self.assertFalse((v == b).all())
            v[0, 0, 0, 0] = 0
            self.assertTrue((v == b).all())

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_year_month_day_hour_minute_second(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return
            
        d = cf.Data([[1.901, 5.101]], 'days since 2000-12-29')
        self.assertTrue(d.year.equals(cf.Data([[2000, 2001]])))
        self.assertTrue(d.month.equals(cf.Data([[12, 1]])))
        self.assertTrue(d.day.equals(cf.Data([[30, 3]])))
        self.assertTrue(d.hour.equals(cf.Data([[21, 2]])))
        self.assertTrue(d.minute.equals(cf.Data([[37, 25]])))
        self.assertTrue(d.second.equals(cf.Data([[26, 26]])))

        d = cf.Data([[1.901, 5.101]],
                    cf.Units('days since 2000-12-29', '360_day'))
        self.assertTrue(d.year.equals(cf.Data([[2000, 2001]])))
        self.assertTrue(d.month.equals(cf.Data([[12, 1]])))
        self.assertTrue(d.day.equals(cf.Data([[30, 4]])))
        self.assertTrue(d.hour.equals(cf.Data([[21, 2]])))
        self.assertTrue(d.minute.equals(cf.Data([[37, 25]])))
        self.assertTrue(d.second.equals(cf.Data([[26, 26]])))
        
        cf.CHUNKSIZE(self.original_chunksize)   
    #--- End: def

    def test_Data_BINARY_AND_UNARY_OPERATORS(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
            array=numpy.arange(3*4*5).reshape(3, 4, 5) + 1
            
            arrays =  (numpy.arange(3*4*5).reshape(3, 4, 5) + 1.0,
                       numpy.arange(3*4*5).reshape(3, 4, 5) + 1)

            for a0 in arrays:
                for a1 in arrays[::-1]:
                    d = cf.Data(a0[(slice(None, None, -1),)*a0.ndim], 'metre')
                    d.flip(i=True)
                    x = cf.Data(a1, 'metre')
    
                    self.assertTrue((d +  x).equals(cf.Data(a0 +  a1, 'm' ), traceback=1)), '%s+%s'  % (repr(d), x)
                    self.assertTrue((d *  x).equals(cf.Data(a0 *  a1, 'm2'), traceback=1)), '%s*%s'  % (repr(d), x)
                    self.assertTrue((d /  x).equals(cf.Data(a0 /  a1, '1' ), traceback=1)), '%s/%s'  % (repr(d), x)
                    self.assertTrue((d -  x).equals(cf.Data(a0 -  a1, 'm' ), traceback=1)), '%s-%s'  % (repr(d), x)
                    self.assertTrue((d // x).equals(cf.Data(a0 // a1, '1' ), traceback=1)), '%s//%s' % (repr(d), x)
                
                    self.assertTrue(d.__truediv__(x).equals(cf.Data(array.__truediv__(array), '1'), traceback=1)), '%s.__truediv__(%s)' % (d, x)
                    self.assertTrue(d.__rtruediv__(x).equals(cf.Data(array.__rtruediv__(array), '1'), traceback=1)) , '%s.__rtruediv__(%s)' % (d, x)
                    
                    try:
                        d ** x
                    except:
                        pass
                    else:
                        self.assertTrue((d**x).all(), '%s**%s' % (d, repr(x)))
    
#                    print '%s {+, -, *, /, //, **, __truediv__, __rtruediv__} %s passed' % (d, x),     "pmshape =", d._pmshape
                #--- End: for                       
            #--- End: for                       
                       
            for a0 in arrays:
                d = cf.Data(a0, 'metre')
    
                for x in (2, 2.0):
                    self.assertTrue((d +  x).equals(cf.Data(a0 +  x, 'm' ), traceback=1)), '%s+%s'  % (repr(d), x)
                    self.assertTrue((d *  x).equals(cf.Data(a0 *  x, 'm' ), traceback=1)), '%s*%s'  % (repr(d), x)
                    self.assertTrue((d /  x).equals(cf.Data(a0 /  x, 'm' ), traceback=1)), '%s/%s'  % (repr(d), x)
                    self.assertTrue((d -  x).equals(cf.Data(a0 -  x, 'm' ), traceback=1)), '%s-%s'  % (repr(d), x)
                    self.assertTrue((d // x).equals(cf.Data(a0 // x, 'm' ), traceback=1)), '%s//%s' % (repr(d), x)
                    self.assertTrue((d ** x).equals(cf.Data(a0 ** x, 'm2'), traceback=1)), '%s**%s' % (repr(d), x)
                    
                    self.assertTrue(d.__truediv__(x).equals(cf.Data(a0.__truediv__(x), 'm'), traceback=1)), '%s.__truediv__(%s)' % (d, x)

                    self.assertTrue(d.__rtruediv__(x).equals(cf.Data(a0.__rtruediv__(x), 'm-1'), traceback=1)) , '%s.__rtruediv__(%s)' % (d, x)
          
#                    print '%s {+, -, *, /, //, **, __truediv__, __rtruediv__} %s passed' % (d, x),                         "pmshape =", d._pmshape
                    
                    self.assertTrue((x +  d).equals(cf.Data(x +  a0, 'm'  ), traceback=1)), '%s+%s'  % (x, repr(d))
                    self.assertTrue((x *  d).equals(cf.Data(x *  a0, 'm'  ), traceback=1)), '%s*%s'  % (x, repr(d))
                    self.assertTrue((x /  d).equals(cf.Data(x /  a0, 'm-1'), traceback=1)), '%s/%s'  % (x, repr(d))
                    self.assertTrue((x -  d).equals(cf.Data(x -  a0, 'm'  ), traceback=1)), '%s-%s'  % (x, repr(d))
                    self.assertTrue((x // d).equals(cf.Data(x // a0, 'm-1'), traceback=1)), '%s//%s' % (x, repr(d))
    
                    try:
                        x ** d
                    except:
                        pass
                    else:
                        self.assertTrue((x**d).all(), '%s**%s' % (x, repr(d)))
    
#                    print '%s {+, -, *, /, //, **} %s passed' % (x, repr(d)), "pmshape =", d._pmshape
                
                    a = a0.copy()                        
                    try:
                        a += x
                    except TypeError:
                        pass
                    else:
                        e = d.copy()
                        e += x
                        self.assertTrue(e.equals(cf.Data(a, 'm'), traceback=1)), '%s+=%s' % (repr(d), x)

                    a = a0.copy()                        
                    try:
                        a *= x
                    except TypeError:
                        pass
                    else:
                        e = d.copy()
                        e *= x
                        self.assertTrue(e.equals(cf.Data(a, 'm'), traceback=1)), '%s*=%s' % (repr(d), x)

                    a = a0.copy()                        
                    try:
                        a /= x
                    except TypeError:
                        pass
                    else:
                        e = d.copy()
                        e /= x
                        self.assertTrue(e.equals(cf.Data(a, 'm'), traceback=1)), '%s/=%s' % (repr(d), x)

                    a = a0.copy()                        
                    try:
                        a -= x
                    except TypeError:
                        pass
                    else:
                        e = d.copy()
                        e -= x
                        self.assertTrue(e.equals(cf.Data(a, 'm'), traceback=1)), '%s-=%s' % (repr(d), x)

                    a = a0.copy()                        
                    try:
                        a //= x
                    except TypeError:
                        pass
                    else:
                        e = d.copy()
                        e //= x
                        self.assertTrue(e.equals(cf.Data(a, 'm'), traceback=1)), '%s//=%s' % (repr(d), x)


                    a = a0.copy()                        
                    try:
                        a **= x
                    except TypeError:
                        pass
                    else:
                        e = d.copy()
                        e **= x
                        self.assertTrue(e.equals(cf.Data(a, 'm2'), traceback=1)), '%s**=%s' % (repr(d), x)

                    a = a0.copy()                        
                    try:
                        a.__itruediv__(x)
                    except TypeError:
                        pass
                    else:
                        e = d.copy()
                        e.__itruediv__(x)
                        self.assertTrue(e.equals(cf.Data(a, 'm'), traceback=1)), '%s.__itruediv__(%s)' % (d, x)
                
#                    print '%s {+=, -=, *=, /=, //=, **=, __itruediv__} %s passed' % (repr(d), x),                         "pmshape =", d._pmshape
                #--- End: for
                
                for x in (cf.Data(2, 'metre'), cf.Data(2.0, 'metre')):
                    self.assertTrue((d +  x).equals(cf.Data(a0 +  x.datum(), 'm' ), traceback=1))
                    self.assertTrue((d *  x).equals(cf.Data(a0 *  x.datum(), 'm2'), traceback=1))
                    self.assertTrue((d /  x).equals(cf.Data(a0 /  x.datum(), '1' ), traceback=1))
                    self.assertTrue((d -  x).equals(cf.Data(a0 -  x.datum(), 'm' ), traceback=1))
                    self.assertTrue((d // x).equals(cf.Data(a0 // x.datum(), '1' ), traceback=1))
    
                    try:
                       d ** x
                    except:
                        pass
                    else:
                        self.assertTrue((x**d).all(), '%s**%s' % (x, repr(d)))
    
                    self.assertTrue(d.__truediv__(x).equals(cf.Data(a0.__truediv__(x.datum()), ''), traceback=1))
                
#                    print '%s {+, -, *, /, //, **, __truediv__} %s passed' % (repr(d), repr(x)),                         "pmshape =", d._pmshape
                #--- End: for
            #--- End: for
        #--- End: for

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def
        
    def test_Data_BROADCASTING(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

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
            
        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
            for a in A:
                for b in A:
                    d = cf.Data(a)
                    e = cf.Data(b)
                    ab = a*b
                    de = d*e
                    self.assertTrue(de.shape == ab.shape)
                    self.assertTrue((de.array == ab).all())
                #--- End: for
            #--- End: for
        #--- End: for

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data__collapse_SHAPE(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        a = numpy.arange(-100, 200., dtype=float).reshape(3, 4, 5, 5)
        ones = numpy.ones(a.shape, dtype=float)
        
        for h in ('sample_size', 'sum', 'min', 'max', 'mean', 'var', 'sd',
                  'mid_range', 'range'):
            for chunksize in self.chunk_sizes:   
                cf.CHUNKSIZE(chunksize)          
    
                d = cf.Data(a[(slice(None, None, -1),) * a.ndim].copy())
                d.flip(i=True)
                x = cf.Data(self.w.copy())
                
                shape = list(d.shape)
     
                for axes in self.axes_combinations:
                    e = getattr(d, h)(axes=axes, squeeze=False)
                    
                    shape = list(d.shape)
                    for i in axes:                        
                        shape[i] = 1
                        
                    shape = tuple(shape)
                    self.assertTrue(
                        e.shape == shape,
                        "%s, axes=%s, not squeezed bad shape: %s != %s" % \
                        (h, axes, e.shape, shape))
                #--- End: for
    
                for axes in self.axes_combinations:
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
                self.assertTrue(
                    e.shape == shape,
                    "%s, axes=%s, squeezed bad shape: %s != %s" % \
                    (h, None, e.shape, shape))
    
                e = getattr(d, h)(squeeze=False)
                shape = (1,) * d.ndim
                self.assertTrue(
                    e.shape == shape,
                    "%s, axes=%s, not squeezed bad shape: %s != %s" % \
                    (h, None, e.shape, shape))
    
#                print 'h=', h, 'pmshape =', d._pmshape
            #--- End: for
        #--- End: for

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_max_min_sum(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          
           
            # unweighted, unmasked
            d = cf.Data(self.a)
            for np, h in zip((numpy.sum, numpy.amin, numpy.amax),
                             (     'sum',     'min',     'max')):
                for axes in self.axes_combinations:
                    b = reshape_array(self.a, axes)
                    b = np(b, axis=-1)                
                    e = getattr(d, h)(axes=axes, squeeze=True)
                    self.assertTrue(
                        e.allclose(b, rtol=1e-05, atol=1e-08),
                        "%s, axis=%s, unweighted, unmasked \ne=%s, \nb=%s, \ne-b=%s" %
                        (h, axes, e.array, b, e.array-b))
            #--- End: for
    
            # unweighted, masked
            d = cf.Data(self.ma)
            for np, h in zip((numpy.ma.sum, numpy.ma.amin, numpy.ma.amax),
                             (     'sum',     'min',     'max')):
                for axes in self.axes_combinations:
                    b = reshape_array(self.ma, axes)
                    b = np(b, axis=-1)                
                    b = numpy.ma.asanyarray(b)
                    e = getattr(d, h)(axes=axes, squeeze=True)
    
                    self.assertTrue(
                        (e.mask.array == b.mask).all(),
                        "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" %
                        (h, axes, e.mask.array, b.mask, e.mask.array==b.mask))

                    self.assertTrue(
                        e.allclose(b, rtol=1e-05, atol=1e-08),
                        "%s, axis=%s, unweighted, masked \ne=%s, \nb=%s, \ne-b=%s" %
                        (h, axes, e.array, b, e.array-b))
            #--- End: for
        #--- End: for

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: for         

    def test_Data_sum_of_weights_sum_of_weights2(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          

            # unweighted, masked
            d = cf.Data(self.ma)
            for a, h in zip((self.mones      , self.mones), 
                            ('sum_of_weights', 'sum_of_weights2')):
                for axes in self.axes_combinations:
                    b = reshape_array(a, axes)
                    b = numpy.ma.asanyarray(b.sum(axis=-1))
                    e = getattr(d, h)(axes=axes, squeeze=True)  
    
                    self.assertTrue(
                        (e.mask.array == b.mask).all(),
                        "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" %
                        (h, axes, e.mask.array, b.mask, e.mask.array==b.mask))

                    self.assertTrue(
                        e.allclose(b, rtol=1e-05, atol=1e-08),
                        "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" %
                        (h, axes, e.array, b, e.array-b))
                #--- End: for
#                print "pmshape =", d._pmshape
            #--- End: for    

            # unweighted, masked
            d = cf.Data(self.a)
            for h in ('sum_of_weights', 'sum_of_weights2'):
                for axes in self.axes_combinations:
                    b = reshape_array(self.ones, axes)
                    b = b.sum(axis=-1)
                    e = getattr(d, h)(axes=axes, squeeze=True)
                    
                    self.assertTrue(
                        e.allclose(b, rtol=1e-05, atol=1e-08),
                        "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                        (h, axes, e.array, b, e.array-b))
            #--- End: for

            # weighted, masked
            d = cf.Data(self.ma)
            x = cf.Data(self.w)
            for a, h in zip((self.mw         , self.mw*self.mw), 
                            ('sum_of_weights', 'sum_of_weights2')):
                for axes in self.axes_combinations:
                    a = a.copy()
                    a.mask = self.ma.mask
                    b = reshape_array(a, axes)
                    b = numpy.ma.asanyarray(b.sum(axis=-1))
                    e = getattr(d, h)(axes=axes, weights=x, squeeze=True)  
                    self.assertTrue(
                        (e.mask.array == b.mask).all(),
                        "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" %
                        (h, axes, e.mask.array, b.mask, e.mask.array==b.mask))

                    self.assertTrue(
                        e.allclose(b, rtol=1e-05, atol=1e-08),
                        "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" %
                        (h, axes, e.array, b, e.array-b))
            #--- End: for
    
            # weighted, unmasked
            d = cf.Data(self.a)
            for a, h in zip((self.w          , self.w*self.w), 
                            ('sum_of_weights', 'sum_of_weights2')):
                for axes in self.axes_combinations:
                    b = reshape_array(a, axes)
                    b = b.sum(axis=-1)                
                    e = getattr(d, h)(axes=axes, weights=x, squeeze=True)
                    self.assertTrue(
                        e.allclose(b, rtol=1e-05, atol=1e-08),
                        "%s, axis=%s, \ne=%s, \nb=%s, \ne-b=%s" %
                        (h, axes, e.array, b, e.array-b))
            #--- End: for
        #--- End: for    

        cf.CHUNKSIZE(self.original_chunksize)
    #---End: def

    def test_Data_mean(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize)          

            # unweighted, unmasked
            d = cf.Data(self.a)
            for axes in self.axes_combinations:
                b = reshape_array(self.a, axes)
                b = numpy.mean(b, axis=-1)                
                e = d.mean(axes=axes, squeeze=True)
                self.assertTrue(
                    e.allclose(b, rtol=1e-05, atol=1e-08),
                    "axis=%s, unweighted, unmasked \ne=%s, \nb=%s, \ne-b=%s" %
                    (axes, e.array, b, e.array-b))
            #--- End: for
    
            # weighted, unmasked
            x = cf.Data(self.w)
            for axes in self.axes_combinations:
                b = reshape_array(self.a, axes)
                v = reshape_array(self.w, axes)
                b = numpy.average(b, axis=-1, weights=v)
                e = d.mean(axes=axes, weights=x, squeeze=True)

                self.assertTrue(
                    e.allclose(b, rtol=1e-05, atol=1e-08),
                    "axis=%s, \ne=%s, \nb=%s, \ne-b=%s" %
                    (axes, e.array, b, e.array-b))
            #--- End: for

            # unweighted, masked
            d = cf.Data(self.ma)
            for axes in self.axes_combinations:
                b = reshape_array(self.ma, axes)
                b = numpy.ma.average(b, axis=-1)
                b = numpy.ma.asanyarray(b)
    
                e = d.mean(axes=axes, squeeze=True)
    
                self.assertTrue(
                    (e.mask.array == b.mask).all(),
                    "axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" %
                    (axes, e.mask.array, b.mask, e.mask.array==b.mask))

                self.assertTrue(
                    e.allclose(b, rtol=1e-05, atol=1e-08),
                    "axis=%s, \ne=%s, \nb=%s, \ne-b=%s" %
                    (axes, e.array, b, e.array-b))
            #--- End: for
     
            # weighted, masked
            for axes in self.axes_combinations:
                b = reshape_array(self.ma, axes)
                v = reshape_array(self.mw, axes)
                b = numpy.ma.average(b, axis=-1, weights=v)
                b = numpy.ma.asanyarray(b)
    
                e = d.mean(axes=axes, weights=x, squeeze=True)
    
                self.assertTrue(
                    (e.mask.array == b.mask).all(),
                    "axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" %
                    (axes, e.mask.array, b.mask, e.mask.array==b.mask))

                self.assertTrue(
                    e.allclose(b, rtol=1e-05, atol=1e-08),
                    "axis=%s, \ne=%s, \nb=%s, \ne-b=%s" %
                    (axes, e.array, b, e.array-b))
            #--- End: for

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_sample_size(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 

            # unmasked 
            d = cf.Data(self.a)
            for axes in self.axes_combinations:
                b = reshape_array(self.ones, axes)
                b = b.sum(axis=-1)
                e = d.sample_size(axes=axes, squeeze=True)
                
                self.assertTrue(
                    e.allclose(b, rtol=1e-05, atol=1e-08),
                    "axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                    (axes, e.array, b, e.array-b))
            #--- End: for
    
            # masked 
            d = cf.Data(self.ma)
            for axes in self.axes_combinations:
                b = reshape_array(self.mones, axes)
                b = b.sum(axis=-1)
                e = d.sample_size(axes=axes, squeeze=True)
                
                self.assertTrue(
                    e.allclose(b, rtol=1e-05, atol=1e-08),
                    "axis=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                    (axes, e.array, b, e.array-b))
            #--- End: for
    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_sd_var(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        ddofs=(0, 1, 2)
        f = 2

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 

            # unweighted, unmasked
            d = cf.Data(self.a, units='K')
            for np, h in zip((numpy.var, numpy.std),
                             ('var'    , 'sd')):
                for ddof in ddofs:
                    for axes in self.axes_combinations:
                        b = reshape_array(self.a, axes)
                        b = np(b, axis=-1, ddof=ddof)                
                        e = getattr(d, h)(axes=axes, squeeze=True, ddof=ddof)
                        self.assertTrue(
                            e.allclose(b, rtol=1e-05, atol=1e-08),
                            "%s, axis=%s, unweighted, unmasked \ne=%s, \nb=%s, \ne-b=%s" %
                            (h, axes, e.array, b, e.array-b))
            #--- End: for

            # unweighted, masked
            d = cf.Data(self.a, units='K')
            x = cf.Data(self.w)
            for h in ('var', 'sd'):
                for axes in self.axes_combinations:                
                    for ddof in ddofs:
                        e = getattr(d, h)(axes=axes, squeeze=True, ddof=ddof)
    
                        b = reshape_array(self.a, axes)
    
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
                        
                        self.assertTrue(
                            (e.mask.array == b.mask).all(),
                            "%s, axes=%s, ddof=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" %
                            (h, axes, ddof, e.mask.array, b.mask, e.mask.array==b.mask))
                        self.assertTrue(
                            e.allclose(b, rtol=1e-05, atol=1e-08),
                            "%s, axes=%s, ddof=%s, \ne=%s, \nb=%s, \ne-b=%s" %
                            (h, axes, ddof, e.array, b, e.array-b))
            #--- End: for

            # weighted, unmasked 
            f= 2
            d = cf.Data(self.a, units='K')
            x = cf.Data(self.w)
            for h in ('var', 'sd'):
                for axes in self.axes_combinations:                
                    for ddof in ddofs:
                        b = reshape_array(self.a, axes)
                        v = reshape_array(self.w, axes)
                        
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
    
                        self.assertTrue(
                            e.allclose(b, rtol=1e-05, atol=1e-08) ,
                            "%s, axis=%s, ddof=%s, \ne=%s, \nb=%s, \ne-b=%s" % \
                            (h, axes, ddof, e.array, b, e.array-b))
            #--- End: for

            # weighted, masked
            f = 2
            d = cf.Data(self.ma, units='K')
            x = cf.Data(self.w)
            for h in ('var', 'sd'):
                for axes in self.axes_combinations:                
                    for ddof in ddofs:
                        b = reshape_array(self.ma, axes)
                        v = reshape_array(self.mw, axes)
    
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
    
                        if h == 'sd':
                            self.assertTrue(e.Units == d.Units)
                        else:                            
                            self.assertTrue(e.Units == d.Units**2)
                   
                        self.assertTrue(
                            (e.mask.array == b.mask).all(),
                            "%s, axis=%s, \ne.mask=%s, \nb.mask=%s, \ne.mask==b.mask=%s" %
                            (h, axes, e.mask.array, b.mask, e.mask.array==b.mask))

                        self.assertTrue(
                            e.allclose(b, rtol=1e-05, atol=1e-08),
                            "%s, axis=%s, ddof=%s, \ne=%s, \nb=%s, \ne-b=%s" %
                            (h, axes, ddof, e.array, b, e.array-b))
            #--- End: for
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Data_dumpd_loadd(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
            
            d = cf.read(self.filename)[0].data
            
            dumpd = d.dumpd()
            self.assertTrue(d.equals(cf.Data(loadd=d.dumpd()), traceback=True))
            self.assertTrue(d.equals(cf.Data(loadd=d.dumpd()), traceback=True))
            d.to_disk()                        
            self.assertTrue(d.equals(cf.Data(loadd=d.dumpd()), traceback=True))
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

#--- End: class


if __name__ == "__main__":
    print 'cf-python version:'     , cf.__version__
    print 'cf-python path:'        , os.path.abspath(cf.__file__)
    print ''
    unittest.main(verbosity=2)
