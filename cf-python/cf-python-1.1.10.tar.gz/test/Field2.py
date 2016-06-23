import tempfile
import os
import sys
import itertools
from operator import mul
import numpy
import cf
import unittest

class FieldTest(unittest.TestCase):
    print 'cf version', cf.__version__, 'running from', os.path.abspath(cf.__file__)

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]


    def test_Field_anchor(self):        
        for chunksize in self.chunk_sizes:            
            f = cf.read(self.filename)[0]
            f.cyclic('grid_lon', period=16)
            
            for anchor in numpy.arange(-20, 76, 0.5):
                print anchor
                g = f.anchor('grid_lon', anchor)
                x0, x1 = g.coord('grid_lon').array[0:2]
                self.assertTrue(x0 <= anchor < x1,
                                "x0=%s, anchor=%s, x1=%s" % \
                                (x0, anchor, x1))
            #--- End: for    
            print "cf.Field.anchor passed", "pmshape =", f.Data._pmshape
    #--- End: def

    def test_Field_transpose(self): 
        for chunksize in self.chunk_sizes:            
            cf.CHUNKSIZE(chunksize)            
            f = cf.read(self.filename)[0]
            
            h = f.copy()
            h.transpose((1, 2, 0), i=True)
            h.transpose((2, 0, 1), i=True)
            h.transpose(('grid_longitude', 'atmos', 'grid_latitude'), i=True)
            h.transpose(('atmos', 'grid_latitude', 'grid_longitude'), i=True)
            self.assertTrue(cf.equals(f, h, traceback=True),
                            "cf.Field.transpose failed")
            print "cf.Field.tranpose passed", "pmshape =", f.Data._pmshape
    #--- End: def

    def test_Field_match(self):
        '''Test cf.Field.match'''
        f = cf.read(self.filename)[0]
        f.long_name = 'qwerty'
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
            self.assertTrue(f.match(**kwargs), 
                            "f.match(**%s) failed" % kwargs)
            kwargs['inverse'] = not kwargs['inverse']
            self.assertFalse(f.match(**kwargs),
                             "f.match(**%s) failed" % kwargs)
        #--- End: for
        print "cf.Field.match passed"
    #--- End: def

#--- End: class

if __name__ == '__main__':
    unittest.main()
