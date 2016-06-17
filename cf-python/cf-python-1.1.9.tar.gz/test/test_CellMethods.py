import cf
import os
import unittest

class CellMethodsTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]
    original_chunksize = cf.CHUNKSIZE()

    strings = ('t: mean',
               'time: point',
               'time: maximum',
               'time: sum',
               'lon: maximum time: mean',
               'time: mean lon: maximum',
               'lat: lon: standard_deviation',
               'lon: standard_deviation lat: standard_deviation',
               'time: standard_deviation (interval: 1 day)',
               'area: mean',
               'lon: lat: mean',
               'time: variance (interval: 1 hr comment: sampled instantaneously)',
               'time: mean',
               'time: mean time: maximum',
               'time: mean within years time: maximum over years',
               'time: mean within days time: maximum within years time: variance over years',
               'time: standard_deviation (interval: 1 day)',
               'time: standard_deviation (interval: 1 year)',
               'time: standard_deviation (interval: 30 year)',
               'time: standard_deviation (interval: 1.0 year)',
               'time: standard_deviation (interval: 30.0 year)',
               'lat: lon: standard_deviation (interval: 10 km)',
               'lat: lon: standard_deviation (interval: 10 km interval: 10 km)',
               'lat: lon: standard_deviation (interval: 0.1 degree_N interval: 0.2 degree_E)', 
               'lat: lon: standard_deviation (interval: 0.123 degree_N interval: 0.234 degree_E)',
               'time: variance (interval: 1 hr comment: sampled instantaneously)',
               'area: mean where land',
               'area: mean where land_sea',
               'area: mean where sea_ice over sea',
               'area: mean where sea_ice over sea',
               'time: minimum within years time: mean over years',
               'time: sum within years time: mean over years',
               'time: mean within days time: mean over days',
               'time: minimum within days time: sum over days',
               'time: minimum within days time: maximum over days',
               'time: mean within days',
               'time: sum within days time: maximum over days',
           )

    def test_CellMethods___str__(self):
        for s in self.strings:
            cm = cf.CellMethods(s)           
            self.assertTrue(str(cm) == s, '%r != %r' % (s, str(cm)))
    #--- End: def

    def test_CellMethods_equals(self):
        for s in self.strings:
            cm0 = cf.CellMethods(s)
            cm1 = cf.CellMethods(s)
            self.assertTrue(cm0.equals(cm1, traceback=True),
                            '%r != %r' % (cm0, cm1))
        #--- End: for
    #--- End: def

    def test_CellMethods_equivalent(self):
        for s in self.strings:
            cm0 = cf.CellMethods(s)
            cm1 = cf.CellMethods(s)
            self.assertTrue(cm0.equivalent(cm1),
                            '%r not equivalent to %r' % (cm0, cm1))
        #--- End: for

        # Intervals
        for s0, s1 in (
                ['lat: lon: mean (interval: 10 km)',
                 'lat: lon: mean (interval: 10 km)'],
                ['lat: lon: mean (interval: 10 km)',
                 'lat: lon: mean (interval: 10 km interval: 10 km)'],
                ['lat: lon: mean (interval: 10 km interval: 10 km)',
                 'lat: lon: mean (interval: 10 km interval: 10 km)'],
                ['lat: lon: mean (interval: 20 km interval: 10 km)',
                 'lat: lon: mean (interval: 20 km interval: 10 km)'],  
                ['lat: lon: mean (interval: 20 km interval: 10 km)',
                 'lat: lon: mean (interval: 20000 m interval: 10000 m)'],  

                ['lat: lon: mean (interval: 10 km)',
                 'lon: lat: mean (interval: 10 km)'],
                ['lat: lon: mean (interval: 10 km)',
                 'lon: lat: mean (interval: 10 km interval: 10 km)'],
                ['lat: lon: mean (interval: 10 km interval: 10 km)',
                 'lon: lat: mean (interval: 10 km interval: 10 km)'],
                ['lat: lon: mean (interval: 20 km interval: 10 km)',
                 'lon: lat: mean (interval: 10 km interval: 20 km)'],  
                ['lat: lon: mean (interval: 20 km interval: 10 km)',
                 'lon: lat: mean (interval: 10000 m interval: 20000 m)'],  
        ):
            cm0 = cf.CellMethods(s0)
            cm1 = cf.CellMethods(s1)
            self.assertTrue(cm0.equivalent(cm1, traceback=True),
                            '%r not equivalent to %r' % (cm0, cm1))
        #--- End: for
    #--- End: def

#--- End: class

if __name__ == '__main__':
    print 'cf-python version:', cf.__version__
    print 'cf-python path:'   , os.path.abspath(cf.__file__)
    print ''
    unittest.main(verbosity=2)
