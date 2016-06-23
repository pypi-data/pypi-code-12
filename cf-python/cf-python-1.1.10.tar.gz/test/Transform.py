import cf
import numpy
import os
import time

def test():
    start_time = time.time()
    print '----------------------------------------------------------'
    print 'cf.Transform'
    print '----------------------------------------------------------'

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "test_file.nc")
    f = cf.read(filename)[0]

    t = cf.Transform(name='atmosphere_hybrid_height_coordinate',
                     a='aux0', b='aux1', orog=f,
                     coord_terms=('a', 'b'))
    print t.dump(complete=True)
    print t
    t.inspect()
    print
    assert t.equals(t.copy(), traceback=True), "Transform not equal to itself"

    # Create a rotated_latitude_longitude grid mapping transform
    t = cf.Transform(name='rotated_latitude_longitude',
                     grid_north_pole_latitude=38.0,
                     grid_north_pole_longitude=190.0)
    print t.dump(complete=True)
    print t
    t.inspect()
    print
    assert t.equals(t.copy(), traceback=True), "Transform not equal to itself"

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All cf.Transform tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------' 
    print
#--- End: def

if __name__ == "__main__":
    test()
