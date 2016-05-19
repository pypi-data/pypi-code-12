from numpy import empty   as numpy_empty
from numpy import ndarray as numpy_ndarray
from numpy import size    as numpy_size

#from numpy.ma import argmax as numpy_argmax

from itertools import izip

from .functions        import parse_indices
from .coordinatebounds import CoordinateBounds
from .variable         import Variable, SubspaceVariable

from .data.data import Data


# ====================================================================
#
# Coordinate object
#
# ====================================================================

class Coordinate(Variable):
    '''

Base class for a CF dimension or auxiliary coordinate construct.


**Attributes**

===============  ========  ===================================================
Attribute        Type      Description
===============  ========  ===================================================
`!climatology`   ``bool``  Whether or not the bounds are intervals of
                           climatological time. Presumed to be False if unset.
===============  ========  ===================================================

'''
#    def __new__(cls, *args, **kwargs):
#        '''
#
#Called to create a new instance with the `!_cyclic` attribute set to
#True. ``*args`` and ``**kwargs`` are passed to the `__init__` method.
#
#''' 
#        self = super(Coordinate, cls).__new__(Coordinate)
#        self._cyclic = True
#        return self
#    #--- End: def

    def __init__(self, properties={}, attributes={}, data=None, bounds=None,
                 copy=True):
        '''

**Initialization**

:Parameters:

    properties : dict, optional
        Initialize a new instance with CF properties from a
        dictionary's key/value pairs.

    attributes : dict, optional
        Provide the new instance with attributes from a dictionary's
        key/value pairs.

    data : cf.Data, optional
        Provide the new instance with an N-dimensional data array.

    bounds : cf.Data or cf.CoordinateBounds, optional
        Provide the new instance with cell bounds.

    copy : bool, optional
        If False then do not copy arguments prior to
        initialization. By default arguments are deep copied.

'''         
        # DO NOT CHANGE _period IN PLACE
        self._period    = None

        self._direction = None

        # Set attributes, CF properties and data
        super(Coordinate, self).__init__(properties=properties,
                                         attributes=attributes,
                                         data=data,
                                         copy=copy)

        # Bounds
        if bounds is not None:
            self.insert_bounds(bounds, copy=copy)

        # Set default standard names based on units
    #--- End: def 

    def _query_contain(self, value):
        '''

'''
        if not self._hasbounds:
            return self == value

#        bounds = self.bounds.Data
#        mn = bounds.min(axes=-1)
#        mx = bounds.max(axes=-1)

        return (self.lower_bounds <= value) & (self.upper_bounds >= value)

#        return ((mn <= value) & (mx >= value)).squeeze(axes=-1, i=True)
    #--- End: def

#    def _binary_operation(self, other, method):
#        '''
#'''
#        self_hasbounds = self._hasbounds
#
#        if isinstance(other, self.__class__):
#            if other._hasbounds:
#                if not self_hasbounds:
#                    raise TypeError("asdfsdfdfds 0000")
#
#                other_bounds = other.bounds
#            elif self_hasbounds:
#                raise TypeError("asdfsdfdfds 00001")
#
#        else:
#            other_bounds = other
#            if numpy_size(other) > 1:
#                raise TypeError("4444444")
#
##        elif isinstance(other, (float, int, long)):
##            other_bounds = other
##
##        elif isinstance(other, numpy_ndarray):
##            if self_hasbounds:
##                if other.size > 1:
##                    raise TypeError("4444444")#
##
##                other_bounds = other
#        #-- End: if
#
#        new = super(Coordinate, self)._binary_operation(other, method)
#
#        if self_hasbounds:
#            new_bounds = self.bounds._binary_operation(other_bounds, method)
#
#        inplace = method[2] == 'i'
#
#        if not inplace:
#            if self_hasbounds:
#                new.bounds = new_bounds
#
#            return new
#        else: 
#            return self
#    #--- End: def        

    def _change_axis_names(self, dim_name_map):
        '''

Change the axis names.

Warning: dim_name_map may be changed in place

:Parameters:

    dim_name_map : dict

:Returns:

    None

:Examples:

'''
        # Change the axis names of the data array
        super(Coordinate, self)._change_axis_names(dim_name_map)

        if self._hasbounds:
            bounds = self.bounds
            if bounds._hasData:
                b_axes = bounds.Data._axes
                if self._hasData:
                    # Change the dimension names of the bounds
                    # array. Note that it is assumed that the bounds
                    # array dimensions are in the same order as the
                    # coordinate's data array dimensions. It is not
                    # required that the set of original bounds
                    # dimension names (bar the trailing dimension)
                    # equals the set of original coordinate data array
                    # dimension names. The bounds array dimension
                    # names will be changed to match the updated
                    # coordinate data array dimension names.
                    dim_name_map = {b_axes[-1]: 'bounds'}
                    for c_dim, b_dim in izip(self.Data._axes, b_axes):
                         dim_name_map[b_dim] = c_dim
                else:
                    dim_name_map[b_axes[-1]] = 'bounds'
                #--- End: if

                bounds._change_axis_names(dim_name_map)
    #--- End: def

    def _equivalent_data(self, other, rtol=None, atol=None,
                         traceback=False, copy=True):
        '''

:Parameters:

    copy : bool, optional

        If False then the *other* coordinate construct might get
        change in place.

:Returns:

    None

:Examples:

>>> 

'''
        if self._hasbounds != other._hasbounds:
            # add traceback
            return False

        if self.shape != other.shape:
            # add traceback
            return False              

        if (self.direction() != other.direction() and 
            self.direction() is not None and other.direction() is not None):
            other = other.flip(i=not copy)
            copy = False
        #--- End: if            

# DCH - should we test self.cyclic(), too? Think of non-cycli yet period coords ....

#        period = self._period
#        if period != other._period:
#            return False

        # Compare the data arrays
        if not super(Coordinate, self)._equivalent_data(other, rtol=rtol,
                                                        atol=atol, copy=copy):
            return False 
#            if period is None:
#                return False
#
#            other = other.anchor(self.datum(0), i=not copy)
#            copy = False
#
#            if not super(Coordinate, self)._equivalent_data(other, rtol=rtol,
#                                                            atol=atol, copy=copy):
#                return False
        #--- End: if

        if self._hasbounds:
            # Both coordinates have bounds
            if not self.bounds._equivalent_data(other.bounds, rtol=rtol,
                                                atol=atol, copy=copy):
                return False
        #--- End: if

        # Still here? Then the data are equivalent.
        return True
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def attributes(self):
        '''

A dictionary of the attributes which are not CF properties.

:Examples:

>>> c.attributes
{}
>>> c.foo = 'bar'
>>> c.attributes
{'foo': 'bar'}
>>> c.attributes.pop('foo')
'bar'
>>> c.attributes
{'foo': 'bar'}

'''
        attributes = super(Coordinate, self).attributes

        # Remove private attributes
        del attributes['_direction']

        return attributes
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (a special attribute)
    # ----------------------------------------------------------------
    @property
    def bounds(self):
        '''

The `cf.CoordinateBounds` object containing the cell bounds.

.. seealso:: `lower_bounds`, `upper_bounds`

:Examples:

>>> c
<CF Coordinate: latitude(64) degrees_north>
>>> c.bounds
<CF CoordinateeBounds: latitude(64, 2) degrees_north>
>>> c.bounds = b
AttributeError: Can't set 'bounds' attribute. Consider the insert_bounds method.
>>> c.bounds.max()
<CF Data: 90.0 degrees_north>
>>> c.bounds -= 1
AttributeError: Can't set 'bounds' attribute. Consider the insert_bounds method.
>>> b = c.bounds
>>> b -= 1
>>> c.bounds.max()       
<CF Data: 89.0 degrees_north>

'''
        return self._get_special_attr('bounds')
    #--- End: def
    @bounds.setter
    def bounds(self, value):
        raise AttributeError(
            "Can't set 'bounds' attribute. Consider the insert_bounds method.")
