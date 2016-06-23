import tempfile
import os
import sys
import numpy
import cf


#cf.CONSTANTS['FM_THRESHOLD'] = 100000000000000000000

import atexit

'''
Tests for the cf package.

'''

tmpfile  = tempfile.mktemp('.nc')
tmpfile2 = tempfile.mktemp('.nca')
tmpfiles = [tmpfile, tmpfile2]
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

print '\n--------------------------------------------------------------------'
print 'TEST: Set chunk size:'

# Save original chunksize
original_chunksize = cf.CHUNKSIZE()

cf.CHUNKSIZE(60)
print 'CHUNKSIZE reset to',cf.CHUNKSIZE()

print '\n--------------------------------------------------------------------'
print "TEST: Create a field:"

# Dimension coordinates
dim0 = cf.Coordinate(data=cf.Data(numpy.arange(10.), 'degrees'))
dim0.standard_name = 'grid_latitude'
 
dim1 = cf.Coordinate(data=cf.Data(numpy.arange(9.) + 20, 'degrees'))
dim1.standard_name = 'grid_longitude'
dim1.Data[-1] += 5
bounds = cf.Data(numpy.array([dim1.Data.array-0.5, dim1.Data.array+0.5]).transpose((1,0)))
bounds[-2,1] = 30
bounds[-1,:] = [30, 36]
dim1.insert_bounds(cf.CoordinateBounds(data=bounds))

dim2 = cf.Coordinate(data=cf.Data(1.5), bounds=cf.Data([1, 2.]))
dim2.standard_name = 'atmosphere_hybrid_height_coordinate'

# Auxiliary coordinates
aux0 = cf.Coordinate(data=cf.Data(10., 'm'))
aux0.id = 'atmosphere_hybrid_height_coordinate_ak'
aux0.insert_bounds(cf.Data([5, 15.], aux0.Units))

aux1 = cf.Coordinate(data=cf.Data(20.))
aux1.id = 'atmosphere_hybrid_height_coordinate_bk'
aux1.insert_bounds(cf.Data([14, 26.]))

aux2 = cf.Coordinate(data=cf.Data(numpy.arange(-45, 45, dtype='int32').reshape(10, 9),
                                  units='degree_N'))
aux2.standard_name = 'latitude'

aux3 = cf.Coordinate(
    data=cf.Data(numpy.arange(60, 150, dtype='int32').reshape(9, 10),
                 units='degreesE'))
aux3.standard_name = 'longitude'

# Cell measures
cm0 = cf.CellMeasure(data=cf.Data(numpy.arange(90.).reshape(9, 10)*1234, 'km 2'))
cm0.measure = 'area'

# Transforms
trans0 = cf.Transform(name='rotated_latitude_longitude',
                      grid_north_pole_latitude=38.0,
                      grid_north_pole_longitude=190.0)

# Data          
data = cf.Data(numpy.arange(90.).reshape(10, 9), 'm s-1')

# Domain
domain = cf.Domain(dim=(dim0, dim1, dim2),
                   aux=[aux0, aux1, aux2, aux3],
                   cm={'cm0': cm0},
                   trans=(trans0,),
                   assign_axes={'aux0': ['dim2'],
                                'aux1': ['dim2'],
                                'aux3': ['dim1', 'dim0'],
                                'cm0' : ['dim1', 'dim0']})

properties = {'standard_name': 'eastward_wind'}

f = cf.Field(properties=properties, domain=domain, data=data) 
orog = f.copy()
orog.standard_name = 'surface_altitude'
orog.insert_data(cf.Data(f.array*2, 'm'))
#orog.Data = cf.Data(f.array*2, 'm')
orog.squeeze()
#orog.domain.squeeze('dim2')
orog.remove_axes('dim2')
orog.transpose([1, 0], i=True)
#orog.finalize()
t = cf.Transform(name='atmosphere_hybrid_height_coordinate',
                 a='aux0', b='aux1', orog=orog,
                 coord_terms=('a', 'b'))
print t.inspect

assert(t.equals(t, traceback=True))
    
#if not t.equals(t, traceback=True):
#    raise RuntimeError("Transform is not equal to itself")
#else:
#    print '\nTransform is equal to itself'

f.domain.insert_transform(t)
rt = f.item('atmosphere_hybrid_height_coordinate', role='t')
print rt.inspect()
print  "f.item('atmosphere_hybrid_height_coordinate', role='t').coords=",rt.coords

