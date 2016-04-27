
import os
import numpy
import cf
import unittest
import inspect

class FieldTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')

    filename2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'test_file2.nc')

    chunk_sizes = (17, 34, 300, 100000)[::-1]
    original_chunksize = cf.CHUNKSIZE()

    f = cf.read(filename)[0]  

    test_only = ()
#    test_only = ('test_Field_transpose','test_Field_squeeze',)
#    test_only = ('test_Field_collapse',)
#    test_only = ('test_Field_match','test_Field_items',)
#    test_only = ('test_Field_items',)
#    test_only = ('test_Field_axes','test_Field_data_axes',)
#    test_only = ('test_Field_where',)
#    test_only = ('test_Field_anchor',)
#    test_only = ('test_Field_period',)
#    test_only = ('test_FieldList_argless_methods',)

    def test_Field_anchor(self):  
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        dimarray = self.f.dim('grid_lon').array
      
        for chunksize in self.chunk_sizes:            
            f = cf.read(self.filename)[0]

            for period in (dimarray.min()-5, dimarray.min()):
                anchors = numpy.arange(dimarray.min()-3*period,
                                       dimarray.max()+3*period, 0.5)

                f.cyclic('grid_lon', period=period)

                # Increasing dimension coordinate    
                for anchor in anchors:
                    g = f.anchor('grid_lon', anchor)
                    x0 = g.coord('grid_lon').datum(-1) - period
                    x1 = g.coord('grid_lon').datum(0)
                    self.assertTrue(
                        x0 < anchor <= x1,
                        'INCREASING period=%s, x0=%s, anchor=%s, x1=%s' % \
                        (period, x0, anchor, x1))
                #--- End: for

                # Decreasing dimension coordinate    
                flipped_f = f.flip('grid_lon')
                for anchor in anchors:
                    g = flipped_f.anchor('grid_lon', anchor)
                    x1 = g.coord('grid_lon').datum(-1) + period
                    x0 = g.coord('grid_lon').datum(0)
                    self.assertTrue(
                        x1 > anchor >= x0,
                        'DECREASING period=%s, x0=%s, anchor=%s, x1=%s' % \
                        (period, x1, anchor, x0))
                #--- End: for
            #--- End: for
        #--- End: for    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Field_axes(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = self.f
        self.assertTrue(f.axes() == set(['dim0', 'dim1', 'dim2']))

        for i in range(f.ndim):
            self.assertTrue(f.axes(i) == set([f.data_axes()[i]]))

        self.assertTrue(f.axes(slice(0,3)) == set(f.data_axes()))
    #--- End: def

    def test_Field_data_axes(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        self.assertTrue(self.f.copy().data_axes() == ['dim0', 'dim1', 'dim2'])
        f = cf.Field(data=cf.Data(9))
        self.assertTrue(f.data_axes() == [])
        del f.Data
        self.assertTrue(f.data_axes() == None)
    #--- End: def

    def test_Field_equals(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:    
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.filename)[0]       
            g = f.copy()
            self.assertTrue(f.equals(g, traceback=True))
            self.assertFalse(f.equals(g+1, traceback=False))
        #--- End: for    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

#    def test_Field_indices(self):
#        if self.test_only and inspect.stack()[0][3] not in self.test_only:
#            return
#
#        for chunksize in self.chunk_sizes:            
#            f = cf.read(self.filename)[0]
#            
#            
#
#        cf.CHUNKSIZE(self.original_chunksize)
#    #--- End: def

    def test_Field_items(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]

        self.assertTrue(set(f.items()) == set(['aux0','aux1','aux2','aux3','aux4','dim0','dim1','dim2','msr0','ref0','ref1']))
        self.assertTrue(set(f.items(inverse=True)) == set([]))

        self.assertTrue(set(f.items(ndim=1)) == set(['aux0','aux1','aux4', 'dim0','dim1','dim2']))
        self.assertTrue(set(f.items(ndim=1, inverse=True)) == set(['aux2','aux3','msr0','ref0','ref1']))

        self.assertTrue(set(f.items(ndim=2)) == set(['aux2','aux3','msr0']))
        self.assertTrue(set(f.items(ndim=2, inverse=True)) == set(['aux0','aux1','aux4','dim0','dim1','dim2', 'ref0', 'ref1']))

        self.assertTrue(set(f.items(ndim=cf.ge(3))) == set([]))
        self.assertTrue(set(f.items(ndim=cf.ge(3), inverse=True)) == set(['aux0','aux1','aux2','aux3','aux4','dim0','dim1','dim2','msr0','ref0','ref1']))

        self.assertTrue(set(f.items(role='d'))    == set(['dim0','dim1','dim2']))
        self.assertTrue(set(f.items(role='da'))   == set(['aux0','aux1','aux2','aux3','aux4','dim0','dim1','dim2']))
        self.assertTrue(set(f.items(role='dam'))  == set(['aux0','aux1','aux2','aux3','aux4','dim0','dim1','dim2','msr0']))
        self.assertTrue(set(f.items(role='damr')) == set(['aux0','aux1','aux2','aux3','aux4','dim0','dim1','dim2','msr0','ref0','ref1']))

        self.assertTrue(set(f.items(axes='Y')) == set(['aux2','aux3','aux4','dim1','msr0']))
        self.assertTrue(set(f.items(axes='Y', inverse=True)) == set(['aux0','aux1','dim0','dim2','ref0','ref1']))
        self.assertTrue(set(f.items('X')) == set(['dim2']))
        self.assertTrue(set(f.items(['X', 'Y', {'standard_name': 'longitude', 'units': 'radians'}])) == 
                        set(['aux3','dim1','dim2']))
        self.assertTrue(set(f.items(['X', 'Y', {'standard_name': 'longitude', 'units': 'K'}])) == 
                        set(['dim1','dim2']))

        self.assertTrue(set(f.items(axes='X', ndim=2)) == set(['aux2','aux3','msr0']))
        self.assertTrue(set(f.items(axes='X', ndim=2, match_and=False)) == set(['aux2','aux3','dim2','msr0']))

        self.assertTrue(set(f.items('longitude', axes='X', ndim=2)) == set(['aux3']))
        self.assertTrue(set(f.items('grid_longitude', axes='X', ndim=2)) == set([]))
        self.assertTrue(set(f.items('grid_longitude', axes='X', ndim=2, match_and=False)) == 
                        set(['aux2','aux3','dim2','msr0']))

        self.assertTrue(set(f.items('atmosphere_hybrid_height_coordinate')) == set(['dim0','ref0']))

        self.assertTrue(set(f.items(axes='X'))       == set(['dim2','aux2','aux3','msr0']))
        self.assertTrue(set(f.items(axes='Y'))       == set(['dim1','aux2','aux3','aux4','msr0']))
        self.assertTrue(set(f.items(axes='Z'))       == set(['dim0','aux0','aux1']))
        self.assertTrue(set(f.items(axes=['X','Y'])) == set(['dim1','dim2','aux2','aux3','aux4','msr0']))
        self.assertTrue(set(f.items(axes=['X','Z'])) == set(['dim0','dim2','aux0','aux1','aux2','aux3','msr0']))
        self.assertTrue(set(f.items(axes=['Z','Y'])) == set(['dim0','dim1','aux0','aux1','aux2','aux3','aux4','msr0']))

        self.assertTrue(set(f.items(axes_all='X'))       == set(['dim2']))
        self.assertTrue(set(f.items(axes_all='Y'))       == set(['dim1','aux4']))
        self.assertTrue(set(f.items(axes_all='Z'))       == set(['dim0','aux0','aux1']))
        self.assertTrue(set(f.items(axes_all=['X','Y'])) == set(['aux2','aux3','msr0']))
        self.assertTrue(set(f.items(axes_all=['X','Z'])) == set([]))
        self.assertTrue(set(f.items(axes_all=['Z','Y'])) == set([]))

        self.assertTrue(set(f.items(axes_subset='X'))       == set(['dim2','aux2','aux3','msr0']))
        self.assertTrue(set(f.items(axes_subset='Y'))       == set(['dim1','aux2','aux3','aux4','msr0']))
        self.assertTrue(set(f.items(axes_subset='Z'))       == set(['dim0','aux0','aux1']))
        self.assertTrue(set(f.items(axes_subset=['X','Y'])) == set(['aux2','aux3','msr0']))
        self.assertTrue(set(f.items(axes_subset=['X','Z'])) == set([]))
        self.assertTrue(set(f.items(axes_subset=['Z','Y'])) == set([]))

        self.assertTrue(set(f.items(axes_superset='X'))       == set(['dim2']))
        self.assertTrue(set(f.items(axes_superset='Y'))       == set(['dim1','aux4']))
        self.assertTrue(set(f.items(axes_superset='Z'))       == set(['dim0','aux0','aux1']))
        self.assertTrue(set(f.items(axes_superset=['X','Y'])) == set(['dim1','dim2','aux2','aux3','aux4','msr0']))
        self.assertTrue(set(f.items(axes_superset=['X','Z'])) == set(['dim0','dim2','aux0','aux1']))
        self.assertTrue(set(f.items(axes_superset=['Z','Y'])) == set(['dim0','dim1','aux0','aux1','aux4']))
    #--- End: def

    def test_Field_match(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]
        f.long_name = 'qwerty'
        f.ncvar = 'tas'
        all_kwargs = (
            {'inverse': False},
            {'inverse': False, 'match': None},
            {'inverse': False, 'match': {}},
            {'inverse': False, 'match': []},
            {'inverse': False, 'match': [None]},
            {'inverse': False, 'match': [{}]},
            {'inverse': False, 'match': [None, {}]},
            {'inverse': False, 'match':  'eastward_wind'},
            {'inverse': False, 'match':  'eastward_wind', 'exact': True},
            {'inverse': False, 'match':  'eastward_'},
            {'inverse': False, 'match':  'e.*_wind$'},
            {'inverse': False, 'match':  'standard_name:eastward_wind'},
            {'inverse': False, 'match':  'standard_name:eastward_wind', 'exact': True},
            {'inverse': False, 'match':  'standard_name:eastward_'},
            {'inverse': False, 'match': {'standard_name': 'eastward_wind'}},
            {'inverse': False, 'match': {'standard_name': 'eastward_'}},
            {'inverse': False, 'match': cf.eq('.*_wind', exact=False)},
            {'inverse': False, 'match':  'long_name:qwerty'},
            {'inverse': False, 'match':  'long_name:qwerty', 'exact': True},
            {'inverse': False, 'match':  'long_name:qwe'},
            {'inverse': False, 'match': {'long_name': 'qwerty'}},
            {'inverse': False, 'match': {'long_name': 'qwe'}},
            {'inverse': False, 'match': {'long_name': cf.eq('qwerty')}},
            {'inverse': False, 'match': {'long_name': cf.eq('qwe', exact=False)}},
            {'inverse': False, 'match': 'ncvar%tas'},
            {'inverse': False, 'match': 'ncvar%tas', 'exact': True},
            {'inverse': False, 'match': 'ncvar%ta'},
            {'inverse': False, 'match': {None: 'ncvar%.*as$'}},
            {'inverse': False, 'match': {None: 'ncvar%tas$'}},
            {'inverse': False, 'match': {None: 'ncvar%tas'}},
            {'inverse': False, 'match': {None: 'ncvar%ta'}},
            #
            {'inverse': False, 'ndim': 3},
            {'inverse': False, 'match':  'eastward_wind', 'ndim': cf.wi(1, 3)},
            {'inverse': False, 'match':  'BBB', 'ndim': cf.wi(1, 3), 'match_and': False},
            {'inverse': False, 'match':  ['BBB', 'east'], 'ndim': cf.wi(1, 3), 'match_and': True},
            #            {'inverse': False}, 
            {'inverse': False, 'ndim': cf.wi(1, 3)},
#            {'inverse': False, 'match': 'eastward_wind'},
#            {'inverse': False, 'match': {'long_name': 'qwerty'}},
#            {'inverse': False, 'match': {'standard_name': 'east'}},
#            {'inverse': False, 'match': 'east'},
#            {'inverse': False, 'match': {'standard_name': 'east.*'}, 'exact': False},
#            {'inverse': False, 'match': 'east.*', 'exact': False},
#            {'inverse': False, 'match': cf.eq('east.*', exact=False)},
#            {'inverse': False, 'match': {'standard_name': cf.eq('east.*', exact=False)}},
#            {'inverse': False, 'match': {'standard_name': 'east', 'long_name': 'qwe'}},
#            {'inverse': False, 'match': {'standard_name': 'east', 'long_name': 'qwe'}, 'match_and': False},
#            {'inverse': False, 'match': {'standard_name': 'east', 'long_name': 'asd'}, 'match_and': False},
#            #
#            {'inverse': True, 'match': {'standard_name': 'east', 'long_name': 'asd'},},
        )
        for kwargs in all_kwargs:
            self.assertTrue(f.match(**kwargs), 
                            'f.match(**%s) failed' % kwargs)
            kwargs['inverse'] = not kwargs['inverse']
            self.assertFalse(f.match(**kwargs),
                             'f.match(**%s) failed' % kwargs)
        #--- End: for
    #--- End: def

    def test_Field_period(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)
        f.dim('X').period(None)
        f.cyclic('X', False)
        self.assertTrue(f.period('X') is None)
        f.cyclic('X', period=360)
        self.assertTrue(f.period('X') == cf.Data(360, 'degrees'))
        f.cyclic('X', False)
        self.assertTrue(f.period('X') == cf.Data(360, 'degrees'))
        f[0].dim('X').period(None)
        self.assertTrue(f.period('X') is None)
    #--- End: def

    def test_Field_squeeze(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f0 = cf.read(self.filename)

        for f in (f0, cf.FieldList(f0)):       
            f.squeeze(i=True)
            g = f.copy()
            h = f.copy()
            i = h.squeeze(i=True)
            self.assertTrue(f.equals(g))
            self.assertTrue(h is i)
        #--- End: for    
    #--- End: def

    def test_Field_transpose(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]
        self.assertTrue(f is f.transpose([0, 1, 2], i=True))
        self.assertTrue(f.equals(f.transpose([0, 1, 2])))

        for chunksize in self.chunk_sizes:            
            cf.CHUNKSIZE(chunksize)            
            f = cf.read(self.filename)[0]
            
            h = f.transpose((1, 2, 0))
            h.transpose((2, 0, 1), i=True)
            h.transpose(('grid_longitude', 'atmos', 'grid_latitude'), i=True)
            h.varray
            h.transpose(('atmos', 'grid_latitude', 'grid_longitude'), i=True)
            self.assertTrue(cf.equals(f, h, traceback=True))
#            print 'pmshape =', f.Data._pmshape
        #--- End: for    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Field_collapse(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:
            f = cf.read(self.filename2)[0]
            g = f.collapse('mean')
            self.assertTrue(g.cell_methods.equals(cf.CellMethods('time: maximum time: latitude: longitude: mean'), traceback=True))

            g = f.collapse('mean', axes=['T', 'X'])
            self.assertTrue(g.cell_methods.equals(cf.CellMethods('time: maximum time: longitude: mean'), traceback=True))

            g = f.collapse('mean', axes=[0, 2])
            self.assertTrue(g.cell_methods.equals(cf.CellMethods('time: maximum time: longitude: mean'), traceback=True))
            
            g = f.collapse('T: mean within years time: minimum over years', 
                           within_years=cf.M(), weights=None)
            self.assertTrue(g.cell_methods.equals(cf.CellMethods('time: maximum time: mean within years time: minimum over years'), traceback=True))

            for m in range(1, 13):
                a = numpy.empty((5, 4, 5))
                for i, year in enumerate(f.subspace(T=cf.month(m)).coord('T').year.unique()):
                    q = cf.month(m) & cf.year(year)
                    x = f.subspace(T=q)
                    x.data.mean(axes=0, i=True)
                    a[i] = x.array
                #--- End: for
                a = a.min(axis=0)
                self.assertTrue(numpy.allclose(a, g.array[m % 12]))
            #--- End: for  

            g = f.collapse('T: mean', group=360)

            for group in (cf.M(12), 
                          cf.M(12, month=12),
                          cf.M(12, day=16),
                          cf.M(12, year=1999, month=11, day=27)):
                g = f.collapse('T: mean', group=group)
                bound = g.coord('T').bounds.dtarray[0, 1]
                self.assertTrue(bound.month == group.month, "group=%s" % group)
                self.assertTrue(bound.day   == group.day  , "group=%s" % group)
            #--- End: for  

            for group in (cf.D(30), 
                          cf.D(30, month=12),
                          cf.D(30, day=16),
                          cf.D(30, year=1999, month=11, day=27)):
                g = f.collapse('T: mean', group=group)
                bound = g.coord('T').bounds.dtarray[0, 1]
                self.assertTrue(bound.day == group.day, "group=%s" % group)
            #--- End: for  

        #--- End: for    

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Field_where(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]
        a = f.array

        for chunksize in self.chunk_sizes:
            f = cf.read(self.filename)[0]

            for condition in (True, 1, [[[True]]], [[[[[456]]]]]):
                g = f.where(condition, -9)
                self.assertTrue(g[0].min() == -9)
                self.assertTrue(g[0].max() == -9)                

            g = f.where(cf.le(34), 34)
            self.assertTrue(g[0].min() == 34)
            self.assertTrue(g[0].max() == 89)   

            g = f.where(cf.le(34), cf.masked)
            self.assertTrue(g[0].min() == 35)
            self.assertTrue(g[0].max() == 89) 

            g = f.where(cf.le(34), cf.masked, 45)
            self.assertTrue(g[0].min() == 45)
            self.assertTrue(g[0].max() == 45)               
        #--- End: for

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def   

    def test_Field_mask_invalid(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]

        g = f.mask_invalid()
        g = cf.FieldList(f).mask_invalid()
        g = f.mask_invalid(i=True)
        g = cf.FieldList(f).mask_invalid(i=True)
    #--- End: def
    
#--- End: class

if __name__ == '__main__':
    print 'cf-python version:'     , cf.__version__
    print 'cf-python path:'        , os.path.abspath(cf.__file__)
    print''
    unittest.main(verbosity=2)