#        self._set_special_attr('bounds', value)        
#        self._hasbounds = True
    #--- End: def
    @bounds.deleter
    def bounds(self):  
        self._del_special_attr('bounds')
        self._hasbounds = False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def cellsize(self):
        '''

A `cf.Data` object containing the coordinate cell sizes.

:Examples:

>>> print c.bounds
<CF CoordinateBounds: latitude(47, 2) degrees_north>
>>> print c.bounds.array
[[-90. -87.]
 [-87. -80.]
 [-80. -67.]]
>>> print d.cellsize
<CF Data: [3.0, ..., 13.0] degrees_north>
>>> print d.cellsize.array
[  3.   7.  13.]
>>> print c.sin().cellsize.array
[ 0.00137047  0.01382178  0.0643029 ]

>>> del c.bounds
>>> c.cellsize
AttributeError: Can't get cell sizes when coordinates have no bounds


'''
        if not self._hasbounds:
            raise AttributeError(
                "Can't get cell sizes when coordinates have no bounds")

        cells = self.bounds.data
        cells = (cells[:, 1] - cells[:, 0]).abs()
        cells.squeeze(1, i=True)
        
        return cells
    #--- End: def
           
    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def ctype(self):
        '''

The CF coordinate type.

One of ``'T'``, ``'X'``, ``'Y'`` or ``'Z'`` if the coordinate object
is for the respective CF axis type, otherwise None.

.. seealso:: `T`, `X`, `~cf.Coordinate.Y`, `Z`

:Examples:

>>> c.X
True
>>> c.ctype
'X'

>>> c.T
True
>>> c.ctype
'T'

'''
        for t in ('T', 'X', 'Y', 'Z'):
            if getattr(self, t):
                return t
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------
    @property
    def dtype(self):
        '''

Numpy data-type of the data array.

:Examples:

>>> c.dtype
dtype('float64')
>>> import numpy
>>> c.dtype = numpy.dtype('float32')

'''
        if self._hasData:
            return self.Data.dtype
        
        if self._hasbounds:
            return self.bounds.dtype

        raise AttributeError("%s doesn't have attribute 'dtype'" %
                             self.__class__.__name__)
    #--- End: def
    @dtype.setter
    def dtype(self, value):
        if self._hasData:
            self.Data.dtype = value

        if self._hasbounds:
            self.bounds.dtype = value
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isauxiliary(self):
        '''

True for auxiliary coordinate constructs, False otherwise.

.. seealso:: `ismeasure`, `isdimension`

:Examples:

>>> c.isauxiliary
False

'''
        return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isdimension(self): 
        '''

True for dimension coordinate constructs, False otherwise.

.. seealso::  `isauxiliary`, `ismeasure`

:Examples:

>>> c.isdimension
False

'''
        return False
    #--- End: def
 
    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isperiodic(self): 
        '''


>>> print c.period()
None
>>> c.isperiodic
False
>>> c.period(cf.Data(360, 'degeres_east'))
None
>>> c.isperiodic
True
>>> c.period(None)
<CF Data: 360 degrees_east>
>>> c.isperiodic
False

'''
        return self._period is not None
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def lower_bounds(self):
        '''

The lower coordinate bounds in a `cf.Data` object.

``c.lower_bounds`` is equivalent to ``c.bounds.data.min(axes=-1)``.

.. seealso:: `bounds`, `upper_bounds`

:Examples:

>>> print c.bounds.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> c.lower_bounds
<CF Data: [3, ..., -1]>
>>> print c.lower_bounds.array
[ 3  1 -1]

'''
        if not self._hasbounds:
            raise ValueError("Can't get lower bounds when there are no bounds")

        return self.bounds.lower_bounds
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def subspace(self):
        '''

Return a new coordinate whose data and bounds are subspaced in a
consistent manner.

This attribute may be indexed to select a subspace from dimension
index values.

**Subspacing by indexing**

Subspacing by dimension indices uses an extended Python slicing
syntax, which is similar numpy array indexing. There are two
extensions to the numpy indexing functionality:

* Size 1 dimensions are never removed.

  An integer index i takes the i-th element but does not reduce the
  rank of the output array by one.

* When advanced indexing is used on more than one dimension, the
  advanced indices work independently.

  When more than one dimension's slice is a 1-d boolean array or 1-d
  sequence of integers, then these indices work independently along
  each dimension (similar to the way vector subscripts work in
  Fortran), rather than by their elements.

:Examples:

'''
        return SubspaceCoordinate(self)
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: T (read only)
    # ----------------------------------------------------------------
    @property
    def T(self):
        '''True if and only if the coordinates are for a CF T axis.

CF T axis coordinates are for a reference time axis hhave one or more
of the following:

  * The `axis` property has the value ``'T'``
  * Units of reference time (see `cf.Units.isreftime` for details)
  * The `standard_name` property is one of ``'time'`` or
    ``'forecast_reference_time'longitude'``

.. seealso:: `ctype`, `X`, `~cf.Coordinate.Y`, `Z`

:Examples:

>>> c.Units
<CF Units: seconds since 1992-10-8>
>>> c.T
True

>>> c.standard_name in ('time', 'forecast_reference_time')
True
>>> c.T
True

>>> c.axis == 'T' and c.T
True

        '''      
        if self.ndim > 1:
            return self.getprop('axis', None) == 'T'

        if (self.Units.isreftime or
            self.getprop('standard_name', 'T') in ('time',
                                                   'forecast_reference_time') or
            self.getprop('axis', None) == 'T'):
            return True
        else:
            return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------
    @property
    def Units(self):
        '''

The Units object containing the units of the data array.

'''
        return Variable.Units.fget(self)
    #--- End: def

    @Units.setter
    def Units(self, value):
        Variable.Units.fset(self, value)

        # Set the Units on the bounds
        if self._hasbounds:
            self.bounds.Units = value

        # Set the Units on the period
        if self._period is not None:
            period = self._period.copy()
            period.Units = value
            self._period = period

        self._direction = None
    #--- End: def
    
    @Units.deleter
    def Units(self):
        Variable.Units.fdel(self)
        
        if self._hasbounds:
            # Delete the bounds' Units
            del self.bounds.Units

        if self._period is not None:
            # Delete the period's Units
            period = self._period.copy()
            del period.Units
            self._period = period

        self._direction = None
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def upper_bounds(self):
        '''

The upper coordinate bounds in a `cf.Data` object.

``c.upper_bounds`` is equivalent to ``c.bounds.data.max(axes=-1)``.

.. seealso:: `bounds`, `lower_bounds`

:Examples:

>>> print c.bounds.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> c.upper_bounds      
<CF Data: [5, ..., 1]>
>>> c.upper_bounds.array     
array([5, 3, 1])

'''
        if not self._hasbounds:
            raise ValueError("Can't get upper bounds when there are no bounds")

        return self.bounds.upper_bounds
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: X (read only)
    # ----------------------------------------------------------------
    @property
    def X(self):
        '''True if and only if the coordinates are for a CF X axis.

CF X axis coordinates are for a horizontal axis have one or more of
the following:

  * The `axis` property has the value ``'X'``
  * Units of longitude (see `cf.Units.islongitude` for details)
  * The `standard_name` property is one of ``'longitude'``,
    ``'projection_x_coordinate'`` or ``'grid_longitude'``

.. seealso:: `ctype`, `T`, `~cf.Coordinate.Y`, `Z`

:Examples:

>>> c.Units
<CF Units: degreeE>
>>> c.X
True

>>> c.standard_name
'longitude'
>>> c.X
True

>>> c.axis == 'X' and c.X
True

        '''              
        if self.ndim > 1:
            return self.getprop('axis', None) == 'X'

        if (self.Units.islongitude or
            self.getprop('axis', None) == 'X' or
            self.getprop('standard_name', None) in ('longitude',
                                                    'projection_x_coordinate',
                                                    'grid_longitude')):
            return True
        else:
            return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: Y (read only)
    # ----------------------------------------------------------------
    @property
    def Y(self):
        '''True if and only if the coordinates are for a CF Y axis.

CF Y axis coordinates are for a horizontal axis and have one or more
of the following:

  * The `axis` property has the value ``'Y'``
  * Units of latitude (see `cf.Units.islatitude` for details)
  * The `standard_name` property is one of ``'latitude'``,
    ``'projection_y_coordinate'`` or ``'grid_latitude'``

.. seealso:: `ctype`, `T`, `X`, `Z`

:Examples:

>>> c.Units
<CF Units: degree_north>
>>> c.Y
True

>>> c.standard_name == 'latitude'
>>> c.Y
True

>>> c.axis
'Y'
>>> c.Y
True

        '''              
        if self.ndim > 1:
            return self.getprop('axis', None) == 'Y'

        if (self.Units.islatitude or 
            self.getprop('axis', None) == 'Y' or 
            self.getprop('standard_name', 'Y') in ('latitude',
                                                   'projection_y_coordinate',
                                                   'grid_latitude')):            
            return True
        else:
            return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: Z (read only)
    # ----------------------------------------------------------------
    @property
    def Z(self):
        '''True if and only if the coordinates are for a CF Z axis.

CF Z axis coordinates are for a vertical axis have one or more of the
following:

  * The `axis` property has the value ``'Z'``
  * Units of pressure (see `cf.Units.ispressure` for details), level,
    layer, or sigma_level
  * The `positive` property has the value ``'up'`` or ``'down'``
    (case insensitive)
  * The `standard_name` property is one of
    ``'atmosphere_ln_pressure_coordinate'``,
    ``'atmosphere_sigma_coordinate'``,
    ``'atmosphere_hybrid_sigma_pressure_coordinate'``,
    ``'atmosphere_hybrid_height_coordinate'``,
    ``'atmosphere_sleve_coordinate``', ``'ocean_sigma_coordinate'``,
    ``'ocean_s_coordinate'``, ``'ocean_s_coordinate_g1'``,
    ``'ocean_s_coordinate_g2'``, ``'ocean_sigma_z_coordinate'`` or
    ``'ocean_double_sigma_coordinate'``

.. seealso:: `ctype`, `T`, `X`, `~cf.Coordinate.Y`

:Examples:

>>> c.Units
<CF Units: Pa>
>>> c.Z
True

>>> c.Units.equivalent(cf.Units('K')) and c.positive == 'up'
True
>>> c.Z
True

>>> c.axis == 'Z' and c.Z
True

>>> c.Units
<CF Units: sigma_level>
>>> c.Z
True

>>> c.standard_name
'ocean_sigma_coordinate'
>>> c.Z
True

        '''   
        if self.ndim > 1:
            return self.getprop('axis', None) == 'Z'
        
        units = self.Units
        if (units.ispressure or
            str(self.getprop('positive', 'Z')).lower() in ('up', 'down') or
            self.getprop('axis', None) == 'Z' or
            (units and units.units in ('level', 'layer' 'sigma_level')) or
            self.getprop('standard_name', None) in
            ('atmosphere_ln_pressure_coordinate',
             'atmosphere_sigma_coordinate',
             'atmosphere_hybrid_sigma_pressure_coordinate',
             'atmosphere_hybrid_height_coordinate',
             'atmosphere_sleve_coordinate',
             'ocean_sigma_coordinate',
             'ocean_s_coordinate',
             'ocean_s_coordinate_g1',
             'ocean_s_coordinate_g2',
             'ocean_sigma_z_coordinate',
             'ocean_double_sigma_coordinate')):
            return True
        else:
            return False
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: axis
    # ----------------------------------------------------------------
    @property
    def axis(self):
        '''

The axis CF property.

:Examples:

>>> c.axis = 'Y'
>>> c.axis
'Y'
>>> del c.axis

>>> c.setprop('axis', 'T')
>>> c.getprop('axis')
'T'
>>> c.delprop('axis')

'''
        return self.getprop('axis')
    #--- End: def
    @axis.setter
    def axis(self, value): 
        self.setprop('axis', value)    
    @axis.deleter
    def axis(self):       
        self.delprop('axis')

    # ----------------------------------------------------------------
    # CF property: calendar
    # ----------------------------------------------------------------
    @property
    def calendar(self):
        '''

The calendar CF property.

This property is a mirror of the calendar stored in the `Units`
attribute.

:Examples:

>>> c.calendar = 'noleap'
>>> c.calendar
'noleap'
>>> del c.calendar

>>> c.setprop('calendar', 'proleptic_gregorian')
>>> c.getprop('calendar')
'proleptic_gregorian'
>>> c.delprop('calendar')

'''
        return Variable.calendar.fget(self)
    #--- End: def

    @calendar.setter
    def calendar(self, value):
        Variable.calendar.fset(self, value)
        # Set the calendar of the bounds
        if self._hasbounds:
            self.bounds.setprop('calendar', value)
    #--- End: def

    @calendar.deleter
    def calendar(self):
        Variable.calendar.fdel(self)
        # Delete the calendar of the bounds
        if self._hasbounds:
            try:
                self.bounds.delprop('calendar')
            except AttributeError:
                pass
    #--- End: def
    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def leap_month(self):
        '''

The leap_month CF property.

:Examples:

>>> c.leap_month = 2
>>> c.leap_month
2
>>> del c.leap_month

>>> c.setprop('leap_month', 11)
>>> c.getprop('leap_month')
11
>>> c.delprop('leap_month')

'''
        return self.getprop('leap_month')
    #--- End: def
    @leap_month.setter
    def leap_month(self, value):
        self.setprop('leap_month', value)
    @leap_month.deleter
    def leap_month(self):        
        self.delprop('leap_month')

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def leap_year(self):
        '''

The leap_year CF property.

:Examples:

>>> c.leap_year = 1984
>>> c.leap_year
1984
>>> del c.leap_year

>>> c.setprop('leap_year', 1984)
>>> c.getprop('leap_year')
1984
>>> c.delprop('leap_year')

'''
        return self.getprop('leap_year')
    #--- End: def
    @leap_year.setter
    def leap_year(self, value):
        self.setprop('leap_year', value)
    @leap_year.deleter
    def leap_year(self):
        self.delprop('leap_year')

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def month_lengths(self):
        '''

The month_lengths CF property.

Stored as a tuple but may be set as any array-like object.

:Examples:

>>> c.month_lengths = numpy.array([34, 31, 32, 30, 29, 27, 28, 28, 28, 32, 32, 34])
>>> c.month_lengths
(34, 31, 32, 30, 29, 27, 28, 28, 28, 32, 32, 34)
>>> del c.month_lengths

>>> c.setprop('month_lengths', [34, 31, 32, 30, 29, 27, 28, 28, 28, 32, 32, 34])
>>> c.getprop('month_lengths')
(34, 31, 32, 30, 29, 27, 28, 28, 28, 32, 32, 34)
>>> c.delprop('month_lengths')

'''
        return self.getprop('month_lengths')
    #--- End: def

    @month_lengths.setter
    def month_lengths(self, value):
        value = tuple(value)
        self.setprop('month_lengths', value)
    #--- End: def
    @month_lengths.deleter
    def month_lengths(self):        
        self.delprop('month_lengths')

    # ----------------------------------------------------------------
    # CF property: positive
    # ----------------------------------------------------------------
    @property
    def positive(self):
        '''

The positive CF property.

:Examples:

>>> c.positive = 'up'
>>> c.positive
'up'
>>> del c.positive

>>> c.setprop('positive', 'down')
>>> c.getprop('positive')
'down'
>>> c.delprop('positive')

'''
        return self.getprop('positive')
    #--- End: def

    @positive.setter
    def positive(self, value):
        self.setprop('positive', value)  
        self._direction = None
   #--- End: def
 
    @positive.deleter
    def positive(self):
        self.delprop('positive')       
        self._direction = None

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def standard_name(self):
        '''

The standard_name CF property.

:Examples:

>>> c.standard_name = 'time'
>>> c.standard_name
'time'
>>> del c.standard_name

>>> c.setprop('standard_name', 'time')
>>> c.getprop('standard_name')
'time'
>>> c.delprop('standard_name')

'''
        return self.getprop('standard_name')
    #--- End: def
    @standard_name.setter
    def standard_name(self, value): 
        self.setprop('standard_name', value)
    @standard_name.deleter
    def standard_name(self):       
        self.delprop('standard_name')

    # ----------------------------------------------------------------
    # CF property: units
    # ----------------------------------------------------------------
    # DCH possible inconsistency when setting self.Units.units ??
    @property
    def units(self):
        '''

The units CF property.

This property is a mirror of the units stored in the `Units`
attribute.

:Examples:

>>> c.units = 'degrees_east'
>>> c.units
'degree_east'
>>> del c.units

>>> c.setprop('units', 'days since 2004-06-01')
>>> c.getprop('units')
'days since 2004-06-01'
>>> c.delprop('units')

'''
        return Variable.units.fget(self)
    #--- End: def

    @units.setter
    def units(self, value):
        Variable.units.fset(self, value)

        if self._hasbounds:
            # Set the units on the bounds        
            self.bounds.setprop('units', value)

        self._direction = None
    #--- End: def
    
    @units.deleter
    def units(self):
        Variable.units.fdel(self)
                
        self._direction = None
        
        if self._hasbounds:
            # Delete the units from the bounds
            try:                
                self.bounds.delprop('units')
            except AttributeError:
                pass
    #--- End: def

    def asauxiliary(self, copy=True):
        '''

Return the coordinate recast as an auxiliary coordinate.

:Parameters:

    copy : bool, optional
        If False then the returned auxiliary coordinate is not
        independent. By default the returned auxiliary coordinate is
        independent.

:Returns:

    out : cf.AuxiliaryCoordinate
        The coordinate recast as an auxiliary coordinate.

:Examples:

>>> a = c.asauxiliary()
>>> a = c.asauxiliary(copy=False)

'''
        return AuxiliaryCoordinate(attributes=self.attributes,
                                   properties=self.properties,
                                   data=getattr(self, 'Data', None),
                                   bounds=getattr(self, 'bounds', None),
                                   copy=copy)
    #--- End: def

    def asdimension(self, copy=True):
        '''

Return the coordinate recast as a dimension coordinate.

:Parameters:

    copy : bool, optional
        If False then the returned dimension coordinate is not
        independent. By default the returned dimension coordinate is
        independent.

:Returns:

    out : cf.DimensionCoordinate
        The coordinate recast as a dimension coordinate.

:Examples:

>>> d = c.asdimension()
>>> d = c.asdimension(copy=False)

'''        
        if self._hasData:
            if self.ndim > 1:
                raise ValueError(
                    "Dimension coordinate must be 1-d (not %d-d)" %
                    self.ndim)
        elif self._hasbounds:
            if self.bounds.ndim > 2:
                raise ValueError(
                    "Dimension coordinate must be 1-d (not %d-d)" %
                    self.ndim)

        return DimensionCoordinate(attributes=self.attributes,
                                   properties=self.properties,
                                   data=getattr(self, 'Data', None),
                                   bounds=getattr(self, 'bounds', None),
                                   copy=copy)
    #--- End: def

    def chunk(self, chunksize=None):
        '''

Partition the data array.

'''         
        if not chunksize:
            # Set the default chunk size
            chunksize = CHUNKSIZE()
            
        # Partition the coordinate's data
        super(Coordinate, self).chunk(chunksize)

        # Partition the data of the bounds, if they exist.
        if self._hasbounds:
            self.bounds.chunk(chunksize)
    #--- End: def

    def clip(self, a_min, a_max, units=None, i=False):
        '''

Clip (limit) the values in the data array and its bounds in place.

Given an interval, values outside the interval are clipped to the
interval edges.

Parameters :
 
    a_min : scalar

    a_max : scalar

    units : str or Units

    {+i}

:Returns: 

    None

:Examples:

'''
        c = super(Coordinate, self).clip(a_min, a_max, units=units, i=i)
        
        if c._hasbounds:
            # Clip the bounds
            c.bounds.clip(a_min, a_max, units=units, i=True)
            
        return c
    #--- End: def
  
    def close(self):
        '''

Close all files referenced by the coordinate.

Note that a closed file will be automatically reopened if its contents
are subsequently required.

:Returns:

    None

:Examples:

>>> c.close()

'''
        new = super(Coordinate, self).close()
        
        if self._hasbounds:
            self.bounds.close()
    #--- End: def

    @classmethod
    def concatenate(cls, coordinates, axis=0, _preserve=True):
        '''
Join a sequence of coordinates together.

:Returns:

    out : cf.{+Variable}

'''      
        coord0 = coordinates[0]

        if len(coordinates) == 1:
            return coordinates0.copy()

        out = Variable.concatenate(coordinates, axis=axis,
                                   _preserve=_preserve)
        
        if coord0._hasbounds:
            bounds = Variable.concatenate(
                [c.bounds for c in coordinates],
                axis=axis, _preserve=_preserve)

            out.insert_bounds(bounds, copy=False)
        
        return out
    #--- End: def

    def contiguous(self, overlap=True):
        '''

Return True if a coordinate is contiguous.

A coordinate is contiguous if its cell boundaries match up, or
overlap, with the boundaries of adjacent cells.

In general, it is only possible for 1 or 0 dimensional coordinates
with bounds to be contiguous, but size 1 coordinates with any number
of dimensions are always contiguous.

An exception occurs if the coordinate is multdimensional and has more
than one element.

:Parameters:

    overlap : bool, optional    
        If False then overlapping cell boundaries are not considered
        contiguous. By default cell boundaries are considered
        contiguous.

:Returns:

    out : bool
        Whether or not the coordinate is contiguous.

:Raises:

    ValueError :
        If the coordinate has more than one dimension.

:Examples:

>>> c.hasbounds
False
>>> c.contiguous()
False

>>> print c.bounds[:, 0]
[  0.5   1.5   2.5   3.5 ]
>>> print c.bounds[:, 1]
[  1.5   2.5   3.5   4.5 ]
>>> c.contiuous()
True

>>> print c.bounds[:, 0]
[  0.5   1.5   2.5   3.5 ]
>>> print c.bounds[:, 1]
[  2.5   3.5   4.5   5.5 ]
>>> c.contiuous()
True
>>> c.contiuous(overlap=False)
False

'''
        if not self._hasbounds:
            return False

        return self.bounds.contiguous(overlap=overlap, direction=self.direction)