print  f.Data.dumpd()
f.dump(complete=1)
print '\nf.items() =',f.items()
print '\nf.axes() =',f.axes()

#print (f.array == 9)

# Ancillary variables
tmp = f.copy()
print  str(f)
print '+++++++++'
print repr(tmp.item('atmosphere_hybrid_height_coordinate', exact=True))
#del tmp.item('atmosphere_hybrid_height_coordinate', exact=True).transforms
tmp.remove_items(role='t') #transforms()
tmp.remove_item('aux0') #aux('aux0')
tmp.remove_item('atmosphere_hybrid_height_coordinate_bk')

f.ancillary_variables = cf.AncillaryVariables()

print 'ANCILLARY 0'
g = tmp.copy()
g.transpose([1,0], i=True)
g.standard_name = 'ancillary0'
g *= 0.01
g.remove_axes(g.axes().difference(g.data_axes()))
f.ancillary_variables.append(g) 
print g

print 'ANCILLARY 1'
g = tmp.copy()
#g.domain.squeeze('dim2')
print g
#g.remove_axes('dim2')
g.standard_name = 'ancillary1'
g *= 0.01
print g
g.remove_axes(g.axes().difference(g.data_axes()))
g.remove_item('atmosphere_hybrid_height_coordinate', role='t')
f.ancillary_variables.append(g) 

g.dump(complete=1)
#sys.exit(0)

print 'ANCILLARY 2'
g = tmp.copy()
print g
print g.domain.dimension_sizes, g.domain.dimensions
g = g.subspace[0]
print g.domain.dimension_sizes, g.domain.dimensions
print g.items()
g.squeeze(i=True)
print g.domain.dimension_sizes, g.domain.dimensions
print
g.standard_name = 'ancillary2'
g *= 0.001
g.remove_axes(g.axes().difference(g.data_axes()))
f.ancillary_variables.append(g)
print g
print g.Data
print g.items()

print 'ANCILLARY 3'
g = tmp.copy()
g = g.subspace[..., 0]
g.squeeze(i=True)
g.standard_name = 'ancillary3'
g *= 0.001
g.remove_axes(g.axes().difference(g.data_axes()))
f.ancillary_variables.append(g)
print g

f.flag_values = [1,2,4]
f.flag_meanings = ['a', 'bb', 'ccc']

print '||||||||||||||||'
print f.domain.dimension_sizes
print f.domain.dimensions
print
f.dump(complete=1)
print '--------------------------------------------||||||||||||||||'

print '\n--------------------------------------------------------------------'
print 'TEST: Print a dump of the field:'
print repr(f)

f.dump()

print '\n--------------------------------------------------------------------'
print 'TEST: Print CF properties:'
print f.properties

print '\n--------------------------------------------------------------------'
print "TEST: Shape of the partition array:"
print '(pndim, psize, pshape) =', (f.Data.partitions.ndim,
                                   f.Data.partitions.size,
                                   f.Data.partitions.shape)

f.cell_methods = cf.CellMethods('grid_longitude: mean grid_latitude: max')


print '\n--------------------------------------------------------------------'
print 'TEST: Write the field to disk:'
print 'tmpfile=', tmpfile
f.dump(complete=1)
f.dump()
print f
cf.write(f, tmpfile)
print 'tmpfile=', tmpfile
f.dump(complete=1)
print 'tmpfile=', tmpfile

print '\n--------------------------------------------------------------------'
print 'TEST: Read the field from disk:'
print f
g = cf.read(tmpfile, squeeze=True)[0]
print g
print 'tmpfile=', tmpfile
try:
    del g.history
except AttributeError:
    pass

g.dump()

print '\n-------------------------------------------------------------------'
print '\nComparison (set)'
c = cf.Comparison('set', [0,3,4,5])
print c
a = (f == c)
print repr(a)
print a.array

print '\n--------------------------------------------------------------------'
print "TEST: Check the equality function:"
assert(cf.equals(g, g.copy(), traceback=True))
print "Field is equal to a copy of itself"

print f
print g
print 'tmpfile=', tmpfile
print  f.ancillary_variables[1]
print  g.ancillary_variables[1]
f.dump(complete=1)
assert(cf.equals(f, g, traceback=True))
print "Field is equal to itself read back in"

