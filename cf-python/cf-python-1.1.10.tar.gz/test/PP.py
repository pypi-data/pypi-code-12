import cf
import numpy
import os
import tempfile
import time

def test(chunk_sizes=(17, 34, 60, 300, 100000)):
    start_time = time.time()

    print '----------------------------------------------------------'
    print 'WGDOS packed PP data'
    print '----------------------------------------------------------'
    tmpfile = tempfile.mktemp('.test_cf-python')
    print 'tmpfile =', tmpfile

    original_chunksize = cf.CHUNKSIZE()

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "wgdos_packed.pp")

    cf.CHUNKSIZE(10000000)
    f = cf.read(filename)[0]

    assert f.data.min() > 221.71, "Bad unpacking of WGDOS packed data"
    assert f.data.max() < 310.45, "Bad unpacking of WGDOS packed data"

    array = f.array

    for chunksize in chunk_sizes[::-1]:

        cf.CHUNKSIZE(chunksize)

        f = cf.read(filename)[0]
        print 'pmshape =',f.data._pmshape, 'chunksize =', chunksize    

        for fmt in ('CFA4', 'NETCDF4'):
            cf.write(f, tmpfile, fmt=fmt)
            assert f.equals(cf.read(tmpfile)[0], traceback=True), \
                'Bad writing/reading. format='+fmt
        #--- End: for

        assert (f.array == array).all(), "Bad unpacking of WGDOS packed data"
    #--- End: for

    # Reset chunk size
    cf.CHUNKSIZE(original_chunksize)

    # Remove temporary file
    os.remove(tmpfile)

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All cf.pp tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------' 
    print
#--- End: def

if __name__ == "__main__":
    test()