#        if monoyine:
#            return self.monit()#
#
#        return False
    #--- End: def

    def cos(self, i=False):
        '''

Take the trigonometric cosine of the data array and bounds in place.

Units are accounted for in the calcualtion, so that the the cosine of
90 degrees_east is 0.0, as is the sine of 1.57079632 radians. If the
units are not equivalent to radians (such as Kelvin) then they are
treated as if they were radians.

The Units are changed to '1' (nondimensionsal).

:Parameters:

    {+i}

:Returns:

    out : cf.Coordinate

:Examples:

>>> c.Units
<CF Units: degrees_east>
>>> print c.array
[[-90 0 90 --]]
>>> c.cos()
>>> c.Units
<CF Units: 1>
>>> print c.array
[[0.0 1.0 0.0 --]]

>>> c.Units
<CF Units: m s-1>
>>> print c.array
[[1 2 3 --]]
>>> c.cos()
>>> c.Units
<CF Units: 1>
>>> print c.array
[[0.540302305868 -0.416146836547 -0.9899924966 --]]

'''
        if i:
            c = self
        else:
            c = self.copy()

        super(Coordinate, c).cos(i=True)

        if c._hasbounds:
            c.bounds.cos(i=True)

        return c
    #--- End: def

    def cyclic(self, axes=None, iscyclic=True):
        '''

Set the cyclicity of axes of the data array and bounds.

.. seealso:: `cf.DimensionCoordinate.period`

:Parameters:

    axes : (sequence of) int
        The axes to be set. Each axis is identified by its integer
        position. By default no axes are set.
        
    iscyclic: bool, optional

:Returns:

    out : list

:Examples:

'''
        old = super(Coordinate, self).cyclic(axes, iscyclic)

        if axes is not None and self._hasbounds:
            axes = _parse_axes(axes)
            self.bounds.cyclic(axes, iscyclic)

        return old
    #--- End: def

    def tan(self, i=False):
        '''

Take the trigonometric tangent of the data array and bounds in place.

Units are accounted for in the calculation, so that the the tangent of
180 degrees_east is 0.0, as is the sine of 3.141592653589793
radians. If the units are not equivalent to radians (such as Kelvin)
then they are treated as if they were radians.

The Units are changed to '1' (nondimensionsal).

:Parameters:

    {+i}

:Returns:

    out : cf.Coordinate

:Examples:

'''
        if i:
            c = self
        else:
            c = self.copy()

        super(Coordinate, c).tan(i=True)

        if c._hasbounds:
            c.bounds.tan(i=True)

        return c
    #--- End: def

    def copy(self, _omit_Data=False, _only_Data=False):
        '''
        
Return a deep copy.

Equivalent to ``copy.deepcopy(c)``.

:Returns:

    out :
        The deep copy.

:Examples:

>>> d = c.copy()

'''
        new = super(Coordinate, self).copy(_omit_Data=_omit_Data,
                                           _only_Data=_only_Data,
                                           _omit_special=('bounds',))

        if self._hasbounds:
            bounds = self.bounds.copy(_omit_Data=_omit_Data,
                                      _only_Data=_only_Data)
            new._set_special_attr('bounds', bounds)        

        return new
    #--- End: def

    def delprop(self, prop):
        '''

Delete a CF property.

.. seealso:: `getprop`, `hasprop`, `setprop`

:Parameters:

    prop : str
        The name of the CF property.

:Returns:

     None

:Examples:

>>> c.delprop('standard_name')
>>> c.delprop('foo')
AttributeError: Coordinate doesn't have CF property 'foo'

'''
        # Delete a special attribute
        if prop in self._special_properties:
            delattr(self, prop)
            return

        # Still here? Then delete a simple attribute

        # Delete selected simple properties from the bounds
        if self._hasbounds and prop in ('standard_name', 'axis', 'positive',
                                        'leap_month', 'leap_year',
                                        'month_lengths'):
            try:
                self.bounds.delprop(prop)
            except AttributeError:
                pass
        #--- End: if

        d = self._private['simple_properties']
        if prop in d:
            del d[prop]
        else:
            raise AttributeError("Can't delete non-existent %s CF property %r" %
                                 (self.__class__.__name__, prop))

        if self._hasbounds and prop in ('standard_name', 'axis', 'positive', 
                                        'leap_month', 'leap_year',
                                        'month_lengths'):
            try:
                self.bounds.delprop(prop)
            except AttributeError:
                pass
    #--- End: def

    def direction(self):
        '''
    
Return None, indicating that it is not specified whether the
coordinate object is increasing or decreasing.

:Returns:

    None
        
:Examples:

>>> print c.direction()
None

''' 
        return
    #--- End: def

    def dump(self, display=True, omit=(), domain=None, key=None, _level=0): 
        '''

Return a string containing a full description of the coordinate.

:Parameters:

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``c.dump()`` is equivalent to
        ``print c.dump(display=False)``.

    omit : sequence of strs
        Omit the given CF properties from the description.

:Returns:

    out : None or str
        A string containing the description.

:Examples:

'''
        indent0 = '    ' * _level
        indent1 = '    ' * (_level+1)

        string = []

        if domain:
            x = ['%s(%d)' % (domain.axis_name(axis), domain.axis_size(axis))
                 for axis in domain.item_axes(key)]
            string.append('%sData(%s) = %s' % (indent0, ', '.join(x),
                                               str(self.Data)))
            
            if self._hasbounds:
                x.append(str(self.bounds.shape[-1]))
                string.append('%sBounds(%s) = %s' % (indent0, ', '.join(x),
                                                     str(self.bounds.Data)))
        else:
            x = [str(s) for s in self.shape]
            string.append('%sData(%s) = %s' % (indent0, ', '.join(x),
                                               str(self.Data)))
            
            if self._hasbounds:
                x.append(str(self.bounds.shape[-1]))
                string.append('%sBounds(%s) = %s' % (indent0, ', '.join(x),
                                                     str(self.bounds.Data)))
        #--- End: if

        if self._simple_properties():
            string.append(self._dump_simple_properties(_level=_level))

        string = '\n'.join(string)
       
        if display:
            print string
        else:
            return string
    #--- End: def

    def expand_dims(self, position=0, i=False):
        '''

Insert a size 1 axis into the data array and bounds in place.

.. seealso:: `flip`, `squeeze`, `transpose`

:Parameters:

    position : int, optional
        Specify the position amongst the data array axes where the new
        axis is to be inserted. By default the new axis is inserted at
        position 0, the slowest varying position.

    {+i}

:Returns:

    out : cf.Coordinate

'''
        if (not self._hasData and
            (not self._hasbounds or not self.bounds._hasData)):
            raise ValueError(
                "Can't insert axis into '%s'" % self.__class__.__name__)

        if self._hasData:
            c = super(Coordinate, self).expand_dims(position, i=i)
        elif i:
            c = self
        else:
            c = self.copy()

        if c._hasbounds and c.bounds._hasData:
            # Expand the coordinate's bounds
            position = _parse_axes([position])[0]
            c.bounds.expand_dims(position, i=True)