print '\n--------------------------------------------------------------------'
# +, -, *, /, **
h = g.copy()
h **= 2
h **= 0.5
h *= 10
h /= 10.
h += 100
h -= 100
h = h ** 3
h = h ** (1/3.)
h = h * 1000
h = h / 1000.
h = h + 10000
h = h - 10000
assert(cf.equals(g, h, traceback=True))
print "Field +, -, *, / and ** passed"

print '\n--------------------------------------------------------------------'
print "TEST: Operators on a field list:"
h = g.copy()
h.override_units('m')
gl = cf.FieldList([h.copy(), h.copy()])
gl += 2

print '       ', gl[1].datum(-1)
x = 2 #.0
y = gl   + x
print '  +',x,':', y[1].datum(-1)
y = gl   * x
print '  *',x,':', y[1].datum(-1)
y = gl   - x
print '  -',x,':', y[1].datum(-1)
y = gl   / x
print '  /',x,':', y[1].datum(-1)
y = gl  // x
print ' //',x,':', y[1].datum(-1)
y = gl  ** int(x)
print ' **',int(x),':', y[1].datum(-1)

y = x  + gl
print x, '  +',':', y[1].datum(-1)
y = x  * gl
print x, '  *',':', y[1].datum(-1)
y = x - gl
print x, '  -',':', y[1].datum(-1)
y = x  / gl
print x, '  /',':', y[1].datum(-1)
y = x // gl
print x, ' //',':', y[1].datum(-1)
#y = x ** gl
#print x, ' **',':', y[1].datum(-1)

y = gl.copy()
y += x
print ' +=',x,':', y[1].datum(-1)
y = gl.copy()
y *= x
print ' *=',x,':', y[1].datum(-1)
y = gl.copy()
y -= x
print ' -=',x,':', y[1].datum(-1)
y = gl.copy()
y /= x
print ' /=',x,':', y[1].datum(-1)
y = gl.copy()
y //= x
print '//=',x,':', y[1].datum(-1)
y = gl.copy()
y **= int(x)
print '**=',int(x),':', y[1].datum(-1)

y = gl.__truediv__(x)
print ' __truediv__(',x,'):', y[1].datum(-1)
y = gl.__rtruediv__(x)
print '__rtruediv__(',x,'):', y[1].datum(-1)
y = gl.copy()
y.__itruediv__(x)
print '__itruediv__(',x,'):', y[1].datum(-1)

y = gl   > x
print '  >',x,':', y[1].datum(-1)
y = gl  >= x
print ' >=',x,':', y[1].datum(-1)
y = gl   < x
print '  <',x,':', y[1].datum(-1)
y = gl  <= x
print ' <=',x,':', y[1].datum(-1)
y = gl  == x
print ' ==',x,':', y[1].datum(-1)
y = gl  != int(x)
print ' !=',int(x),':', y[1].datum(-1)

y = abs(gl)
print 'abs','  :', y[1].datum(-1)
y = -gl
print '  -','  :', y[1].datum(-1)
y = +gl
print '  +','  :', y[1].datum(-1)
#y = ~gl
#print ' ~','  :', y[1].datum(-1)

gl.dtype = int

y =  gl  & x
print '  &',int(x),':', y[1].datum(-1)
y =  gl  | x               
print '  |',int(x),':', y[1].datum(-1)
y =  gl  ^ x               
print '  ^',int(x),':', y[1].datum(-1)
y =  gl << x               
print ' <<',int(x),':', y[1].datum(-1)
y =  gl >> x               
print ' >>',int(x),':', y[1].datum(-1)
                           
y =  x   & gl              
print int(x),'  &',':', y[1].datum(-1)
y =  x   | gl              
print int(x),'  |',':', y[1].datum(-1)
y =  x  ^ gl               
print int(x),'  ^',':', y[1].datum(-1)
y =  x << gl               
print int(x),' <<',':', y[1].datum(-1)
y =  x >> gl               
print int(x),' >>',':', y[1].datum(-1)
                                
y = gl.copy()                   
y       &= x                    
print ' &=',int(x),':', y[1].datum(-1)
y = gl.copy()
y       |= x
print ' |=',int(x),':', y[1].datum(-1)
y = gl.copy()
y       ^= x
print ' ^=',int(x),':', y[1].datum(-1)

#sys.exit(0)

print '\n--------------------------------------------------------------------'
print "TEST: tranpose, flip, expand_dims, squeeze and remove_axes:"
h = g.copy()
h.transpose((1, 0), i=True)
h.transpose((1, 0), i=True)
h.transpose(('grid_longitude', 'grid_latitude'), i=True)
h.transpose(('grid_latitude', 'grid_longitude'), i=True)
assert(cf.equals(g, h, traceback=True))
print "Tranpose of field passed"

