import cf
import os
import time

def test(chunk_sizes=(17, 34, 60, 300, 100000)):
    start_time = time.time()

    print '----------------------------------------------------------'
    print 'cf.aggregate'
    print '----------------------------------------------------------'

    #import create_field
    
    #f = create_field.test()
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "test_file.nc")
    original_chunksize = cf.CHUNKSIZE()

    cf.CHUNKSIZE(10000000)
    f = cf.read(filename, squeeze=True)[0]
    print f

    f.transform('at').inspect()

    for chunksize in chunk_sizes[::-1]:
        f.aux('aux0').id = 'atmosphere_hybrid_height_coordinate_ak'
        f.aux('aux1').id = 'atmosphere_hybrid_height_coordinate_bk'

        g = cf.FieldList(f.subspace[0])
        g.append(f.subspace[1:3])
        g.append(f.subspace[3])
        g[-1].flip(0, i=True)
        g.append(f.subspace[4:7])
        g[-1].flip(0, i=True)
        g.extend([f.subspace[i] for i in range(7, f.shape[0])])

        g0 = g.copy()

        assert g.equals(g0, traceback=True), "g != itself"
        
        h = cf.aggregate(g, info=1)
        
        assert h[0].shape == (10, 9), 'h[0].shape is '+repr(h[0].shape)

        assert h[0].equals(f, traceback=True), 'asdasds'
        
        assert g.equals(g0, traceback=True), "g != itself after aggregation"
        
        i = cf.aggregate(g, info=1)
        
        assert i.equals(h, traceback=True), "The second aggregation != the first"
        
        assert g.equals(g0, traceback=True), "g != itself after the second aggregation"
        
        i = cf.aggregate(g, info=1, axes='grid_latitude')
        
        assert i.equals(h, traceback=True), "The third aggregation != the first"
        
        assert g.equals(g0, traceback=True), "g !=itself after the third aggregation"
        
        assert i[0].shape == (10,9), 'i[0].shape is '+repr(i[0].shape)    
        
        i = cf.aggregate(g, info=1, axes='grid_latitude', donotchecknonaggregatingaxes=1)
        
        assert i.equals(h, traceback=True), "The fourth aggregation != the first"
        
        assert g.equals(g0, traceback=True), "g != itself after the fourth aggregation"
        
        assert i[0].shape == (10,9), 'i[0].shape is '+repr(i[0].shape)    
    #--- End: for

    print  h

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All aggregation tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------'
#--- End: def

if __name__ == "__main__":
    test()