#        if i:
#            c = self
#        else:
#            c = self.copy()
#
#        # Expand the coordinate's data, if it has any.
#        if c._hasData:
##            super(Coordinate, self).expand_dims(position, i=True)
#            c.Data.expand_dims(position, i=True)
#
#        # Expand the coordinate's bounds, if it has any.
#        if c._hasbounds and c.bounds._hasData:
##            c.bounds.expand_dims(position, i=True)
#            c.bounds.Data.expand_dims(position, i=True)

        return c
    #--- End: def

    def flip(self, axes=None, i=False):
        '''

Flip dimensions of the data array and bounds in place.

The trailing dimension of the bounds is flipped if and only if the
coordinate is 1 or 0 dimensional.

:Parameters:

    axes : (sequence of) int, optional
        Flip the dimensions whose positions are given. By default all
        dimensions are flipped.

    {+i}

:Returns:

    out : cf.Coordinate

:Examples:

>>> c.flip()
>>> c.flip(1)

>>> d = c.subspace[::-1, :, ::-1, :]
>>> c.flip([2, 0]).equals(d)
True

'''
        c = super(Coordinate, self).flip(axes, i=i)

        # ------------------------------------------------------------
        # Flip the requested dimensions in the coordinate's bounds, if
        # it has any.
        #
        # As per section 7.1 in the CF conventions: i) if the
        # coordinate is 0 or 1 dimensional then flip all dimensions
        # (including the the trailing size 2 dimension); ii) if the
        # coordinate has 2 or more dimensions then do not flip the
        # trailing dimension.
        # ------------------------------------------------------------
        if c._hasbounds and c.bounds._hasData:
            # Flip the bounds
            if not c.ndim:
                # Flip the bounds of 0-d coordinates
                axes = (-1,)
            elif c.ndim == 1:
                # Flip the bounds of 1-d coordinates
                if axes in (0, -1):
                    axes = (0, -1)
                elif axes is not None:
                    axes = _parse_axes(axes) + [-1]
            else:
                # Do not flip the bounds of N-d coordinates (N >= 2)
                axes = _parse_axes(axes)

            c.bounds.flip(axes, i=True)            
        #--- End if

        direction = c._direction
        if direction is not None:
            c._direction = not direction

        return c
    #--- End: def

    def insert_bounds(self, bounds, copy=True):
        '''

Insert cell bounds into the coordinate in-place.

:Parameters:

    bounds : cf.Data or cf.CoordinateBounds

    copy : bool, optional

:Returns:

    None

'''
        # Check dimensionality
        if bounds.ndim != self.ndim + 1:
            raise ValueError(
"Can't set coordinate bounds: Incorrect number of dimemsions: %d (expected %d)" % 
(bounds.ndim, self.ndim+1))

        # Check shape
        if bounds.shape[:-1] != self.shape:
            raise ValueError(
"Can't set coordinate bounds: Incorrect shape: %s (expected %s)" % 
(bounds.shape, self.shape+(bounds.shape[-1],)))

        if copy:            
            bounds = bounds.copy()

        # Check units
        units      = bounds.Units
        self_units = self.Units
        if units and not units.equivalent(self_units):
            raise ValueError(
"Can't set coordinate bounds: Incompatible units: %r (not equivalent to %r)" %
(bounds.Units, self.Units))

        bounds.Units = self_units

        if not isinstance(bounds, CoordinateBounds):
            bounds = CoordinateBounds(data=bounds, copy=False)  
       
        # Copy selected coordinate properties to the bounds
        for prop in ('standard_name', 'axis', 'positive', 'leap_months',
                     'leap_years', 'month_lengths'):
            value = self.getprop(prop, None)
            if value is not None:
                bounds.setprop(prop, value)

        self._set_special_attr('bounds', bounds)        

        self._hasbounds = True
        self._direction = None
    #--- End: def

    def insert_data(self, data, bounds=None, copy=True):
        '''

Insert a new data array into the coordinate in place.

A coordinate bounds data array may also inserted if given with the
*bounds* keyword. Coordinate bounds may also be inserted independently
with the `insert_bounds` method.

:Parameters:

    data : cf.Data

    bounds : cf.Data, optional

    copy : bool, optional

:Returns:

    None

'''
        if data is not None:
            super(Coordinate, self).insert_data(data, copy=copy)

        if bounds is not None:
            self.insert_bounds(bounds, copy=copy)

        self._direction = None
    #--- End: def

    def override_units(self, new_units, i=False):
        '''
    {+i}

'''
        if i:
            c = self
        else:
            c = self.copy()

        super(Coordinate, c).override_units(new_units, i=True)

        if c._hasbounds:
            c.bounds.override_units(new_units, i=True)

        if c._period is not None:
            # Never change _period in place
            c._period.override_units(new_units, i=False)

        return c
    #--- End: def

    def roll(self, axis, shift, i=False):
        '''
    {+i}
'''      
        if self.size <= 1:
            if i:
                return self
            else:
                return self.copy()

        c = super(Coordinate, self).roll(axis, shift, i=i)

        # Roll the bounds, if there are any
        if c._hasbounds:
            b = c.bounds
            if b._hasData:
                b.roll(axis, shift, i=True)
        #--- End: if

        return c
    #--- End: def

    def setprop(self, prop, value):
        '''

Set a CF property.

.. seealso:: `delprop`, `getprop`, `hasprop`

:Parameters:

    prop : str
        The name of the CF property.

    value :
        The value for the property.

:Returns:

     None

:Examples:

>>> c.setprop('standard_name', 'time')
>>> c.setprop('foo', 12.5)

'''
        # Set a special attribute
        if prop in self._special_properties:
            setattr(self, prop, value)
            return

        # Still here? Then set a simple property
        self._private['simple_properties'][prop] = value

        # Set selected simple properties on the bounds
        if self._hasbounds and prop in ('standard_name', 'axis', 'positive', 
                                        'leap_month', 'leap_year',
                                        'month_lengths'):
            self.bounds.setprop(prop, value)
    #--- End: def

    def sin(self, i=False):
        '''

Take the trigonometric sine of the data array and bounds in place.

Units are accounted for in the calculation. For example, the the sine
of 90 degrees_east is 1.0, as is the sine of 1.57079632 radians. If
the units are not equivalent to radians (such as Kelvin) then they are
treated as if they were radians.

The Units are changed to '1' (nondimensionsal).

:Parameters:

    {+i}

:Returns:

    out : cf.Coordinate

:Examples:

>>> c.Units
<CF Units: degrees_north>
>>> print c.array
[[-90 0 90 --]]
>>> c.sin()
>>> c.Units
<CF Units: 1>
>>> print c.array
[[-1.0 0.0 1.0 --]]

>>> c.Units
<CF Units: m s-1>
>>> print c.array
[[1 2 3 --]]
>>> c.sin()
>>> c.Units
<CF Units: 1>
>>> print c.array
[[0.841470984808 0.909297426826 0.14112000806 --]]

'''
        if i:
            c = self
        else:
            c = self.copy()

        super(Coordinate, c).sin(i=True)

        if c._hasbounds:
            c.bounds.sin(i=True)

        return c
    #--- End: def

    def log(self, base=10, i=False):
        '''

Take the logarithm the data array and bounds element-wise.

:Parameters:

    base : number, optional
    
    {+i}

:Returns:

    out : cf.Coordinate

'''
        if i:
            c = self
        else:
            c = self.copy()

        super(Coordinate, c).log(base, i=True)

        if c._hasbounds:
            c.bounds.log(base, i=True)

        return c
    #--- End: def

    def squeeze(self, axes=None, i=False):
        '''

Remove size 1 dimensions from the data array and bounds in place.

.. seealso:: `expand_dims`, `flip`, `transpose`

:Parameters:

    axes : (sequence of) int, optional
        The size 1 axes to remove. By default, all size 1 axes are
        removed. Size 1 axes for removal may be identified by the
        integer positions of dimensions in the data array.

    {+i}

:Returns:

    out : cf.Coordinate

:Examples:

>>> c.squeeze()
>>> c.squeeze(1)
>>> c.squeeze([1, 2])

'''
        c = super(Coordinate, self).squeeze(axes, i=i)

        if c._hasbounds and c.bounds._hasData:
            # Squeeze the bounds
            axes = _parse_axes(axes)
            c.bounds.squeeze(axes, i=True)

        return c
    #--- End: def

    def transpose(self, axes=None, i=False):
        '''

Permute the dimensions of the data array and bounds in place.

.. seealso:: `expand_dims`, `flip`, `squeeze`

:Parameters:

    axes : (sequence of) int, optional
        The new order of the data array. By default, reverse the
        dimensions' order, otherwise the axes are permuted according
        to the values given. The values of the sequence comprise the
        integer positions of the dimensions in the data array in the
        desired order.

    {+i}

:Returns:

    out : cf.Coordinate

:Examples:

>>> c.ndim
3
>>> c.transpose()
>>> c.transpose([1, 2, 0])

'''
        c = super(Coordinate, self).transpose(axes, i=i)

        ndim = c.ndim
        if c._hasbounds and ndim > 1 and c.bounds._hasData:
            # Transpose the bounds
            if axes is None:
                axes = range(ndim-1, -1, -1) + [-1]
            else:
                axes = _parse_axes(axes) + [-1]
                
            bounds = c.bounds
            bounds.transpose(axes, i=True)

            if (ndim == 2 and
                bounds.shape[-1] == 4 and 
                axes[0] == 1 and 
                (c.Units.islongitude or c.Units.islatitude or
                 c.getprop('standard_name', None) in ('grid_longitude' or
                                                      'grid_latitude'))):
                # Swap columns 1 and 3 so that the coordinates are
                # still contiguous (if they ever were). See section
                # 7.1 of the CF conventions.
                bounds.subspace[..., [1, 3]] = bounds.subspace[..., [3, 1]]
        #--- End: if

        return c
    #--- End: def