h.flip((1, 0), i=True)
h.flip((1, 0), i=True)
h.flip(0, i=True)
h.flip(1, i=True)
h.flip([0, 1], i=True)
assert(cf.equals(g, h, traceback=True))
print "Flipping field axes passed"

#axisA = h.expand_dims()
#axisB = h.expand_dims()
#h.remove_axes([axisA, axisB])
#assert(cf.equals(g, h, traceback=True))
#print "Field expand_dims, squeeze and remove_axes passed"

print '\n--------------------------------------------------------------------'
print "TEST: Access the field's data as a numpy array:"
print g.array

print '\n--------------------------------------------------------------------'
print "TEST: Access the field's coordinates' data arrays:"
print 'grid_latitude :', g.item('lat').array
print 'grid_longitude:', g.item('lon').array

print '\n--------------------------------------------------------------------'
print 'TEST: Subspace the field (1):'
print g.subspace[..., 2:5].array

print '\n--------------------------------------------------------------------'
print 'TEST: Subspace the field (2):'
print g.subspace[9::-4, ...].array

print '\n--------------------------------------------------------------------'
print 'TEST: Subspace the field (3):'
h = g.subspace[(slice(None, None, -1),) * g.ndim]
print '\n\n\n\@AND BACK\n\n\n\n'
h.dump(complete=1)
h = h.subspace[(slice(None, None, -1),) * h.ndim]
print g
print h
g.dump(complete=1)
assert(g.equals(h, traceback=True))

print '\n--------------------------------------------------------------------'
print 'TEST: Indices for a subspace defined by coordinates:'
print f.indices()
print f.indices(grid_lat=cf.lt(5), grid_lon=27)
print f.indices('exact', 
                grid_latitude=cf.lt(5), grid_longitude=27,
                atmosphere_hybrid_height_coordinate=1.5)

print '\n--------------------------------------------------------------------'
print 'TEST: Subspace the field:'
print g.subspace(grid_latitude=cf.lt(5), grid_longitude=27, atmosphere_hybrid_height_coordinate=1.5)

print '\n--------------------------------------------------------------------'
print 'TEST: Create list of fields:'
fl = cf.FieldList([g, g, g, g])

print '\n--------------------------------------------------------------------'
print 'TEST: Write a list of fields to disk:'
cf.write((f, fl), tmpfile)
cf.write(fl, tmpfile)

print '\n--------------------------------------------------------------------'
print 'TEST: Read a list of fields from disk:'
fl = cf.read(tmpfile, squeeze=True)
try:
    fl.delattr('history')
except AttributeError:
    pass

print repr(fl)

print '\n--------------------------------------------------------------------'
print 'TEST: Print all fields in the list:'
print fl

print '\n--------------------------------------------------------------------'
print 'TEST: Print the last field in the list:'
print fl[-1]

print '\n--------------------------------------------------------------------'
print 'TEST: Print the data of the last field in the list:'
print fl[-1].array

print '\n--------------------------------------------------------------------'
print 'TEST: Modify the last field in the list:'
fl[-1] *= -1
print fl[-1].array

print '\n--------------------------------------------------------------------'
print 'TEST: Changing units\n:'
fl[-1].units = 'mm.s-1'
print fl[-1].array

print '\n--------------------------------------------------------------------'
print 'TEST: Combine fields not in place:'
g = fl[-1] - fl[-1]
print g.array

print '\n--------------------------------------------------------------------'
print 'TEST: Combine field with a size 1 Data object:'
g += cf.Data([[[[[1.5]]]]], 'cm.s-1')
print g.array
g.dump()
print '\n--------------------------------------------------------------------'
print "TEST: Setting data array elements to a scalar with subspace[]:"
g.subspace[...] = 0
print g
g.subspace[3:7, 2:5] = -1
print g.array,'\n'
g.subspace[6:2:-1, 4:1:-1] = numpy.array(-1)
print g.array,'\n'
g.subspace[[0, 3, 8], [1, 7, 8]] = numpy.array([[[[-2]]]])
print g.array,'\n'
g.subspace[[8, 3, 0], [8, 7, 1]] = cf.Data(-3, None)
print g.array,'\n'
g.subspace[[7, 4, 1], slice(6, 8)] = [-4]
print g.array

