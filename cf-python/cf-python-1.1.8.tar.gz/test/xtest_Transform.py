import cf
import numpy
import os
import unittest

class TransformTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]

    def test_Transform_equals(self):
        f = cf.read(self.filename)[0]
        
        t = cf.Transform(name='atmosphere_hybrid_height_coordinate',
                         a='aux0', b='aux1', orog=f,
                         coord_terms=('a', 'b'))
        #        print t.dump(complete=True)
        #        print t
        #        t.inspect()
        #        print
        self.assertTrue(t.equals(t.copy(), traceback=True))
        
        # Create a rotated_latitude_longitude grid mapping transform
        t = cf.Transform(name='rotated_latitude_longitude',
                         grid_north_pole_latitude=38.0,
                         grid_north_pole_longitude=190.0)
        #        print t.dump(complete=True)
        #        print t
        #        t.inspect()
        #        print
        self.assertTrue(t.equals(t.copy(), traceback=True))
    #--- End: def
#--- End: class

if __name__ == '__main__':
    print 'cf-python version:', cf.__version__
    print 'cf-python path:'   , os.path.abspath(cf.__file__)
    print ''
    unittest.main(verbosity=2)

  