#--- End: class


# ====================================================================
#
# SubspaceCoordinate object
#
# ====================================================================

class SubspaceCoordinate(SubspaceVariable):

    __slots__ = []

    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]

'''
        coord = self.variable

        if indices is Ellipsis:
            return coord.copy()

        indices, roll = parse_indices(coord, indices, True)

        if roll:
            data = coord.Data
            axes = data._axes
            cyclic_axes = data._cyclic
            for iaxis, shift in roll.iteritems():
                if axes[iaxis] not in cyclic_axes:
                    raise IndexError(
                        "Can't do a cyclic slice on a non-cyclic axis")

                coord = coord.roll(iaxis, shift)
            #--- End: for
            new = coord
        else:
            new = coord.copy(_omit_Data=True)

#        # Copy the coordinate
#        new = coord.copy(_omit_Data=True)

 #       # Parse the index (so that it's ok for appending the bounds
 #       # index if required)
 #       indices = parse_indices(coord, indices)
    
        coord_data = coord.Data

        new.Data = coord_data[tuple(indices)]

        # Subspace the bounds, if there are any
        if not new._hasbounds:
            bounds = None
        else:
            bounds = coord.bounds
            if bounds._hasData:
                if coord_data.ndim <= 1:
                    index = indices[0]
                    if isinstance(index, slice):
                        if index.step < 0:
                            # This scalar or 1-d coordinate has been
                            # reversed so reverse its bounds (as per
                            # 7.1 of the conventions)
                            indices.append(slice(None, None, -1))
                    elif coord_data.size > 1 and index[-1] < index[0]:
                        # This 1-d coordinate has been reversed so
                        # reverse its bounds (as per 7.1 of the
                        # conventions)
                        indices.append(slice(None, None, -1))                    
                #--- End: if
                new.bounds.Data = bounds.Data[tuple(indices)]
        #--- End: if

        new._direction = None

        # Return the new coordinate
        return new
    #--- End: def

#--- End: class

# ====================================================================
#
# DimensionCoordinate object
#
# ====================================================================

class DimensionCoordinate(Coordinate):
    '''

