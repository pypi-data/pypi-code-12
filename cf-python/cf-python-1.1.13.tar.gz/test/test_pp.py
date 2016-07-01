import cf
import numpy
import os
import tempfile
import time
import unittest
import atexit

tmpfile  = tempfile.mktemp('.cf-python_test')
tmpfiles = [tmpfile]
def _remove_tmpfiles():
    '''
'''
    for f in tmpfiles:
        try:
            os.remove(f)
        except OSError:
            pass
#--- End: def
atexit.register(_remove_tmpfiles)

class ppTest(unittest.TestCase):
    ppfilename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'wgdos_packed.pp')
    chunk_sizes = (17, 34, 300, 100000)[::-1]
    original_chunksize = cf.CHUNKSIZE()

    def test_PP_WGDOS_UNPACKING(self):
#        print 'skipping WGDOS unpacking !!!!!!! ... '
#        return
        cf.CHUNKSIZE(10000000)
        f = cf.read(self.ppfilename)[0]
        
        self.assertTrue(f.data.min() > 221.71,
                        'Bad unpacking of WGDOS packed data')
        self.assertTrue(f.data.max() < 310.45,
                        'Bad unpacking of WGDOS packed data')
        
        array = f.array
    
        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 

            f = cf.read(self.ppfilename)[0]

            for fmt in ('CFA4', 'NETCDF4'):
                cf.write(f, tmpfile, fmt=fmt)
                g = cf.read(tmpfile)[0]

                self.assertTrue((f.array == array).all(),
                                'Bad unpacking of WGDOS packed data')

                self.assertTrue(f.equals(g, traceback=True),
                                'Bad writing/reading. format='+fmt)
        #--- End: for
        original_chunksize = cf.CHUNKSIZE()
    #--- End: def

#--- End: class

if __name__ == '__main__':
    print 'cf-python version:', cf.__version__
    print 'cf-python path:'   , os.path.abspath(cf.__file__)
    print ''
    unittest.main(verbosity=2)