print '\n--------------------------------------------------------------------'
print "TEST: Setting of (un)masked elements with setdata():"
g.subspace[::2, 1::2] = numpy.ma.masked
print g.array,'\n'
g.Data.to_memory(1)
print g.Data.partitions[0][1].subarray
g.setdata(99, None)
print g.array,'\n'
g.Data.to_memory(1)
print g.Data.partitions[0][1].subarray
g.setdata(2, None, g.mask)   # Softern?
print g.array,'\n'
g.Data.to_memory(1)
print g.Data.partitions[0][1].subarray
print '\n--------------'

g.subspace[slice(None, None, 2), slice(1, None, 2)] = cf.masked
print g.array,'\n'
g.Data.to_memory(1)
print g.Data.partitions[0][1].subarray
g.setdata([[-1]], None, g.mask)
print g.array,'\n'
g.Data.to_memory(1)
print g.Data.partitions[0][1].subarray
g.setdata(cf.Data(0, None), None)
print g.array,'\n'
g.Data.to_memory(1)
print g.Data.partitions[0][1].subarray

h = g.subspace[:3, :4]
h.setdata(-1, None)
h.subspace[0, 2] = 2
h.dump()
print h.array
h.transpose([1, 0], i=True)
print h.array

h.flip([1, 0], i=True)
print h.array, h.shape
print h
print g.subspace[slice(None, 3), slice(None, 4)], g.subspace[slice(None, 3), slice(None, 4)].shape

print 'AA', g.shape, g.subspace[slice(None, 3), slice(None, 4)].shape


g.subspace[slice(None, 3), slice(None, 4)] = h

h = g.subspace[:3, :4]
h.subspace[...] = -1
h.subspace[0, 2] = 2
g.subspace[slice(None, 3), slice(None, 4)] = h
print g.array

print '\n--------------------------------------------------------------------'
print "TEST: Make sure all partitions' data are in temporary files:"
g.Data.to_disk()
print g.Data.partitions
#sys.exit(0)

print '\n--------------------------------------------------------------------'
print "TEST: Push partitions' data from temporary files into memory:"
g.Data.to_memory(regardless=True)
print g.Data.partitions

print '\n--------------------------------------------------------------------'
print g.Data.partitions
print "TEST: Push partitions' data from memory to temporary files:"
g.Data.to_disk()
print g.Data.partitions

print '\n--------------------------------------------------------------------'
print "TEST: Iterate through array values:"
for x in f.Data.flat():
    print x,
print

print '\n--------------------------------------------------------------------'
print 'TEST: Reset chunk size:'
cf.CHUNKSIZE(original_chunksize)
print 'CHUNKSIZE reset to',cf.CHUNKSIZE()

print '\n--------------------------------------------------------------------'
print 'TEST: Move Data partitions to disk:'
f.Data.to_disk()
print f.Data.dumpd()

print '\n--------------------------------------------------------------------'
print 'TEST: Create a CFA file ('+tmpfile2+'):'
cf.write(f, tmpfile2, fmt='CFA4')
cf.write(f, tmpfile2, fmt='CFA3')
print 'OK'

print '\n--------------------------------------------------------------------'
print 'TEST: Read the CFA file ('+tmpfile2+'):'
n = cf.read(tmpfile2, squeeze=True)[0]
print repr(n)

if not cf.equals(f, n, traceback=True):
    raise RuntimeError("Field is not equal to itself read back in from CFA file")
print 'OK'

cf.CHUNKSIZE(original_chunksize)
print f

f.transpose(i=True)
f.flip(i=True)

print  f.Data.dumpd()
cf.write(f, 'delme.nc')
print f
f = cf.read('delme.nc')[0]

print f
print '########################################'
print  f.Data.dumpd()
cf.write(f, 'delme.nca', fmt='CFA4')
g = cf.read('delme.nca')[0]
print g

f.aux('aux0').id = 'atmosphere_hybrid_height_coordinate_ak'
f.aux('aux1').id = 'atmosphere_hybrid_height_coordinate_bk'


b = f.subspace[:,0:6,:]
c = f.subspace[:,6:,:]
print '-----------------------'
print f
print b
print c

d = cf.aggregate([b, c], info=1)[0]

print d



print '\n--------------------------------------------------------------------'
print "TEST: Remove temporary files:"
cf.data.partition._remove_temporary_files()

cf.CHUNKSIZE(original_chunksize)

f.dump(complete=1)