A CF dimension coordinate construct.

**Attributes**

===============  ========  ===================================================
Attribute        Type      Description
===============  ========  ===================================================
`!climatology`   ``bool``  Whether or not the bounds are intervals of
                           climatological time. Presumed to be False if unset.
===============  ========  ===================================================

'''
#    def _query_contain(self, value):
#        '''#
#
#'''
#        if not self._hasbounds:
#            return self == value#
#
#        return (self.lower_bounds <= value) & (self.upper_bounds >= value)
#    #--- End: def

    def _centre(self, period):
        '''

It assumed, but not checked, that the period has been set.

'''

        if self.direction():
            mx = self.Data[-1]
        else:
            mx = self.Data[0]
            
        return ((mx // period) * period).squeeze(i=True)
    #--- End: def

    def _infer_direction(self):
        '''
    
Return True if a coordinate is increasing, otherwise return False.

A coordinate is considered to be increasing if its *raw* data array
values are increasing in index space or if it has no data not bounds
data.

If the direction can not be inferred from the coordinate's data then
the coordinate's units are used.

The direction is inferred from the coordinate's data array values or
its from coordinates. It is not taken directly from its `cf.Data`
object.

:Returns:

    out : bool
        Whether or not the coordinate is increasing.
        
:Examples:

>>> c.array
array([  0  30  60])
>>> c._get_direction()
True
>>> c.array
array([15])
>>> c.bounds.array
array([  30  0])
>>> c._get_direction()
False

'''
        if self._hasData:
            # Infer the direction from the dimension coordinate's data
            # array
            c = self.Data
            if c._size > 1:
                c = c[0:2].unsafe_array
                return c.item(0,) < c.item(1,)
        #--- End: if

        # Still here? 
        if self._hasbounds:
            # Infer the direction from the dimension coordinate's
            # bounds
            b = self.bounds
            if b._hasData:
                b = b.Data
                b = b[(0,)*(b.ndim-1)].unsafe_array
                return b.item(0,) < b.item(1,)
        #--- End: if

#        # Still here? Then infer the direction from the dimension
#        # coordinate's positive CF property.
#        positive = self.getprop('positive', None)
#        if positive is not None and positive[0] in 'dD':
#            return False
#
        # Still here? Then infer the direction from the units.
        return not self.Units.ispressure
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def cellsize(self):
        '''

A `cf.Data` object containing the coordinate cell sizes.

:Examples:

>>> print c.bounds
<CF CoordinateBounds: latitude(47, 2) degrees_north>
>>> print c.bounds.array
[[-90. -87.]
 [-87. -80.]
 [-80. -67.]]
>>> print d.cellsize
<CF Data: [3.0, ..., 13.0] degrees_north>
>>> print d.cellsize.array
[  3.   7.  13.]
>>> print c.sin().cellsize.array
[ 0.00137047  0.01382178  0.0643029 ]

>>> del c.bounds
>>> c.cellsize
AttributeError: Can't get cell sizes when coordinates have no bounds


'''
        if not self._hasbounds:
            raise AttributeError(
                "Can't get cell sizes when coordinates have no bounds")

        cells = self.bounds.data

#        if bounds_range is not None:
#            bounds_range = Data.asdata(bounds_range)#
#
#            if not bounds_range.Units:
#                bounds_range = bounds_range.override_units(self.Units)
#            cells.clip(*bounds_range, units=bounds_range.Units, i=True)
#        #--- End: if
        if self.direction():            
            cells = cells[:, 1] - cells[:, 0]
        else:
            cells = cells[:, 0] - cells[:, 1]

        cells.squeeze(1, i=True)
        
#        if units:
#            if cells.Units.equivalent(units):
#                cells.Units = units
#            else:
#                raise ValueError("sdfm 845 &&&&")
        
        return cells
    #--- End: def
           
    @property
    def decreasing(self): 
        '''

True if the dimension coordinate is increasing, otherwise
False.

A dimension coordinate is increasing if its coordinate values are
increasing in index space.

The direction is inferred from one of, in order of precedence:

* The data array
* The bounds data array
* The `units` CF property

:Returns:

    out : bool
        Whether or not the coordinate is increasing.
        
True for dimension coordinate constructs, False otherwise.

>>> c.decreasing
False
>>> c.flip().increasing
True

'''
        return not self.direction()
    #--- End: def

    @property
    def increasing(self): 
        '''

True for dimension coordinate constructs, False otherwise.

>>> c.increasing
True
>>> c.flip().increasing
False

'''
        return self.direction()
    #--- End: def

    @property
    def isauxiliary(self):
        '''

True for auxiliary coordinate constructs, False otherwise.

.. seealso:: `ismeasure`, `isdimension`

:Examples:

>>> c.isauxiliary
False

'''
        return False
    #--- End: def

    @property
    def isdimension(self): 
        '''

True for dimension coordinate constructs, False otherwise.

.. seealso::  `isauxiliary`, `ismeasure`

:Examples:

>>> c.isdimension
True

'''
        return True
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def lower_bounds(self):
        '''

The lower dimension coordinate bounds in a `cf.Data` object.

.. seealso:: `bounds`, `upper_bounds`

:Examples:

>>> print c.bounds.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> c.lower_bounds
<CF Data: [3, ..., -1]>
>>> print c.lower_bounds.array
[ 3  1 -1]

'''
        if not self._hasbounds or not self.bounds._hasData:
            raise ValueError("Can't get lower bounds when there are no bounds")

        if self.direction():
            i = 0
        else:
            i = 1

        return self.bounds.data[..., i].squeeze(1, i=True)
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def upper_bounds(self):
        '''

The upper dimension coordinate bounds in a `cf.Data` object.

.. seealso:: `bounds`, `lower_bounds`

:Examples:

>>> print c.bounds.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> c.upper_bounds      
<CF Data: [5, ..., 1]>
>>> c.upper_bounds.array     
array([5, 3, 1])

'''
        if not self._hasbounds or not self.bounds._hasData:
            raise ValueError("Can't get upper bounds when there are no bounds")

        if self.direction():
            i = 1
        else:
            i = 0

        return self.bounds.data[..., i].squeeze(1, i=True)
    #--- End: def

#    def anchor(self, value, i=False, dry_run=False):  
#        '''
#        '''
#        if i or dry_run:
#            c = self
#        else:
#            c = self.copy()
#        
#        
#        period = c.period()
#        if period is None:
#            raise ValueError(
#"Cyclic {!r} axis has no period".format(dim.name()))
#
#        value = Data.asdata(value)
#        if not value.Units:
#            value = value.override_units(dim.Units)
#        elif not value.Units.equivalent(dim.Units):
#            raise ValueError(
#"Anchor value has incompatible units: {!r}".format(value.Units))
#
#        axis_size = self.size
#        if axis_size <= 1:
#            # Don't need to roll a size one axis
#            if dry_run:
#                return {'axis': axis, 'roll': 0, 'nperiod': 0}
#            else:
#                return c
#        
#        d = c.data
#
#        if c.increasing:
#            # Adjust value so it's in the range [d[0], d[0]+period) 
#            n = ((d[0] - value) / period).ceil(i=True)
#            value1 = value + n * period
#
#            shift = axis_size - numpy_argmax(d - value1 >= 0)
#            if not dry_run:
#                c.roll(axis, shift, i=True)     
#
#            dim = domain.item(axis)
#            n = ((value - c.data[0]) / period).ceil(i=True)
#        else:
#            # Adjust value so it's in the range (d[0]-period, d[0]]
#            n = ((d[0] - value) / period).floor(i=True)
#            value1 = value + n * period
#
#            shift = axis_size - numpy_argmax(value1 - d >= 0)
#            if not dry_run:
#                c.roll(axis, shift, i=True)     
#
#            dim = domain.item(axis)
#            n = ((value - c.data[0]) / period).floor(i=True)
#        #--- End: if
#
#        if dry_run:
#            return  {'axis': axis, 'roll': shift, 'nperiod': n*period}
#
#        if n:
#            np = n * period
#            c += np
#            if c.hasbounds:
#                bounds = c.bounds
#                bounds += np
#        #--- End: if
#                
#        return c
#    #--- End: def

    def asdimension(self, copy=True):
        '''

Return the dimension coordinate.

:Parameters:

    copy : bool, optional
        If False then the returned dimension coordinate is not
        independent. By default the returned dimension coordinate is
        independent.

:Returns:

    out : cf.DimensionCoordinate
        The dimension coordinate.

:Examples:

>>> d = c.asdimension()
>>> print d is c
True

>>> d = c.asdimension(copy=False)
>>> print d == c
True
>>> print d is c
False

'''
        if copy:
            return self.copy()
        
        return self
    #--- End: def

    def direction(self):
        '''
    
Return True if the dimension coordinate is increasing, otherwise
return False.

A dimension coordinate is increasing if its coordinate values are
increasing in index space.

The direction is inferred from one of, in order of precedence:

* The data array
* The bounds data array
* The `units` CF property

:Returns:

    out : bool
        Whether or not the coordinate is increasing.
        
:Examples:

>>> c.array
array([  0  30  60])
>>> c.direction()
True

>>> c.bounds.array
array([  30  0])
>>> c.direction()
False

''' 
        _direction = self._direction
        if _direction is not None:
            return _direction

        _direction = self._infer_direction()
        self._direction = _direction

        return _direction
    #--- End: def

    # DimensionCoordinate
    def get_bounds(self, create=False, insert=False, bound=None,
                   cellsize=None, copy=True):
        '''Get the cell bounds.
    
Either return its existing bounds or, if there are none, optionally
create bounds based on the coordinate array values.
    
:Parameters:

    create : bool, optional
        If True then create bounds if and only if the the dimension
        coordinate does not already have them. Bounds for Voronoi
        cells are created unless *bound* is set.

    insert : bool, optional 
        If True then insert the created bounds into the coordinate in
        place. By default the created bounds are not inserted. Ignored
        if *create* is not True.

    bound : *optional*
        If set to an upper or lower bound for the whole array, then
        bounds are created which include this value and for which each
        array element is in the centre of its bounds. By default
        bounds for Voronoi cells are created. Ignored if *create* is
        not True.

    copy : bool, optional
        If False then the returned bounds are not independent of the
        existing bounds, if any, or those inserted, if *create* and
        *insert* are both True. By default the returned bounds are
        independent.

:Returns:

    out : cf.CoordinateBounds
        The existing or created bounds.

:Examples:

>>> c.get_bounds()
>>> c.get_bounds(create=True)
>>> c.get_bounds(create=True, bound=60)
>>> c.get_bounds(create=True, insert=True)
>>> c.get_bounds(create=True, bound=-9000.0, insert=True, copy=False)

'''
        if self._hasbounds:
            if copy:
                return self.bounds.copy()
            else:
                return self.bounds
         
        if not create:
            raise ValueError(
                "Dimension coordinates have no bounds and create={0}".format(create))

        array = self.unsafe_array
        size = array.size    

        if cellsize is not None:
            cellsize = Data.asdata(abs(cellsize))
            if cellsize.Units:
                if not cellsize.Units.equivalent(self.Units):
                    raise ValueError("jhgsjhbd jh ")
                cellsize.Units = self.Units
            cellsize = cellsize.datum()

        if bound is None:
            # Creat Voronoi bounds
            if size < 2:
                if cellsize is not None:
                    raise ValueError(
"Can't create bounds for Voronoi cells from one value when cellsize parameter is unset")

                cellsize  = cellsize * 0.5
                if not self.direction():
                    cellsize *= -1
   
                coord = array.item(0,)
                bounds_1d = [coord - cellsize, coord + cellsize]
            else:
                bounds_1d = [array.item(0,)*1.5 - array.item(1,)*0.5]
                bounds_1d.extend((array[0:-1] + array[1:])*0.5)
                bounds_1d.append(array.item(-1,)*1.5 - array.item(-2,)*0.5)

            dtype = type(bounds_1d[0])

        else:
            direction = self.direction()
            if not direction and size > 1:
                array = array[::-1]

            bounds_1d = [bound]
            if bound <= array.item(0,):
                for i in xrange(size):
                    bound = 2.0*array.item(i,) - bound
                    bounds_1d.append(bound)
            elif bound >= array.item(-1,):
                for i in xrange(size-1, -1, -1):
                    bound = 2.0*array.item(i,) - bound
                    bounds_1d.append(bound)

                bounds_1d = bounds_1d[::-1]
            else:
                raise ValueError("bad bound value")

            dtype = type(bounds_1d[-1])

            if not direction:               
                bounds_1d = bounds_1d[::-1]
        #--- End: if

        bounds = numpy_empty((size, 2), dtype=dtype)
        bounds[:,0] = bounds_1d[:-1]
        bounds[:,1] = bounds_1d[1:]        

        if cellsize is not None:
            cells = abs(bounds[:, 1] - bounds[:, 0])
            cells = cells.squeeze(axis=1)
            for i, (c, s) in enumerate(zip(array, cells)):
                if s <= cellsize:
                    continue
                if self.direction():
                    if c - bounds[i,0] <= cellsize:
                        bounds[i,1] = bounds[i,0] + cellsize
                    elif bounds[i,1] - c <= cellsize:
                        bounds[i,0] = bounds[i,1] - cellsize
                    else:
                        raise ValueError("asdasdasds8888888888888888888888")
                else:
                    if bounds[i,0] - c <= cellsize:
                        bounds[i,1] = bounds[i,0] - cellsize
                    elif c - bounds[i,1] <= cellsize:
                        bounds[i,0] = bounds[i,1] + cellsize
                    else:
                        raise ValueError("asdasdasds8888888888888888888888 66767")
        #--- End: if

        bounds = CoordinateBounds(data=Data(bounds, self.Units), copy=False)
                           
        if insert:
            self.insert_bounds(bounds, copy=copy)

        return bounds            
    #--- End: def

    def period(self, *value):
        '''Set the period for cyclic coordinates.

:Parameters:

    value : data-like or None, optional
        The period. The absolute value is used.

:Returns:

    out : cf.Data or None
        The period prior to the change, or the current period if no
        *value* was specified. In either case, None is returned if the
        period had not been set previously.

:Examples:

>>> print c.period()
None
>>> c.Units
<CF Units: degrees_east>
>>> print c.period(360)
None
>>> c.period()
<CF Data: 360.0 'degrees_east'>
>>> import math
>>> c.period(cf.Data(2*math.pi, 'radians'))
<CF Data: 360.0 degrees_east>
>>> c.period()
<CF Data: 6.28318530718 radians>
>>> c.period(None)
<CF Data: 6.28318530718 radians>
>>> print c.period()
None
>>> print c.period(-360)
None
>>> c.period()
<CF Data: 360.0 degrees_east>

        '''     
        old = self._period
        if old is not None:
            old = old.copy()

        if not value:
            return old
  
        value = value[0]

        if value is not None:
            value = Data.asdata(abs(value*1.0))
            units = value.Units
            if not units:
                value = value.override_units(self.Units)
            elif not units.equivalent(self.Units):
                raise ValueError(
"Period units {!r} are not equivalent to coordinate units {!r}".format(
    units, self.Units))

            range = self.Data.range()
            if range >= value:
                raise ValueError(
"The coordinate range {!r} is not less than the period {!r}".format(
    range, value))
        #--- End: if

        self._period = value

        return old
    #--- End: def

    def roll(self, axis, shift, i=False):
        '''
    {+i}

'''
        if self.size <= 1:
            if i:
                return self
            else:
                return self.copy()

        shift %= self.size

        period = self._period

        if not shift:
            # Null roll
            if i:
                return self
            else:
                return self.copy()
        elif period is None:
            raise ValueError(
"Can't roll %s array by %s positions when no period has been set" %
(shift, self.__class__.__name__))

        direction = self.direction()

#        if direction:
#            mx = self.Data[-1]
#        else:
#            mx = self.Data[0]
#            
#        centre = (mx // period) * period
        centre = self._centre(period)

        c = super(DimensionCoordinate, self).roll(axis, shift, i=i)

        isbounded = c._hasbounds
        if isbounded:
            b = c.bounds
            if not b._hasData:
                isbounded = False
        #--- End: if
 
        if direction:
            # Increasing
            c.subspace[:shift] -= period
            if isbounded:
                b.subspace[:shift] -= period

            if c.Data[0] <= centre - period:
                c += period
                if isbounded:
                    b += period 
        else:
            # Decreasing
            c.subspace[:shift] += period
            if isbounded:
                b.subspace[:shift] += period

            if c.Data[0] >= centre + period:
                c -= period
                if isbounded:
                    b -= period
        #--- End: if 

        c._direction = direction

#
#
#        if self.direction():
#            indices = c > c.subspace[-1]
#        else:
#            indices = c > c.subspace[0]
#
#        c.setdata(c - period, None, indices)
#
#        isbounded = c._hasbounds
#        if isbounded:
#            b = c.bounds
#            if b._hasData:
#                indices.expand_dims(1, i=True)
#                b.setdata(b - period, None, indices)
#            else:
#                isbounded = False
#        #--- End: if
#
#        shift = None
#        if self.direction():
#            # Increasing
#            if c.datum(0) <= centre - period:
#                shift = period
##                c += period
#            elif c.datum(-1) >= centre + period:
#                shift = -period
##                c -= period
#        else:
#            # Decreasing
#            if c.datum(0) >= centre + period:
#                shift = -period
##                c -= period                
#            elif c.datum(-1) <= centre - period:
#                shift = period
##                c += period
#        #--- End: if
#        
#        if shift:
#            c += shift
#            if isbounded:
#                b += shift
#        #--- End: if

        return c
    #--- End: def

#--- End: class


# ====================================================================
#
# AuxiliaryCoordinate object
#
# ====================================================================

class AuxiliaryCoordinate(Coordinate):
    '''

A CF auxiliary coordinate construct.


**Attributes**

===============  ========  ===================================================
Attribute        Type      Description
===============  ========  ===================================================
`!climatology`   ``bool``  Whether or not the bounds are intervals of
                           climatological time. Presumed to be False if unset.
===============  ========  ===================================================

'''
    @property
    def isauxiliary(self):
        '''

True for auxiliary coordinate constructs, False otherwise.

.. seealso:: `ismeasure`, `isdimension`

:Examples:

>>> c.isauxiliary
True

'''
        return True
    #--- End: def

    @property
    def isdimension(self): 
        '''

True for dimension coordinate constructs, False otherwise.

.. seealso::  `isauxiliary`, `ismeasure`

:Examples:

>>> c.isdimension
False

'''
        return False
    #--- End: def
 
    def asauxiliary(self, copy=True):
        '''

Return the auxiliary coordinate.

:Parameters:

    copy : bool, optional   
        If False then the returned auxiliary coordinate is not
        independent. By default the returned auxiliary coordinate is
        independent.

:Returns:

    out : cf.AuxiliaryCoordinate
        The auxiliary coordinate.

:Examples:

>>> d = c.asauxiliary()     
>>> print d is c
True

>>> d = c.asauxiliary(copy=False)
>>> print d == c
True
>>> print d is c
False

'''
        if copy:
            return self.copy()
        
        return self
    #--- End: def

#--- End: class

def _parse_axes(axes):
    if axes is None:
        return axes
    return [(i + ndim if i < 0 else i) for i in axes]
