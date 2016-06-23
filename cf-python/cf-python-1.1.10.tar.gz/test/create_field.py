import cf
import numpy
import os

def test():
    print '----------------------------------------------------------'
    print 'Create a field'
    print '----------------------------------------------------------'

    # Dimension coordinates
    dim0 = cf.Coordinate(data=cf.Data(numpy.arange(10.), 'degrees'))
    dim0.standard_name = 'grid_latitude'
     
    dim1 = cf.Coordinate(data=cf.Data(numpy.arange(9.) + 20, 'degrees'))
    dim1.standard_name = 'grid_longitude'
    dim1.Data[-1] += 5
    bounds = cf.Data(numpy.array([dim1.Data.array-0.5, dim1.Data.array+0.5]).transpose((1,0)))
    bounds[-2,1] = 30
    bounds[-1,:] = [30, 36]
    dim1.insert_bounds(cf.Bounds(data=bounds))
    
    dim2 = cf.Coordinate(data=cf.Data(1.5), bounds=cf.Data([1, 2.]))
    dim2.standard_name = 'atmosphere_hybrid_height_coordinate'
    
    # Auxiliary coordinates
    aux0 = cf.Coordinate(data=cf.Data(10., 'm'))
    aux0.id = 'atmosphere_hybrid_height_coordinate_ak'
    aux0.insert_bounds(cf.Data([5, 15.], aux0.Units))
    
    aux1 = cf.Coordinate(data=cf.Data(20.))
    aux1.id = 'atmosphere_hybrid_height_coordinate_bk'
    aux1.insert_bounds(cf.Data([14, 26.]))
    
    aux2 = cf.Coordinate(
        data=cf.Data(numpy.arange(-45, 45, dtype='int32').reshape(10, 9),
                     units='degree_N'))
    aux2.standard_name = 'latitude'
    
    aux3 = cf.Coordinate(
        data=cf.Data(numpy.arange(60, 150, dtype='int32').reshape(9, 10),
                     units='degreesE'))
    aux3.standard_name = 'longitude'
    
    aux4 = cf.AuxiliaryCoordinate(
        data=cf.Data(['alpha','beta','gamma','delta','epsilon',
                      'zeta','eta','theta','iota','kappa']))
    aux4.standard_name = 'greek_letters'
    aux4.subspace[0] = cf.masked


    # Cell measures
    cm0 = cf.CellMeasure(
        data=cf.Data(1+numpy.arange(90.).reshape(9, 10)*1234, 'km 2'))
    cm0.measure = 'area'
    
    # Transforms
    trans0 = cf.Transform(name='rotated_latitude_longitude',
                          grid_north_pole_latitude=38.0,
                          grid_north_pole_longitude=190.0)
                
    # Data          
    data = cf.Data(numpy.arange(90.).reshape(10, 9), 'm s-1')
    
    # Domain
    domain = cf.Domain(dim=(dim0, dim1, dim2),
                       aux=[aux0, aux1, aux2, aux3, aux4],
                       cm={'cm0': cm0},
                       trans=(trans0,),
                       assign_axes={'aux0': ['dim2'],
                                    'aux1': ['dim2'],
                                    'aux4': ['dim0'],
                                    'aux3': ['dim1', 'dim0'],
                                    'cm0' : ['dim1', 'dim0']},
                       )
    
    properties = {'standard_name': 'eastward_wind'}
    
    f = cf.Field(properties=properties, domain=domain, data=data) 
    orog = f.copy()
    orog.standard_name = 'surface_altitude'
    orog.insert_data(cf.Data(f.array*2, 'm'))
    orog.squeeze()
    orog.remove_axes('dim2')
    orog.transpose([1, 0])

    t = cf.Transform(name='atmosphere_hybrid_height_coordinate',
                     a='aux0', b='aux1', orog=orog,
                     coord_terms=('a', 'b'))
                     
    f.domain.insert_transform(t)
    
    # Ancillary variables
    tmp = f.copy()
    tmp.remove_items(role='t')
    tmp.remove_item('aux0')
    tmp.remove_item('atmosphere_hybrid_height_coordinate_bk')
    
    f.ancillary_variables = cf.AncillaryVariables()

    g = tmp.copy()
    g.transpose([1,0])
    g.standard_name = 'ancillary0'
    g *= 0.01
    g.remove_axes(g.axes().difference(g.data_axes()))
    f.ancillary_variables.append(g) 

    g = tmp.copy()
    g.standard_name = 'ancillary1'
    g *= 0.01
    g.remove_axes(g.axes().difference(g.data_axes()))
    f.ancillary_variables.append(g) 
    
    g = tmp.copy()
    g = g.subspace[0]
    g.squeeze()
    g.standard_name = 'ancillary2'
    g *= 0.001
    g.remove_axes(g.axes().difference(g.data_axes()))
    f.ancillary_variables.append(g)
    
    g = tmp.copy()
    g = g.subspace[..., 0]
    g.squeeze()
    g.standard_name = 'ancillary3'
    g *= 0.001
    g.remove_axes(g.axes().difference(g.data_axes()))
    f.ancillary_variables.append(g)
    
    f.flag_values = [1,2,4]
    f.flag_meanings = ['a', 'bb', 'ccc']      

    f.dump(complete=True)
    print f
    print repr(f)

    # Write the file, and read it in
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    cf.write(f, filename)
    g = cf.read(filename, squeeze=True)[0]

    print 'G DUMP ========================================'
    g.dump(complete=True)

    assert g.equals(f, traceback=True), "Field not equal to itself read back in"

    return f

    print
    print '---------------------------------------------------------------------------'
    print 'All field creation tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print '---------------------------------------------------------------------------' 
    print
#--- End: def

if __name__ == "__main__":
    test()
