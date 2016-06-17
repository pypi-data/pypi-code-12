import tempfile
import cf
import os
import unittest
import atexit
import numpy

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

class read_writeTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]
    original_chunksize = cf.CHUNKSIZE()

    def test_read_select(self):
        # select on field list
        f = cf.read(self.filename, select='eastward_wind')
        g = cf.read(self.filename)
        self.assertTrue(f.equals(g, traceback=True),
                        'Bad read with select keyword')
    #--- End: def

    def test_read_top_level(self):
        # Test top_level keyword of cf.read
        filename = self.filename
        self.assertTrue(len(cf.read(filename)) == 1)
        self.assertTrue(len(cf.read(filename, top_level=['dimension'])) == 6)
        self.assertTrue(len(cf.read(filename, top_level=['auxiliary'])) == 11)
        self.assertTrue(len(cf.read(filename, top_level='measure')) == 4)
        self.assertTrue(len(cf.read(filename, top_level=['ancillary'])) == 5)
        self.assertTrue(len(cf.read(filename, top_level='reference')) == 2)
        self.assertTrue(len(cf.read(filename, top_level='field')) == 6)
        self.assertTrue(len(cf.read(filename, top_level=['ancillary', 'auxiliary'])) == 15)
        self.assertTrue(len(cf.read(filename, top_level=['reference', 'auxiliary'])) == 12)
        self.assertTrue(len(cf.read(filename, top_level=['field', 'auxiliary'])) == 16)
        self.assertTrue(len(cf.read(filename, top_level=['field', 'measure', 'auxiliary'])) == 19)
        self.assertTrue(len(cf.read(filename, top_level='coordinate')) == 16)
        self.assertTrue(len(cf.read(filename, top_level='all')) == 24)
        self.assertTrue(len(cf.read(filename, top_level=('field', 'measure', 'coordinate'))) == 24)
    #--- End: def

    def test_read_write_format(self):
        # No compression
        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
            f = cf.read(self.filename)[0]
            for fmt in ('NETCDF3_CLASSIC',
                        'NETCDF3_64BIT',
                        'NETCDF4',
                        'NETCDF4_CLASSIC',
                        'CFA3', 
                        'CFA4'):
                cf.write(f, tmpfile, fmt=fmt)
                g = cf.read(tmpfile)[0]
                self.assertTrue(f.equals(g, traceback=True),
                                'Bad read/write of format: {0}'.format(fmt))
        #--- End: for
    #--- End: def

    def test_read_write_netCDF4_compress_shuffle(self):
        # Compression
        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
            f = cf.read(self.filename)[0]
            for fmt in ('NETCDF4',
                        'NETCDF4_CLASSIC',
                        'CFA4'):
                for no_shuffle in (True, False):
                    for compress in range(10):
                        cf.write(f, tmpfile, fmt=fmt,
                                 compress=compress,
                                 no_shuffle=no_shuffle)
                        g = cf.read(tmpfile)[0]
                        self.assertTrue(
                            f.equals(g, traceback=True),
                            'Bad read/write with lossless compression: {0}, {1}, {2}'.format(fmt, compress, no_shuffle))
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize) 
    #--- End: def

    def test_write_datatype(self):
#        if self.test_only and inspect.stack()[0][3] not in self.test_only:
#            return

        # Compression
        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
            f = cf.read(self.filename)[0] 
            self.assertTrue(f.dtype == numpy.dtype(float))
            cf.write(f, tmpfile, fmt='NETCDF4', 
                     datatype={numpy.dtype(float): numpy.dtype('float32')})
            g = cf.read(tmpfile)
            self.assertTrue(g.dtype == numpy.dtype('float32'), 
                            'datatype read in is '+str(g.dtype))
#--- End: class

if __name__ == "__main__":
    print 'cf-python version:', cf.__version__
    print 'cf-python path:'   , os.path.abspath(cf.__file__)
    print ''
    unittest.main(verbosity=2)
