import cf

import numpy
data = cf.Data(numpy.arange(90.).reshape(10, 9), 'm s-1')
properties = {'standard_name': 'eastward_wind'}
dim0 = cf.DimensionCoordinate(data=cf.Data(range(10), 'degrees_north'),
                              properties={'standard_name': 'latitude'})

dim1 = cf.DimensionCoordinate(data=cf.Data(range(9), 'degrees_east'))
dim1.standard_name = 'longitude'
domain = cf.Domain(dim=[dim0, dim1])
f = cf.Field(properties=properties, data=data, domain=domain)

aux = cf.AuxiliaryCoordinate(data=cf.Data(['alpha','beta','gamma','delta','epsilon',
                                            'zeta','eta','theta','iota','kappa']))
    			       
aux.long_name = 'extra'
print f.items()
f.insert_aux(aux)
f.cell_methods = cf.CellMethods('latitude: point')
f.long_name = 'wind'
print f

print repr(f.remove_item({'long_name': 'extra'}))
del f.cell_methods
print f
