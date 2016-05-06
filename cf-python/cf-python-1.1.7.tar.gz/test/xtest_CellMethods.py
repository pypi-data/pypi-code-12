import cf
import os
import unittest

class CellMethodsTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]
    original_chunksize = cf.CHUNKSIZE()

    def test_CellMethods___str__(self):
        for s in ("t: mean",
                  "time: point",
                  "time: maximum",
                  "time: sum",
                  "lon: maximum time: mean"
                  "time: mean lon: maximum",
                  "lat: lon: standard_deviation",
                  "lon: standard_deviation lat: standard_deviation",
                  "time: standard_deviation (interval: 1 day)",
                  "area: mean",
                  "lon: lat: mean",
                  "lat: lon: standard_deviation (interval: 0.1 degree_N interval: 0.2 degree_E)",
                  "time: variance (interval: 1 hr comment: sampled instantaneously)",
                  'time: mean',
                  'time: mean time: maximum',
                  'time: mean within years time: maximum over years',
                  'time: mean within days time: maximum within years time: variance over years',
                  "time: standard_deviation (interval: 1 day)",
                  "time: standard_deviation (interval: 1 year)",
                  "lat: lon: standard_deviation (interval: 10 km)",
                  "lat: lon: standard_deviation (interval: 0.1 degree_N interval: 0.2 degree_E)",
                  "lat: mean (area-weighted) or lat: mean (interval: 1 degree_north comment: area-weighted)",
                  "time: variance (interval: 1 hr comment: sampled instantaneously)",
                  "area: mean where land",
                  "area: mean where land_sea",
                  "area: mean where sea_ice over sea",
                  "area: mean where sea_ice over sea",
                  "time: minimum within years time: mean over years",
                  "time: sum within years time: mean over years",
                  "time: mean within days time: mean over days",
                  "time: minimum within days time: sum over days",
                  "time: minimum within days time: maximum over days",
                  "time: mean within days",
                  "time: sum within days time: maximum over days"
                  ):
            cm = cf.CellMethods(s)
            self.assertTrue(str(cm) == s, 'Problem with input string: %r' % s)
    #--- End: def

#--- End: class

if __name__ == '__main__':
    print 'cf-python version:', cf.__version__
    print 'cf-python path:'   , os.path.abspath(cf.__file__)
    print ''
    unittest.main(verbosity=2)
