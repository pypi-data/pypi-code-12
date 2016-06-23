import cf
import numpy

#---------------------------------------------------------------------
# 1. Create the field's domain items
#---------------------------------------------------------------------
# Create a grid_latitude dimension coordinate
dim0 = cf.DimensionCoordinate(properties={'standard_name': 'grid_latitude'},
                              data=cf.Data(numpy.arange(10.), 'degrees'))

# Create a grid_longitude dimension coordinate
dim1 = cf.DimensionCoordinate(data=cf.Data(numpy.arange(9.), 'degrees'))
dim1.standard_name = 'grid_longitude'

# Create a time dimension coordinate (with bounds)
bounds = cf.CoordinateBounds(
data=cf.Data([0.5, 1.5], cf.Units('days since 2000-1-1', calendar='noleap')))
dim2 = cf.DimensionCoordinate(properties=dict(standard_name='time'),
                              data=cf.Data(1, cf.Units('days since 2000-1-1',
                                                       calendar='noleap')),
                              bounds=bounds)

# Create a longitude auxiliary coordinate
aux0 = cf.AuxiliaryCoordinate(data=cf.Data(numpy.arange(90).reshape(10, 9),
                                           'degrees_north'))
aux0.standard_name = 'latitude'

# Create a latitude auxiliary coordinate
aux1 = cf.AuxiliaryCoordinate(properties=dict(standard_name='longitude'),
                              data=cf.Data(numpy.arange(1, 91).reshape(9, 10),
                                           'degrees_east'))

# Create a rotated_latitude_longitude grid mapping transform
trans0 = cf.Transform(grid_mapping_name='rotated_latitude_longitude',
                      grid_north_pole_latitude=38.0,
                      grid_north_pole_longitude=190.0)

# --------------------------------------------------------------------
# 2. Create the field's domain from the previously created items
# --------------------------------------------------------------------
domain = cf.Domain(dim=[dim0, dim1, dim2],
                   aux=[aux0, aux1],
                   trans=trans0,
                   assign_axes={'aux1': ['dim1', 'dim0']})

#---------------------------------------------------------------------
# 3. Create the field
#---------------------------------------------------------------------
# Create CF properties
properties = {'standard_name': 'eastward_wind',
              'long_name'    : 'East Wind',
              'cell_methods' : cf.CellMethods('latitude: point')}

# Create the field's data array
data = cf.Data(numpy.arange(90.).reshape(9, 10), 'm s-1')

# Finally, create the field
f = cf.Field(properties=properties,
             domain=domain,
             data=data,
             axes=domain.axes(['grid_long', 'grid_lat'], ordered=True))

print "The new field:\n"
print f
