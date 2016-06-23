from .docstring import format_docstring
from .functions import RTOL, ATOL
from .functions import inspect as cf_inspect
from .utils     import List
#####
# ====================================================================
#
# FieldList object
#
# ====================================================================

class FieldList(List):
    '''

An ordered sequence of fields.

Each element of a field list is a `cf.Field` object.

A field list has all of the callable methods, reserved attributes and
reserved CF properties that a field object has. When used with a field
list, a callable method or a reserved attribute or CF property is
applied independently to each field and, unless a method (or
assignment to a reserved attribute or CF property) carries out an
in-place change to each field, a sequence of the results is returned.
The type of sequence that may be returned will either be a new
`cf.FieldList` object or else a `cf.List` object.

In addition, a field list supports the python list-like operations
(such as indexing and methods like `!append`), but not the python list
arithmetic and comparison behaviours. Any field list arithmetic and
comparison operation is applied independently to each field element,
so all of the operators defined for a field are allowed.

'''

    def __init__(self, fields=None):
        '''

**Initialization**

:Parameters:

    fields : (sequence of) cf.Field, optional
         Create a new field list with these fields.

:Examples:

>>> fl = cf.FieldList()
>>> len(fl)
0
>>> f
<CF Field: air_temperature() K>
>>> fl = cf.FieldList(f)
>>> len(fl
1
>>> fl = cf.FieldList([f, f])
>>> len(fl)
2
>>> fl = cf.FieldList(cf.FieldList([f] * 3))
>>> len(fl)
3
'''
        super(FieldList, self).__init__(fields)
    #--- End: def

    def __array__(self, *dtype):
        '''

Returns a numpy array copy the data array for a single element field
list.

See `cf.Field.__array__`` for details.

:Returns:

    out : numpy.ndarray
        The numpy array copy the data array.

        '''

        
        _list = self._list
        if len(_list) == 1:
            f = _list[0]
            if f._hasData:
                return f.__array__(*dtype)
        #--- End: if

        raise ValueError("%s has no numpy.ndarray interface" %
                         self.__class__.__name__)
    #--- End: def

    @property
    def __data__(self):
        '''

'''        
        _list = self._list
        if len(_list) == 1:
            f = _list[0]
            if f._hasData:
                return f.data
        #--- End: if

        raise ValueError("%s has no cf.Data interface" %
                         self.__class__.__name__)
    #--- End: def

    def __delattr__(self, attr):
        '''

x.__delattr__(attr) <==> del x.attr

'''
        for f in self._list:
            delattr(f, attr)
    #--- End: def

    def __repr__(self):
        '''
x.__repr__() <==> repr(x)

'''
        return repr(self._list).replace('>, ', '>,\n ')
    #--- End: def

    def __str__(self):
        '''
x.__str__() <==> str(x)

'''
        return '\n'.join([str(x) for x in self._list])
    #--- End: def

    def _query_contain(self, value):
        '''
'''
        return type(self)([f._query_contain(value) for f in self._list])

    def _query_set(self, value):
        '''
'''
        return type(self)([f._query_set(value) for f in self._list])
    #--- End: def

    def _query_wi(self, value):
        '''
'''
        return type(self)([f._query_wi(value) for f in self._list])
    #--- End: def

    def _query_wo(self, value):
        '''
'''
        return type(self)([f._query_wo(value) for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------
    @property
    def ancillary_variables(self):
        '''

The `cf.AncillaryVariables` objects containing CF ancillary data for
each field.

``fl.ancillary_variables`` is equivalent to
``cf.List(f.ancillary_variables for f in fl)``.

``fl.ancillary_variables = value`` is equivalent to ``for f in fl:
f.ancillary_variables = value``.

``del fl.ancillary_variables`` is equivalent to ``for f in fl: del
f.ancillary_variables``.

See `cf.Field.ancillary_variables` for details.

        '''
        return List([f.ancillary_variables for f in self._list])
    #--- End: def
    @ancillary_variables.setter
    def ancillary_variables(self, value):
        for f in self._list:
            f.ancillary_variables = value
    #--- End: def
    @ancillary_variables.deleter
    def ancillary_variables(self):
        for f in self._list:
            del f.ancillary_variables
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------
    @property
    def array(self):
        '''

The numpy array deep copy of the data array of each field.

``fl.array`` is equivalent to ``cf.List(f.array for f in fl)``.

See `cf.Field.array` for details.

'''
        return List([f.array for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def attributes(self):
        '''
The dictionaries of the attributes which are not CF properties for each field.

``fl.attributes`` is equivalent to ``cf.List(f.attributes for f in
fl)``.

See `cf.Field.attributes` for details.

        '''
        return List([f.attributes for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def data(self):
        '''
The `cf.Data` objects containing the data array for each field.

``fl.data`` is equivalent to ``cf.List(f.data for f in fl)``.

See `cf.Field.data` for details.

'''
        return List([f.data for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: Data
    # ----------------------------------------------------------------
    @property
    def Data(self):
        '''

The `!Data` attribute of each field.

``fl.Data`` is equivalent to ``cf.List(f.Data for f in fl)``.

``fl.Data = value`` is equivalent to ``for f in fl: f.Data = value``.

``del fl.Data`` is equivalent to ``for f in fl: del f.Data``.

See `cf.Field.Data` for details.

'''
        return List([f.Data for f in self._list])
    #--- End: def
    @Data.setter
    def Data(self, value):
        for f in self._list:
            f.Data = value
    #--- End: def
    @Data.deleter
    def Data(self):
        for f in self._list:
            del f.Data
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------
    @property
    def dtarray(self):
        '''

The `!dtarray` attribute for each field.

``fl.dtarray`` is equivalent to ``cf.List(f.dtarray for f in fl)``.

See `cf.Field.dtarray` for details.

'''
        return List([f.dtarray for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------
    @property
    def dtvarray(self):
        '''

The `!dtvarray` attribute for each field.

``fl.dtvarray`` is equivalent to ``cf.List(f.dtvarray for f in fl)``.

See `cf.Field.dtvarray` for details.

'''
        return List([f.dtvarray for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute:
    # ----------------------------------------------------------------
    @property
    def Flags(self):
        '''

The `!Flags` attribute of each field.

``fl.Flags`` is equivalent to ``cf.List(f.Flags for f in fl)``.

``fl.Flags = value`` is equivalent to ``for f in fl: f.Flags =
value``.

``del fl.Flags`` is equivalent to ``for f in fl: del f.Flags``.

See `cf.Field.Flags` for details.

'''
        return List([f.Flags for f in self._list])
    #--- End: def
    @Flags.setter
    def Flags(self, value):
        for f in self._list:
            f.Flags = value
    #--- End: def
    @Flags.deleter
    def Flags(self):
        for f in self._list:
            del f.Flags
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read-only
    # ----------------------------------------------------------------
    @property
    def day(self):
        '''

The day of each data array element of each field.

``fl.day`` is equivalent to ``cf.FieldList(f.day for f in fl)``.

See `cf.Field.day` for details.

'''
        return type(self)([f.day for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute:
    # ----------------------------------------------------------------
    @property
    def domain(self):
        '''

The `!domain` attribute of each field.

``fl.domain`` is equivalent to ``cf.List(f.domain for f in fl)``.

``fl.domain = value`` is equivalent to ``for f in fl: f.domain =
value``.

``del fl.domain`` is equivalent to ``for f in fl: del f.domain``.

See `cf.Field.domain` for details.

'''
        return List([f.domain for f in self._list])
    #--- End: def
    @domain.setter
    def domain(self, value):
        for f in self._list:
            f.domain = value
    #--- End: def
    @domain.deleter
    def domain(self):
        for f in self._list:
            del f.domain
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute:
    # ----------------------------------------------------------------
    @property
    def dtype(self):
        '''

The `!dtype` attribute for each field.

``fl.dtype`` is equivalent to ``cf.List(f.dtype for f in fl)``.

``fl.dtype = value`` is equivalent to ``for f in fl: f.dtype =
value``.

``del fl.dtype`` is equivalent to ``for f in fl: del f.dtype``.

See `cf.Field.dtype` for details.

'''
        return List([f.dtype for f in self._list])
    #--- End: def
    @dtype.setter
    def dtype(self, value):
        for f in self._list:
            f.dtype = value
    #--- End: def
    @dtype.deleter
    def dtype(self):
        for f in self._list:
            del f.dtype
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def isscalar(self):
        '''

The `!isscalar` attribute of each field.

``fl.isscalar`` is equivalent to ``cf.List(f.isscalar for f in fl)``.

See `cf.Field.isscalar` for details.

'''
        return List([f.isscalar for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute:
    # ----------------------------------------------------------------
    @property
    def hardmask(self):
        '''

The `!hardmask` attribute of each field.

``fl.hardmask`` is equivalent to ``cf.List(f.hardmask for f in fl)``.

``fl.hardmask = value`` is equivalent to ``for f in fl: f.hardmask =
value``.

See `cf.Field.hardmask` for details.

'''
        return List([f.hardmask for f in self._list])
    #--- End: def
    @hardmask.setter
    def hardmask(self, value):
        for f in self._list:
            f.hardmask = value
    #--- End: def
    @hardmask.deleter
    def hardmask(self):
        for f in self._list:
            del f.hardmask
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def hasbounds(self):
        '''

Whether or not each field has cell bounds.

``fl.hasbounds`` is equivalent to ``cf.List(f.hasbounds for f in
fl)``.

See `cf.Field.hasbounds` for details.

'''
        return List([f.hasbounds for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def hour(self):
        '''

The hour of each data array element of each field.

``fl.hour`` is equivalent to ``cf.FieldList(f.hour for f in fl)``.

See `cf.Field.hour` for details.

'''
        return type(self)([f.hour for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def mask(self):
        '''

The `!mask` attribute of each field.

``fl.mask`` is equivalent to ``cf.FieldList(f.mask for f in fl)``.

See `cf.Field.mask` for details.

'''
        return type(self)([f.mask for f in self._list])
    #--- End: def

    def max(self):
         '''

The maximum of the data array for each field.

``fl.max()`` is equivalent to ``cf.List(f.max() for f in fl)``.

see ``cf.field.max`` for details.

.. seealso:: `collapse`

'''
         return List([f.max() for f in self._list])
    #--- End: def

    def mid_range(self):
         '''

The mid-range of the data array for each field.

``fl.mid_range()`` is equivalent to ``cf.List(f.mid_range() for f in fl)``.

see ``cf.field.mid_range`` for details.

.. seealso:: `collapse`

'''
         return List([f.mid_range() for f in self._list])
    #--- End: def

    def range(self):
         '''

The mid-range of the data array for each field.

``fl.range()`` is equivalent to ``cf.List(f.range() for f in fl)``.

see ``cf.field.mid_range`` for details.

.. seealso:: `collapse`

'''
         return List([f.range() for f in self._list])
    #--- End: def

    def min(self):
         '''

The minimum of the data array for each field.

``fl.min()`` is equivalent to ``cf.List(f.min() for f in fl)``.

see ``cf.field.min`` for details.

.. seealso:: `collapse`

'''
         return List([f.min() for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def minute(self):
        '''

The minute of each data array element of each field.

``fl.minute`` is equivalent to ``cf.FieldList(f.minute for f in fl)``.

See `cf.Field.minute` for details.

'''
        return type(self)([f.minute for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def month(self):
        '''

The minute of each data array element of each field.

``fl.month`` is equivalent to ``cf.FieldList(f.month for f in fl)``.

See `cf.Field.month` for details.

'''
        return type(self)([f.month for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def properties(self):
        '''

The `!properties` attribute of each field.

``fl.properties`` is equivalent to ``cf.List(f.properties for f in
fl)``.

See `cf.Field.properties` for details.

'''
        return List([f.properties for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def ndim(self):
        '''

The number of dimensions in the data array of each field.

``fl.ndim`` is equivalent to ``cf.List(f.ndim for f in fl)``.

See `cf.Field.ndim` for details.

'''
        return List([f.ndim for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def second(self):
        '''

The minute of each data array element of each field.

``fl.second`` is equivalent to ``cf.FieldList(f.second for f in fl)``.

See `cf.Field.second` for details.

'''
        return type(self)([f.second for f in self._list])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: shape (read only)
    # ----------------------------------------------------------------
    @property
    def shape(self):
        '''The shape of the the data array of each field.

``fl.shape`` is equivalent to ``cf.List(f.shape for f in fl)``.

See `cf.Field.shape` for details.

        '''
        return List([f.shape for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: size (read only)
    # ----------------------------------------------------------------
    @property
    def size(self):
        '''
The number of elements in the data array of each field.

``fl.size`` is equivalent to ``cf.List(f.size for f in fl)``.

See `cf.Field.size` for details.

'''
        return List([f.size for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def T(self):
        '''

Returns False for each field.

``fl.T`` is equivalent to ``cf.List(f.T for f in fl)``.

See `cf.Field.T` for details.

'''              
        return List([f.T for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def unique(self):
        '''

The unique elements of the data array for each field.

``fl.unique`` is equivalent to ``cf.List(f.unique for f in fl)``.

See `cf.Field.unique` for details.

'''              
        return List([f.unique for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def X(self):
        '''

Returns False for each field.

``fl.X`` is equivalent to ``cf.List(f.X for f in fl)``.

See `cf.Field.X` for details.

'''              
        return List([f.X for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def Y(self):
        '''

Returns False for each field.

``fl.Y`` is equivalent to ``cf.List(f.Y for f in fl)``.

See `cf.Field.Y` for details.

'''              
        return List([f.Y for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def Z(self):
        '''

Returns False for each field.

``fl.Z`` is equivalent to ``cf.List(f.Z for f in fl)``.

See `cf.Field.Z` for details.

'''              
        return List([f.Z for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: Units
    # ----------------------------------------------------------------
    @property
    def Units(self):
        '''

The `cf.Units` objects containing the units of the data array of each
field.

``fl.Units`` is equivalent to ``cf.List(f.Units for f in fl)``.

``fl.Units = value`` is equivalent to ``for f in fl: f.Units =
value``.

``del fl.Units`` is equivalent to ``for f in fl: del f.Units``.

See `cf.Field.Units` for details.

        '''
        return List([f.Units for f in self._list])
    #--- End: def
    @Units.setter
    def Units(self, value):
        for f in self._list:
            f.Units = value
    #--- End: def
    @Units.deleter
    def Units(self):
        for f in self._list:
            del f.Units
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: varray
    # ----------------------------------------------------------------
    @property
    def varray(self):
        '''

The `!varray` attribute for each field.

``fl.varray`` is equivalent to ``cf.List(f.varray for f in fl)``.

See `cf.Field.varray` for details.

'''
        return List([f.varray for f in self._list])    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def year(self):
        '''

The year of each data array element of each field.

``fl.year`` is equivalent to ``cf.FieldList(f.year for f in fl)``.

See `cf.Field.year` for details.

'''
        return type(self)([f.year for f in self._list])
    #--- End: def

    #--------------------------------------------------------
    # CF property: flag_masks
    # ----------------------------------------------------------------
    @property
    def flag_masks(self):
        '''

The `!flag_masks` CF property of each field.

``fl.flag_masks`` is equivalent to ``cf.List(f.flag_masks for f in
fl)``.

``fl.flag_masks = value`` is equivalent to ``for f in fl: f.flag_masks
= value``.

``del fl.flag_masks`` is equivalent to ``for f in fl: del
f.flag_masks``.

See `cf.Field.flag_masks` for details.

'''
        return List([f.flag_masks for f in self._list])    
    #--- End: def
    @flag_masks.setter
    def flag_masks(self, value): 
        for f in self._list:
            f.flag_masks = value
    #--- End: def
    @flag_masks.deleter
    def flag_masks(self):
        for f in self._list:
            del f.flag_masks
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: flag_meanings
    # ----------------------------------------------------------------
    @property
    def flag_meanings(self):
        '''

The `!flag_meanings` CF property of each field.

``fl.flag_meanings`` is equivalent to ``cf.List(f.flag_meanings for f
in fl)``.

``fl.flag_meanings = value`` is equivalent to ``for f in fl:
f.flag_meanings = value``.

``del fl.flag_meanings`` is equivalent to ``for f in fl: del
f.flag_meanings``.

See `cf.Field.flag_meanings` for details.

'''
        return List([f.flag_meanings for f in self._list])    
    #--- End: def
    @flag_meanings.setter
    def flag_meanings(self, value): 
        for f in self._list:
            f.flag_meanings = value
    #--- End: def
    @flag_meanings.deleter
    def flag_meanings(self):
        for f in self._list:
            del f.flag_meanings
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: flag_values
    # ----------------------------------------------------------------
    @property
    def flag_values(self):
        '''

The `!flag_values` CF property of each field.

``fl.flag_values`` is equivalent to ``cf.List(f.flag_values for f in
fl)``.

``fl.flag_values = value`` is equivalent to ``for f in fl:
f.flag_values = value``.

``del fl.flag_values`` is equivalent to ``for f in fl: del
f.flag_values``.

See `cf.Field.flag_values` for details.

'''
        return List([f.flag_values for f in self._list])    
    #--- End: def
    @flag_values.setter
    def flag_values(self, value): 
        for f in self._list:
            f.flag_values = value
    #--- End: def
    @flag_values.deleter
    def flag_values(self):
        for f in self._list:
            del f.flag_values
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: comment
    # ----------------------------------------------------------------
    @property
    def comment(self):
        '''

The `!comment` CF property of each field.

``fl.comment`` is equivalent to ``cf.List(f.comment for f in fl)``.

``fl.comment = value`` is equivalent to ``for f in fl: f.comment =
 value``.

``del fl.comment`` is equivalent to ``for f in fl: del f.comment``.

See `cf.Field.comment` for details.

'''
        return List([f.comment for f in self._list])    
    #--- End: def
    @comment.setter
    def comment(self, value): 
        for f in self._list:
            f.comment = value
    #--- End: def
    @comment.deleter
    def comment(self):
        for f in self._list:
            del f.comment
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: _FillValue
    # ----------------------------------------------------------------
    @property
    def _FillValue(self):
        '''

The `!_FillValue` CF property of each field.

``fl._FillValue`` is equivalent to ``cf.List(f._FillValue for f in
fl)``.

``fl._FillValue = value`` is equivalent to ``for f in fl: f._FillValue
= value``.

``del fl._FillValue`` is equivalent to ``for f in fl: del
f._FillValue``.

See `cf.Field._FillValue` for details.

'''
        return List([f._FillValue for f in self._list])    
    #--- End: def
    @_FillValue.setter
    def _FillValue(self, value): 
        for f in self._list:
            f._FillValue = value
    #--- End: def
    @_FillValue.deleter
    def _FillValue(self):
        for f in self._list:
            del f._FillValue
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: history
    # ----------------------------------------------------------------
    @property
    def history(self):
        '''

The `!history` CF property of each field.

``fl.history`` is equivalent to ``cf.List(f.history for f in fl)``.

``fl.history = value`` is equivalent to ``for f in fl: f.history =
value``.

``del fl.history`` is equivalent to ``for f in fl: del f.history``.

See `cf.Field.history` for details.

'''
        return List([f.history for f in self._list])    
    #--- End: def
    @history.setter
    def history(self, value): 
        for f in self._list:
            f.history = value
    #--- End: def
    @history.deleter
    def history(self):
        for f in self._list:
            del f.history
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: add_offset
    # ----------------------------------------------------------------
    @property
    def add_offset(self):
        '''

The `!add_offset` CF property of each field.

``fl.add_offset`` is equivalent to ``cf.List(f.add_offset for f in
fl)``.

``fl.add_offset = value`` is equivalent to ``for f in fl: f.add_offset
= value``.

``del fl.add_offset`` is equivalent to ``for f in fl: del
f.add_offset``.

See `cf.Field.add_offset` for details.

'''
        return List([f.add_offset for f in self._list])    
    #--- End: def
    @add_offset.setter
    def add_offset(self, value): 
        for f in self._list:
            f.add_offset = value
    #--- End: def
    @add_offset.deleter
    def add_offset(self):
        for f in self._list:
            del f.add_offset
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: calendar
    # ----------------------------------------------------------------
    @property
    def calendar(self):
        '''

The `!calendar` CF property of each field.

``fl.calendar`` is equivalent to ``cf.List(f.calendar for f in fl)``.

``fl.calendar = value`` is equivalent to ``for f in fl: f.calendar =
value``.

``del fl.calendar`` is equivalent to ``for f in fl: del f.calendar``.

See `cf.Field.calendar` for details.

'''
        return List([f.calendar for f in self._list])    
    #--- End: def
    @calendar.setter
    def calendar(self, value): 
        for f in self._list:
            f.calendar = value
    #--- End: def
    @calendar.deleter
    def calendar(self):
        for f in self._list:
            del f.calendar
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: cell_methods
    # ----------------------------------------------------------------
    @property
    def cell_methods(self):
        '''

The `!cell_methods` CF property of each field.

``fl.cell_methods`` is equivalent to ``cf.List(f.cell_methods for f in
fl)``.

``fl.cell_methods = value`` is equivalent to ``for f in fl:
f.cell_methods = value``.

``del fl.cell_methods`` is equivalent to ``for f in fl: del
f.cell_methods``.

See `cf.Field.cell_methods` for details.

'''
        return List([f.cell_methods for f in self._list])    
    #--- End: def
    @cell_methods.setter
    def cell_methods(self, value): 
        for f in self._list:
            f.cell_methods = value
    #--- End: def
    @cell_methods.deleter
    def cell_methods(self):
        for f in self._list:
            del f.cell_methods
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: Conventions
    # ----------------------------------------------------------------
    @property
    def Conventions(self):
        '''

The `!Conventions` CF property of each field.

``fl.Conventions`` is equivalent to ``cf.List(f.Conventions for f in
fl)``.

``fl.Conventions = value`` is equivalent to ``for f in fl:
f.Conventions = value``.

``del fl.Conventions`` is equivalent to ``for f in fl: del
f.Conventions``.

See `cf.Field.Conventions` for details.

'''
        return List([f.Conventions for f in self._list])    
    #--- End: def
    @Conventions.setter
    def Conventions(self, value): 
        for f in self._list:
            f.Conventions = value
    #--- End: def
    @Conventions.deleter
    def Conventions(self):
        for f in self._list:
            del f.Conventions
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: institution
    # ----------------------------------------------------------------
    @property
    def institution(self):
        '''

The `!institution` CF property of each field.

``fl.institution`` is equivalent to ``cf.List(f.institution for f in
fl)``.

``fl.institution = value`` is equivalent to ``for f in fl:
f.institution = value``.

``del fl.institution`` is equivalent to ``for f in fl: del
f.institution``.

See `cf.Field.institution` for details.

'''
        return List([f.institution for f in self._list])    
    #--- End: def
    @institution.setter
    def institution(self, value): 
        for f in self._list:
            f.institution = value
    #--- End: def
    @institution.deleter
    def institution(self):
        for f in self._list:
            del f.institution
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: leap_month
    # ----------------------------------------------------------------
    @property
    def leap_month(self):
        '''

The `!leap_month` CF property of each field.

``fl.leap_month`` is equivalent to ``cf.List(f.leap_month for f in
fl)``.

``fl.leap_month = value`` is equivalent to ``for f in fl: f.leap_month
= value``.

``del fl.leap_month`` is equivalent to ``for f in fl: del
f.leap_month``.

See `cf.Field.leap_month` for details.

'''
        return List([f.leap_month for f in self._list])    
    #--- End: def
    @leap_month.setter
    def leap_month(self, value): 
        for f in self._list:
            f.leap_month = value
    #--- End: def
    @leap_month.deleter
    def leap_month(self):
        for f in self._list:
            del f.leap_month
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: leap_year
    # ----------------------------------------------------------------
    @property
    def leap_year(self):
        '''

The `!leap_year` CF property of each field.

``fl.leap_year`` is equivalent to ``cf.List(f.leap_year for f in
fl)``.

``fl.leap_year = value`` is equivalent to ``for f in fl: f.leap_year =
value``.

``del fl.leap_year`` is equivalent to ``for f in fl: del
f.leap_year``.

See `cf.Field.leap_year` for details.

'''
        return List([f.leap_year for f in self._list])    
    #--- End: def
    @leap_year.setter
    def leap_year(self, value): 
        for f in self._list:
            f.leap_year = value
    #--- End: def
    @leap_year.deleter
    def leap_year(self):
        for f in self._list:
            del f.leap_year
    #--- End: def


    # ----------------------------------------------------------------
    # CF property: long_name
    # ----------------------------------------------------------------
    @property
    def long_name(self):
        '''

The `!long_name` CF property of each field.

``fl.long_name`` is equivalent to ``cf.List(f.long_name for f in
fl)``.

``fl.long_name = value`` is equivalent to ``for f in fl: f.long_name =
value``.

``del fl.long_name`` is equivalent to ``for f in fl: del
f.long_name``.

See `cf.Field.long_name` for details.

'''
        return List([f.long_name for f in self._list])    
    #--- End: def
    @long_name.setter
    def long_name(self, value): 
        for f in self._list:
            f.long_name = value
    #--- End: def
    @long_name.deleter
    def long_name(self):
        for f in self._list:
            del f.long_name
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: missing_value
    # ----------------------------------------------------------------
    @property
    def missing_value(self):
        '''

The `!missing_value` CF property of each field.

``fl.missing_value`` is equivalent to ``cf.List(f.missing_value for f
in fl)``.

``fl.missing_value = value`` is equivalent to ``for f in fl:
f.missing_value = value``.

``del fl.missing_value`` is equivalent to ``for f in fl: del
f.missing_value``.

See `cf.Field.missing_value` for details.

'''
        return List([f.missing_value for f in self._list])    
    #--- End: def
    @missing_value.setter
    def missing_value(self, value): 
        for f in self._list:
            f.missing_value = value
    #--- End: def
    @missing_value.deleter
    def missing_value(self):
        for f in self._list:
            del f.missing_value
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: month_lengths
    # ----------------------------------------------------------------
    @property
    def month_lengths(self):
        '''

The `!month_lengths` CF property of each field.

``fl.month_lengths`` is equivalent to ``cf.List(f.month_lengths for f
in fl)``.

``fl.month_lengths = value`` is equivalent to ``for f in fl:
f.month_lengths = value``.

``del fl.month_lengths`` is equivalent to ``for f in fl: del
f.month_lengths``.

See `cf.Field.month_lengths` for details.

'''
        return List([f.month_lengths for f in self._list])    
    #--- End: def
    @month_lengths.setter
    def month_lengths(self, value): 
        for f in self._list:
            f.month_lengths = value
    #--- End: def
    @month_lengths.deleter
    def month_lengths(self):
        for f in self._list:
            del f.month_lengths
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: references
    # ----------------------------------------------------------------
    @property
    def references(self):
        '''

The `!references` CF property of each field.

``fl.references`` is equivalent to ``cf.List(f.references for f in
fl)``.

``fl.references = value`` is equivalent to ``for f in fl: f.references
= value``.

``del fl.references`` is equivalent to ``for f in fl: del
f.references``.

See `cf.Field.references` for details.

'''
        return List([f.references for f in self._list])    
    #--- End: def
    @references.setter
    def references(self, value): 
        for f in self._list:
            f.references = value
    #--- End: def
    @references.deleter
    def references(self):
        for f in self._list:
            del f.references
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: scale_factor
    # ----------------------------------------------------------------
    @property
    def scale_factor(self):
        '''

The `!scale_factor` CF property of each field.

``fl.scale_factor`` is equivalent to ``cf.List(f.scale_factor for f in
fl)``.

``fl.scale_factor = value`` is equivalent to ``for f in fl:
f.scale_factor = value``.

``del fl.scale_factor`` is equivalent to ``for f in fl: del
f.scale_factor``.

See `cf.Field.scale_factor` for details.

'''
        return List([f.scale_factor for f in self._list])    
    #--- End: def
    @scale_factor.setter
    def scale_factor(self, value): 
        for f in self._list:
            f.scale_factor = value
    #--- End: def
    @scale_factor.deleter
    def scale_factor(self):
        for f in self._list:
            del f.scale_factor
    #--- End: def


    # ----------------------------------------------------------------
    # CF property: source
    # ----------------------------------------------------------------
    @property
    def source(self):
        '''

The `!source` CF property of each field.

``fl.source`` is equivalent to ``cf.List(f.source for f in fl)``.

``fl.source = value`` is equivalent to ``for f in fl: f.source =
value``.

``del fl.source`` is equivalent to ``for f in fl: del f.source``.

See `cf.Field.source` for details.

'''
        return List([f.source for f in self._list])    
    #--- End: def
    @source.setter
    def source(self, value): 
        for f in self._list:
            f.source = value
    #--- End: def
    @source.deleter
    def source(self):
        for f in self._list:
            del f.source
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: standard_error_multiplier
    # ----------------------------------------------------------------
    @property
    def standard_error_multiplier(self):
        '''

The `!standard_error_multiplier` CF property of each field.

``fl.standard_error_multiplier`` is equivalent to
``cf.List(f.standard_error_multiplier for f in fl)``.

``fl.standard_error_multiplier = value`` is equivalent to ``for f in
fl: f.standard_error_multiplier = value``.

``del fl.standard_error_multiplier`` is equivalent to ``for f in fl:
del f.standard_error_multiplier``.

See `cf.Field.standard_error_multiplier` for details.

'''
        return List([f.standard_error_multiplier for f in self._list])    
    #--- End: def
    @standard_error_multiplier.setter
    def standard_error_multiplier(self, value): 
        for f in self._list:
            f.standard_error_multiplier = value
    #--- End: def
    @standard_error_multiplier.deleter
    def standard_error_multiplier(self):
        for f in self._list:
            del f.standard_error_multiplier
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: standard_name
    # ----------------------------------------------------------------
    @property
    def standard_name(self):
        '''

The `!standard_name` CF property of each field.

``fl.standard_name`` is equivalent to ``cf.List(f.standard_name for f
in fl)``.

``fl.standard_name = value`` is equivalent to ``for f in fl:
f.standard_name = value``.

``del fl.standard_name`` is equivalent to ``for f in fl: del
f.standard_name``.

See `cf.Field.standard_name` for details.

'''
        return List([f.standard_name for f in self._list])    
    #--- End: def
    @standard_name.setter
    def standard_name(self, value): 
        for f in self._list:
            f.standard_name = value
    #--- End: def
    @standard_name.deleter
    def standard_name(self):
        for f in self._list:
            del f.standard_name
    #--- End: def


    # ----------------------------------------------------------------
    # CF property: title
    # ----------------------------------------------------------------
    @property
    def title(self):
        '''

The `!title` CF property of each field.

``fl.title`` is equivalent to ``cf.List(f.title for f in fl)``.

``fl.title = value`` is equivalent to ``for f in fl: f.title =
value``.

``del fl.title`` is equivalent to ``for f in fl: del f.title``.

See `cf.Field.title` for details.

'''
        return List([f.title for f in self._list])    
    #--- End: def
    @title.setter
    def title(self, value): 
        for f in self._list:
            f.title = value
    #--- End: def
    @title.deleter
    def title(self):
        for f in self._list:
            del f.title
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: units
    # ----------------------------------------------------------------
    @property
    def units(self):
        '''

The `!units` CF property of each field.

``fl.units`` is equivalent to ``cf.List(f.units for f in fl)``.

``fl.units = value`` is equivalent to ``for f in fl: f.units =
value``.

``del fl.units`` is equivalent to ``for f in fl: del f.units``.

See `cf.Field.units` for details.

'''
        return List([f.units for f in self._list])    
    #--- End: def
    @units.setter
    def units(self, value): 
        for f in self._list:
            f.units = value
    #--- End: def
    @units.deleter
    def units(self):
        for f in self._list:
            del f.units
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: valid_max
    # ----------------------------------------------------------------
    @property
    def valid_max(self):
        '''

The `!valid_max` CF property of each field.

``fl.valid_max`` is equivalent to ``cf.List(f.valid_max for f in
fl)``.

``fl.valid_max = value`` is equivalent to ``for f in fl: f.valid_max =
value``.

``del fl.valid_max`` is equivalent to ``for f in fl: del
f.valid_max``.

See `cf.Field.valid_max` for details.

'''
        return List([f.valid_max for f in self._list])    
    #--- End: def
    @valid_max.setter
    def valid_max(self, value): 
        for f in self._list:
            f.valid_max = value
    #--- End: def
    @valid_max.deleter
    def valid_max(self):
        for f in self._list:
            del f.valid_max
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: valid_min
    # ----------------------------------------------------------------
    @property
    def valid_min(self):
        '''

The `!valid_min` CF property of each field.

``fl.valid_min`` is equivalent to ``cf.List(f.valid_min for f in
fl)``.

``fl.valid_min = value`` is equivalent to ``for f in fl: f.valid_min =
value``.

``del fl.valid_min`` is equivalent to ``for f in fl: del
f.valid_min``.

See `cf.Field.valid_min` for details.

'''
        return List([f.valid_min for f in self._list])    
    #--- End: def
    @valid_min.setter
    def valid_min(self, value): 
        for f in self._list:
            f.valid_min = value
    #--- End: def
    @valid_min.deleter
    def valid_min(self):
        for f in self._list:
            del f.valid_min
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: valid_range
    # ----------------------------------------------------------------
    @property
    def valid_range(self):
        '''

The `!valid_range` CF property of each field.

``fl.valid_range`` is equivalent to ``cf.List(f.valid_range for f in
fl)``.

``fl.valid_range = value`` is equivalent to ``for f in fl:
f.valid_range = value``.

``del fl.valid_range`` is equivalent to ``for f in fl: del
f.valid_range``.

See `cf.Field.valid_range` for details.

'''
        return List([f.valid_range for f in self._list])    
    #--- End: def
    @valid_range.setter
    def valid_range(self, value): 
        for f in self._list:
            f.valid_range = value
    #--- End: def
    @valid_range.deleter
    def valid_range(self):
        for f in self._list:
            del f.valid_range
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def subspace(self):
        '''

Subspace each field in the list, returning a new list of fields.

Subspacing by data array indices or by coordinate values are both
allowed.

:Examples:

>>> fl
[<CF Variable: air_temperature(73, 96)>,
 <CF Variable: air_temperature(73, 96)>]
>>> fl.subspace[0,0]
[<CF Variable: air_temperature(1,1)>,
 <CF Variable: air_temperature(1,1)>]
>>> fl.slice(longitude=0, latitude=0)
[<CF Variable: air_temperature(1,1)>,
 <CF Variable: air_temperature(1,1)>]

'''
        return SubspaceFieldList(self)
    #--- End: def

    def sum(self):
         '''

The sum of the data array for each field.

``fl.sum()`` is equivalent to ``cf.List(f.sum() for f in fl)``.

See ``cf.field.sum`` for details.

.. seealso:: `collapse`

'''
         return List([f.sum() for f in self._list])
    #--- End: def

    def sd(self):
         '''

The standard deviation of the data array for each field.

``fl.sd()`` is equivalent to ``cf.List(f.sd() for f in fl)``.

See ``cf.field.sd`` for details.

.. seealso:: `collapse`

'''
         return List([f.sd() for f in self._list])
    #--- End: def

    def var(self):
         '''

The variance of the data array for each field.

``fl.var()`` is equivalent to ``cf.List(f.var() for f in fl)``.

See ``cf.field.var`` for details.

.. seealso:: `collapse`

'''
         return List([f.var() for f in self._list])
    #--- End: def

    def sample_size(self):
         '''

The number of non-missing data elements in the data array for each
field.

``fl.sample_size()`` is equivalent to ``cf.List(f.sample_size() for f in fl)``.

See ``cf.field.sample_size`` for details.

.. seealso:: `collapse`

         '''
         return List([f.sample_size() for f in self._list])
    #--- End: def

    def all(self):
        '''

Test whether all data array elements evaluate to True for each field.

``fl.all()`` is equivalent to ``cf.List(f.all() for f in fl)``.

See ``cf.field.all`` for details.

:Returns:

    out : cf.List

'''
        return List([f.all() for f in self._list])
    #--- End: def

    def anchor(self,  axis, value, i=False, _dry_run=False, **kwargs):
        '''

Roll a cyclic axis of each field so that the given value lies in the
first coordinate cell.

``fl.anchor()`` is equivalent to ``cf.FieldList(f.anchor() for f in
fl)``.

See `cf.Field.anchor` for details.

:Parameters:

    axis, kwargs : *optional*
        Select the unique axis which would be selected by this call of
        the field's `axes` method: ``f.axes(axis, **kwargs)``. See
        `cf.Field.axes` for details.
  
    value : data-like
        Anchor the dimension coordinate values for the selected
        cyclic axis to this value. See `cf.Field.anchor` for details.

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

    _dry_run : bool, optional
        Return a dictionary of parameters which describe the anchoring
        process. See `cf.Field.anchor` for details.

:Returns:

    out : cf.FieldList

:Examples:

        '''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.anchor(axis, value, i=True, _dry_run=_dry_run, **kwargs)

        return fl
    #--- End: def

    def any(self):
        '''

Test whether any data array elements evaluate to True for each field.

``fl.any()`` is equivalent to ``cf.List(f.any() for f in fl)``.

See ``cf.field.any`` for details.

:Returns:

    out : cf.List

'''
        return List([f.any() for f in self._list])
    #--- End: def

    def aux(self, items=None, axes=None, axes_all=None,
            axes_subset=None, axes_superset=None, exact=False,
            inverse=False, match_and=True, ndim=None,
            key=False, copy=False):
        '''+def_aux

:Returns:

    out : cf.List   
        For each field, the unique auxiliary coordinate object or its
        domain identifier or, if there isn't a unique item, None.

        '''
        return List([f.aux(items=items, axes=axes, axes_all=axes_all,
                           axes_subset=axes_subset,
                           axes_superset=axes_superset, ndim=ndim,
                           exact=exact, inverse=inverse,
                           match_and=match_and, key=key, copy=copy)
                     for f in self._list])
    #--- End: def  
    format_docstring(aux, item='auxiliary coordinate',
                     identity='~cf.AuxiliaryCoordinate.identity')

    def auxs(self, items=None, **kwargs):
        '''Return auxiliary coordinate objects from each field.

``fl.auxs()`` is equivalent to ``cf.List(f.auxs() for f in fl)``.

See `cf.Field.auxs` for details.

:Parameters:

    items, kwargs : *optional*
        See `cf.Field.auxs` for details.
  
:Returns:

    out : cf.List of dicts
        For each field, a dictionary whose keys are domain item
        identifiers with corresponding values of auxiliary coordinate
        objects.

        '''
        return List([f.auxs(items=items, **kwargs) for f in self._list])
    #--- End: def

    def axes(self, axes=None, ordered=False, size=None, **kwargs):
        '''Return domain axis identifiers from each field.

``fl.axes()`` is equivalent to ``cf.List(f.axes() for f in fl)``.

See `cf.Field.axes` for details.

:Parameters:

    axes, kwargs : *optional*
        Select axes. See `cf.Field.axes` for details.

    ordered : bool, optional
        Return ordered lists of axes instead of an unordered sets. See
        `cf.Field.axes` for details.

    size :  int or cf.Query, optional
        Select axes whose sizes equal *size*. See `cf.Field.axes` for
        details.

:Returns:

    out : cf.List
        For each field, a set of domain axis identifiers, or a list if
        ordered is True.

        '''
        return List([f.axes(axes=axes, ordered=ordered, size=size, **kwargs)
                     for f in self._list])
    #--- End: def

    def axes_sizes(self, axes=None, size=None, key=False, **kwargs):
        '''{+def_axes_sizes}

:Returns:
    
    out : cf.List
        The sizes of the axes.

:Examples 2: 

'''
        return List([f.axes_sizes(axes=axes, size=size, key=key, **kwargs)
                     for f in self._list])
    #---End: def
    format_docstring(axes_sizes)

    def axis(self, axes=None, size=None, **kwargs):
        '''{+def_axis}

:Returns:
  
    out : cf.List
       
:Examples 2:
'''
        return List([f.axis(axes=axes, size=size, **kwargs)
                     for f in self._list])
    #---End: def
    format_docstring(axis)

    def binary_mask(self):
        '''

Return a binary (0 and 1) missing data mask for each field.

``fl.binary_mask()`` is equivalent to ``cf.List(f.binary_mask() for f
in fl)``.

See `cf.Field.binary_mask` for details.

:Returns:

    out : cf.FieldList
        The binary missing data mask for each field.

'''
        return type(self)([f.binary_mask() for f in self._list])
    #--- End: def

    def ceil(self, i=False):
        '''{+def_ceil}

:Examples 2:

See `cf.Field.ceil` for further examples.
''' 
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.ceil(i=True)

        return fl
    #--- End: def
    format_docstring(ceil)

    def chunk(self, *args, **kwargs):
        '''Partition the data array for each field.

``fl.chunk()`` is equivalent to ``for f in fl: f.chunk()``.

:Parameters:

    args, kwargs : *optional*
        See `cf.Field.chunk` for details.

:Returns:

    None

        '''
        for f in self._list:
            f.chunk(*args, **kwargs)
    #--- End: def

    def clip(self, a_min, a_max, units=None, i=False):
        '''Clip (limit) the values in the data array for each field.

``fl.clip()`` is equivalent to ``cf.FieldList(f.clip() for f in fl)``.

See `cf.Field.clip` for details.

:Parameters:

    a_min : scalar

    a_max : scalar

    units : str or Units, optional

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

        '''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.clip(a_min, a_max, units=units, i=True)

        return fl
    #--- End: def

    def close(self):
        '''

Close all referenced open data files from each field.

``fl.close()`` is equivalent to ``for f in fl: f.close()``.

See `cf.Field.close` for details.

:Returns:

    None

'''  
        for f in self._list:
            f.close()
    #--- End: def

    def measure(self,  item=None, key=False, **kwargs):
        '''Return a cell measure object, or its domain identifier, from each
field.

``fl.measure()`` is equivalent to ``cf.List(f.measure() for f in
fl)``.

See `cf.Field.measure` for details.

:Parameters:

    item, kwargs : *optional*
        See `cf.Field.measure` for details.
  
    key : bool, optional
  
:Returns:

    out : cf.List   
        For each field, the unique cell measure object or its domain
        identifier or, if there isn't a unique item, None.

        '''
        return List([f.measure(item=item, key=key, **kwargs) for f in self._list])
    #--- End: def

    def measures(self, items=None, **kwargs):
        '''Return cell measure objects from each field.

``fl.measures()`` is equivalent to ``cf.List(f.measures() for f in
fl)``.

See `cf.Field.measures` for details.

:Parameters:

    items, kwargs : *optional*
        See `cf.Field.measures` for details.
  
:Returns:

    out : cf.List of dicts
        For each field, a dictionary whose keys are domain item
        identifiers with corresponding values of cell measure objects.

        '''
        return List([f.measures(items=items, **kwargs) for f in self._list])
    #--- End: def

    def collapse(self, method, axes=None, squeeze=False, mtol=1,
                 weights='auto', ddof=1, a=None, i=False, group=None,
                 regroup=False, within_days=None, within_years=None,
                 over_days=None, over_years=None,
                 coordinate='mid_range', group_by='coords', **kwargs):
        '''

Collapse axes of each field by statistical calculations.

``fl.collapse()`` is equivalent to ``cf.FieldList(f.collapse() for f
in fl)``.

See `cf.Field.collapse` for details.

:Parameters:

    method : str or cf.Cellmethods
        Define the collapse method.See `cf.Field.collapse` for
        details.

    axes, kwargs : optional 
        The axes to be collapsed. See `cf.Field.collapse` for details.

    weights : *optional*
        Specify the weights for the collapse. See `cf.Field.collapse`
        for details.

    squeeze : bool, optional
        If True then collapsed axes are removed from the data
        array. See `cf.Field.collapse` for details.

    mtol : number, optional
        For each element in the output data array, the fraction of
        contributing input array elements which is allowed to contain
        missing data. See `cf.Field.collapse` for details.

    ddof : number, *optional*
        The delta degrees of freedom in the calculation of a standard
        deviation or variance. See `cf.Field.collapse` for details.

    a : *optional*
        Specify the value of :math:`a` in the calculation of a
        weighted standard deviation or variance when *ddof* is greater
        than 0. See `cf.Field.collapse` for details.

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList
        The collapsed fields.

        '''
        if i:
            fl = self
        else:
            fl = self.copy()
            
        for f in fl._list:
            f.collapse(method, axes=axes, squeeze=squeeze, mtol=mtol,
                       weights=weights, ddof=ddof, a=a, group=group,
                       regroup=regroup, within_days=within_days, within_years=within_years,
                       over_days=over_days, over_years=over_years,
                       coordinate=coordinate, group_by=group_by, i=True, **kwargs)

        return fl
    #--- End: def

    def concatenate(self, axis=0, _preserve=True):
        '''Join the sequence of fields together.

The concatenation of the fields in the field list is carried out in
order. Each field must have equivalent units and the same shape,
except in the concatenation axis of their data arrays.

.. seealso:: `cf.aggregate`, `cf.Data.concatenate`

:Parameters:

    axis : int, optional
        The position of the data array axis along which the fields
        will be joined. The default is 0.

    _preserve : bool, optional 
        If False then the time taken to do the concatenation is
        reduced at the expense of changing the fields in place and
        **these in place changes will render the fields
        unusable**. Therefore, only set to False if it is 100% certain
        that the fields will not be accessed again. By default the
        fields are preserved.

:Returns:

    out : cf.Field

:Examples:

        '''         
        return self._list[0].concatenate(self._list, axis=axis,
                                         _preserve=_preserve)
    #--- End: def

    def coord(self, item=None, key=False, **kwargs):
        '''Return a dimension or auxiliary coordinate object, or its domain
identifier, from each field.

``fl.coord()`` is equivalent to ``cf.List(f.coord() for f in fl)``.

See `cf.Field.coord` for details.

:Parameters:

    item, kwargs : *optional*
        See `cf.Field.coord`for details.
  
    key : bool, optional
        If True then return the domain's identifier for the item,
        rather than the item itself. See `cf.Field.coord` for details.

:Returns:

    out : cf.List   
        For each field, the unique dimension or auxiliary coordinate
        object or its domain identifier or, if there isn't a unique
        item, None.

        '''
        return List([f.coord(item=item, key=key, **kwargs) for f in self._list])
    #--- End: def

    def coords(self,  items=None, **kwargs):
        '''Return dimension or auxiliary coordinate objects from each field.

``fl.coords()`` is equivalent to ``cf.List(f.coords() for f in fl)``.

See `cf.Field.coords` for details.

:Parameters:

    items, kwargs : *optional*
        See `cf.Field.coords` for details.
  
:Returns:

    out : cf.List of dicts
        For each field, a dictionary whose keys are domain item
        identifiers with corresponding values of dimension or
        auxiliary coordinate objects.

        '''
        return List([f.coords( items=items, **kwargs) for f in self._list])
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``f.copy()`` is equivalent to ``copy.deepcopy(f)``.

:Returns:

    out : 
        The deep copy.

:Examples:

>>> g = f.copy()

'''
        new = type(self)()

        new_list = new._list
        for f in self._list:
            new_list.append(f.copy())
        
        return new
    #--- End: def

    def cos(self, i=False):
        '''

Take the trigonometric cosine of the data array for each field.

``fl.cos()`` is equivalent to ``cf.FieldList(f.cos() for f in fl)``.

See `cf.Field.cos` for details.

:Parameters:

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.cos(i=True)

        return fl
    #--- End: def

    def cyclic(self, axes=None, iscyclic=True, period=None, **kwargs):
        '''{+def_cyclic}

:Parameters:

    {+axes, kwargs}

    {+iscyclic}

    {+period}
        
:Returns:

    out : cf.List
        The axes of each the field which were cyclic prior to the new
        setting, or the current cyclic axes if no axis was specified.

        '''
        return List([f.cyclic(axes=axes, iscyclic=iscyclic, period=period,
                              **kwargs)
                     for f in self._list])
    #--- End: def
    format_docstring(cyclic)

    def data_axes(self):
        '''

Return the axes of a domain item from each field.

``fl.data_axes()`` is equivalent to ``cf.List(f.data_axes() for f in
fl)``.

See `cf.Field.data_axes` for details.
  
:Return:

    out : cf.List
        For each field, the ordered list of data axes, or, if there is
        no data array, None.

'''
        return List([f.data_axes() for f in self._list])
    #--- End: def

    def datum(self, *index):
        '''

Return an element of the data array for each field as a standard Python
scalar.

``fl.datum()`` is equivalent to ``cf.List(f.datum() for f in fl)``.

See `cf.Field.datum` for details.
  
:Parameters:

    index : *optional*
        Specify which element to return. See `cf.Field.datum` for
        details.

:Return:

    out : cf.List
        For each field, the requested element of the data array.

'''
        return List([f.datum(*index) for f in self._list])
    #--- End: def

    def dim(self, items=None, axes=None, axes_all=None,
            axes_subset=None, axes_superset=None, exact=False,
            inverse=False, match_and=True, ndim=None,
            key=False, copy=False):
        '''{+def_dim}

:Parameters: 

    {+items}

    {+ndim}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}

:Returns:

    out : cf.List   
        For each field, the unique dimension coordinate object or its
        domain identifier or, if there isn't a unique item, None.

        '''
        return List([f.dim(items=items, axes=axes, axes_all=axes_all,
                           axes_subset=axes_subset,
                           axes_superset=axes_superset, ndim=ndim,
                           exact=exact, inverse=inverse,
                           match_and=match_and, key=key, copy=copy)
                     for f in self._list])
    #--- End: def  
    format_docstring(dim, item='dimension coordinate',
                     identity='~cf.DimensionCoordinate.identity')

    def dims(self, items=None, **kwargs):
        '''Return dimension coordinate objects from each field.

``fl.dims()`` is equivalent to ``cf.List(f.dims() for f in fl)``.

See `cf.Field.dims` for details.

:Parameters:

    items, kwargs : *optional*
        See `cf.Field.dims` for details.
  
:Returns:

    out : cf.List of dicts
        For each field, a dictionary whose keys are domain item
        identifiers with corresponding values of dimension coordinate
        objects.

        '''
        return List([f.dims(items=items, **kwargs) for f in self._list])
    #--- End: def

    def delprop(self, prop):
        '''

Delete a CF property from each field.

``fl.delprop(prop)`` is equivalent to ``for f in fl:
f.delprop(prop)``.

:Parameters:

    prop : str
        The name of the CF property.

:Returns:

    None

.. seealso:: `cf.Field.delprop`, `getprop`, `hasprop`, `setprop`

'''
        for f in self._list:
            f.delprop(prop)
    #--- End: def
    
    def expand_dims(self, position=0, axis=None, i=False, **kwargs):
        '''

Insert a size 1 axis into the data array of each field .

``fl.expand_dims()`` is equivalent to ``cf.FieldList(f.expand_dims()
for f in fl)``.

See `cf.Field.expand_dims` for details.

:Parameters:

    position : int, optional
        Specify the position that the new axis will have in the data
        array axes. See `cf.Field.expand_dims`.

    axis, kwargs : *optional*
        Specify the axis to insert. See `cf.Field.expand_dims`.

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.expand_dims(position=position, axis=axis, i=True, **kwargs)

        return fl
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False):
        '''

Whether or not two field lists are pair-wise equal.

:Parameters:

    other : cf.FieldList
        The fields to compare for equality.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `cf.ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `cf.RTOL` function is used.

    ignore_fill_value : bool, optional
        If True then data arrays with different fill values are
        considered equal. By default they are considered unequal.

    traceback : bool, optional
        If True then print a traceback highlighting where any pair of
        fields differ.

:Returns: 

    out : cf.List

'''
        if self is other:
            return True
         
        # Check that each instance is the same type
        if self.__class__ != other.__class__:
            if traceback:
                print("%s: Different types: %s, %s" %
                      (self.__class__.__name__,
                       self.__class__.__name__,
                       other.__class__.__name__))
            return False
        #--- End: if

        # Check that the lists have the same number of fields
        if len(self) != len(other): 
            if traceback:
                print("%s: Different numbers of fields: %d, %d" %
                      (self.__class__.__name__, len(self), len(other)))
            return False
        #--- End: if

        if rtol is None:
            rtol = RTOL()
        if atol is None:
            atol = ATOL()

        # Check the fields pairwise
        for f, g in zip(self._list, other._list):
            if not f.equals(g, rtol=rtol, atol=atol,
                            ignore_fill_value=ignore_fill_value,
                            traceback=traceback):
                if traceback:
                    print("%s: Different fields: %r, %r" %
                          (self.__class__.__name__, f, g))
                return False
        #--- End: for

        # Still here? Then we have equality.
        return True
    #--- End: def
 
    def dump(self, complete=False, display=True, level=0, title='Field', q='='):
        '''

Return a full description of each the field.

See `cf.Field.dump` for details.

:Parameters:

:Returns:

    out : None or cf.List
        The description of each field.

'''
        if display:
            for f in self._list:
                f.dump(complete=complete, display=True, level=level,
                       title=title, q=q)
        else:
            return List([f.dump(complete=complete, display=False, level=level,
                                title=title, q=q)
                         for f in self._list])
    #--- End: def

    def fill_value(self):
        '''

Return the data array missing data value for each field.

``fl.fill_value()`` is equivalent to ``cf.List(f.fill_value() for f in
fl)``.

See `cf.Field.fill_value` for details.

:Returns:

    out :
        For each field, the missing data value, or None if one hasn't
        been set.

'''
        return List([f.fill_value() for f in self._list])
    #--- End: def
                   
    def flip(self, axes=None, i=False, **kwargs):
        '''

Flip axes of the data array for each field.

``fl.flip()`` is equivalent to ``cf.FieldList(f.flip() for f in fl)``.

See `cf.Field.flip` for details.

:Parameters:

    axes, kwargs : *optional*
        Select the axes to be flipped. See `cf.Field.flip` for
        details.

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.flip(axes=axes, i=True, **kwargs)

        return fl
    #--- End: def

    def getprop(self, prop, *default):
        '''

Get a CF property from each field.

When a default argument is given, it is returned when the attribute
doesn't exist; without it, an exception is raised in that case.

``fl.getprop(prop, *default)`` is equivalent to
``cf.List(f.getprop(prop, *default) for f in fl)``.

:Parameters:

    prop : str
        The name of the CF property.

    default : optional
        Return *default* if and only if the variable does not have the
        named property.

:Returns:

    out : cf.List
        The value of the named property, or the default value, for
        each field.

.. seealso:: `cf.Field.getprop`, `delprop`, `hasprop`, `setprop`

'''
        return List([f.getprop(prop, *default) for f in self._list])
    #--- End: def

    def hasprop(self, prop):
        '''

For each field, return True if a CF property exists, otherise False.

``fl.hasprop(prop)`` is equivalent to ``cf.List(f.hasprop(prop) for f
in fl)``.

:Parameters:

    prop : str
        The name of the property.

:Returns:

    out : cf.List
        True or False for each field.

.. seealso:: `cf.Field.hasprop`, `delprop`, `getprop`, `setprop`

'''
        return List([f.hasprop(prop) for f in self._list])
    #--- End: def

    def identity(self, default=None):
        '''

Return the identity of each field.

``fl.identity()`` is equivalent to ``cf.List(f.identity() for f in
fl)``.

See `cf.Field.identity` for details.

:Parameters:

    default : *optional*
        See `cf.Field.identity`.
  
:Returns:

    out :
        For each field, its identity.

'''
        return List([f.identity(default) for f in self._list])
    #--- End: def

    def indices(self, *exact, **kwargs):
        '''

For each field, return the data array indices which correspond to item
values.

``fl.indices(*exact, **kwargs)`` is equivalent to
``cf.List(f.indices(*exact, **kwargs) for f in fl)``.

See `cf.Field.indices` for details.

:Parameters:

    exact, kwargs : *optional*
        See `cf.Field.indices`.
  
:Returns:

    out : cf.List of tuples
        
'''
        return List([f.indices(*exact, **kwargs) for f in self._list])
    #--- End: def

    def insert_data(self, *args, **kwargs):
        '''Insert a new data array into the only field in place.

An exception is raised if there is not exactly one field in the list.

``fl.insert_data()`` is equivalent to ``if len(fl) == 1:
fl[0].insert_data()``.

See `cf.Field.insert_data` for details.

:Parameters:

    args, kwargs : *optional*
        See `cf.Field.insert_data`.
  
:Returns:

    None

        '''
        if len(self._list) == 1:
            self._list[0].insert_data(*args, **kwargs)
        else:
            raise TypeError(
                "Can only insert data for field lists with one element")
    #--- End: def

    def inspect(self):
        '''

Inspect the object for debugging.

.. seealso:: `cf.inspect`

:Returns: 

    None

'''
        print cf_inspect(self)
    #--- End: def

    def iscyclic(self, axes=None, **kwargs):
        '''{+def_iscyclic}

:Parameters:

    {+axes, kwargs}

:Returns:

    out : cf.List        

'''    
        return List([f.iscyclic(axes=axes, **kwargs) for f in self._list])
    #--- End: def
    format_docstring(iscyclic)

    def item(self, items=None, role=None, axes=None, axes_all=None,
             axes_subset=None, axes_superset=None, exact=False,
             inverse=False, match_and=True, ndim=None,
             key=False, copy=False):
        '''

Return a domain item, or its domain identifier, from each field.

``fl.item()`` is equivalent to ``cf.List(f.item() for f in fl)``.

See `cf.Field.item` for details.

:Parameters:

    {+items}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}

:Returns:

    out : cf.List
        For each field, the item or its domain identifier or, if there
        isn't a unique item, None.

        '''
        return List([f.item(item=items, role=role, axes=axes,
                            axes_all=axes_all,
                            axes_subset=axes_subset,
                            axes_superset=axes_superset, ctype=ctype,
                            exact=exact, inverse=inverse,
                            match_and=match_and, ndim=ndim,
                            key=key, copy=copy)
                     for f in self._list])
    #--- End: def

    def item_axes(self, item=None, **kwargs):
        '''Return the axes of a domain item from each field.

``fl.item_axes()`` is equivalent to ``cf.List(f.item_axes() for f in
fl)``.

See `cf.Field.item_axes` for details.

:Parameters:

    args, kwargs : *optional*
        See `cf.Field.item_axes`.
  
:Return:

    out : cf.List
        For each field, the ordered list of item axes, or, if there
        isn't a unique item or the item is a coordinate reference,
        None.

        '''
        return List([f.item_axes(*args, **kwargs) for f in self._list])
    #--- End: def

    def items(self, items=None, role=None, axes=None, axes_all=None,
              axes_subset=None, axes_superset=None, ndim=None, match_and=True,
              exact=False, inverse=False, copy=False):
        '''Return domain items from each field.

``fl.items()`` is equivalent to ``cf.List(f.items() for f in fl)``.

See `cf.Field.items` for details.

:Parameters:

    {+items}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out : dict
        For each field, a dictionary whose keys are domain item
        identifiers with corresponding values of items of the domain.

        '''
        return List([f.items(items, role=role, axes=axes,
                             axes_all=axes_all,
                             axes_subset=axes_subset,
                             axes_superset=axes_superset,
                             ndim=ndim, exact=exact,
                             inverse=inverse, match_and=match_and, copy=copy)
                     for f in self._list])
    #--- End: def

    def iter(self, name, *args, **kwargs):
        '''Return an iterator over the results of a method applied to the field
list.

``fl.iter(name)`` is equivalent to ``iter(getattr(fl, name)())``.

:Parameters:

    name : str
        The name of the method to apply to each element.

    args, kwargs : *optional*
        The arguments to be used in the call to the named method.

:Returns:

    out : generator
        An iterator over the results of the named method applied to
        each element.

.. seealso:: `method`

:Examples:

>>> fl.getprop('standard_name')
['air_temperature', 'eastward_wind']
>>> for x in fl.iter('getprop', 'standard_name'):
...     print x
...
'air_temperature'
'eastward_wind'

>>> fl.iter('squeeze')
[None, None]

        '''
        return iter(getattr(self, name)(*args, **kwargs))
    #--- End: def

    def floor(self, i=False):
        '''{+def_floor}

:Examples 2:

See `cf.Field.floor` for further examples.
''' 
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.floor(i=True)

        return fl
    #--- End: def
    format_docstring(floor)

    def mask_invalid(self, i=False):
        '''Mask the data array of each field where invalid values occur (NaNs or
infs).

Note that:

* Invalid values in the results of arithmetic operations may only
  occur if the raising of `FloatingPointError` exceptions has been
  suppressed by `cf.Data.seterr`.

* If the raising of `FloatingPointError` exceptions has been allowed
  then invalid values in the results of arithmetic operations may be
  automatically converted to masked values, depending on the setting
  of `cf.Data.mask_fpe`. In this case, such automatic conversion might
  be faster than calling `mask_invalid`.

:Parameters:

    {+i}

:Returns:

    out : cf.FieldList

.. seealso:: `cf.Data.mask_fpe`, `cf.Data.seterr`

:Examples:
'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.mask_invalid(i=True)

        return fl
    #--- End: def

    def match(self, match=None, items=None, rank=None,
              ndim=None, exact=False, match_and=True, 
              inverse=False):

        '''Test whether or not each field satisfies the given conditions.

``fl.match()`` is equivalent to ``cf.List(f.match() for f in fl)``.

See `cf.Field.match` for details.

:Parameters:

    match : *optional*
        Set conditions on the field property values. See
        `cf.Field.match` for details.

    coord : optional

    csize : dict, optional
        A dictionary which identifies coordinate objects of the fields
        with corresponding tests on their cell sizes. See
        `cf.Field.match` for details.

    rank : int or cf.Query, optional
        Specifiy a condition on the field domain ranks, where the
        domain rank is the number of domain axes. See `cf.Field.match`
        for details.

    ndim : int or cf.Query, optional

DCH

    exact : bool, optional
        The *exact* argument applies to the interpretion of particular
        conditions given by values of the *match* argument and by keys
        of the *cvalue* and *csize* arguments. See `cf.Field.match`
        for details.

    match_and : bool, optional
        By default *match_and* is True and the field matches if it
        satisfies all of the conditions specified by all of the test
        types (properties, coordinate object values, coordinate object
        cell sizes, domain rank and data array rank). See
        `cf.Field.match` for details.
       
    inverse : bool, optional
        If True then return a field matches if it does not satisfy the
        given conditions. See `cf.Field.match` for details.

:Returns:

    out : cf.List of bools
        For each field, True if it satisfies the given criteria, False
        otherwise.

        '''
        return List([f.match(match=match, items=items, rank=rank,
                             ndim=ndim, exact=exact,
                             match_and=match_and, 
                             inverse=inverse)
                     for f in self._list])
    #--- End: def

    def method(self, name, *args, **kwargs):
        '''Return the results of a method applied to each field.

``fl.method(name)`` is equivalent to ``fl.name()``.

:Parameters:

    name : str
        The name of the method to apply to each element.

    args, kwargs : *optional*
        The arguments to be used in the call to the named method.

:Returns:

    out : cf.FieldList or cf.List  
        The results of the named method applied to each element.

.. seealso:: `iter`

:Examples:

>>> fl.getprop('standard_name')
['air_temperature', 'eastward_wind']
>>> fl.method('getprop', 'standard_name')
['air_temperature', 'eastward_wind']

>>> fl.method('squeeze')
[None, None]

        '''
        return getattr(self, name)(*args, **kwargs)
    #--- End: def

    def name(self, default=None, identity=False):
        '''

Return a name for each field.

``fl.name()`` is equivalent to ``cf.List(f.name() for f in fl)``.

See `cf.Field.name` for details.

:Parameters:

    default : *optional*
        See `cf.Field.name`.

    identity : bool, optional
        See `cf.Field.name`.
  
:Returns:

    out : cf.List
       For each field, a name.

'''
        return List([f.name(default, identity=identity) for f in self._list])
    #--- End: def

    def override_units(self, new_units, i=False):
        '''Override the data array units in place.

``fl.override_units()`` is equivalent to
``cf.FieldList(f.override_units() for f in fl)``.

See `cf.Field.override_units` for details.

:Parameters:

    new_units : str or Units
        The new units for the data array. See
        `cf.Field.override_units` for details.

    {+i}
  
:Returns:

    out : cf.FieldList

        '''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.override_units(new_units, i=True)

        return fl
    #--- End: def

    def regrids(self, dst, src_cyclic=False, dst_cyclic=False,
                src_2D_latlong=False, dst_2D_latlong=False, conservative=True,
                ignore_dst_mask=False, i=False):
        '''

Regrid fields from one latitude-longitude grid to another.

'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.regrids(dst, src_cyclic=src_cyclic, dst_cyclic=dst_cyclic,
                      src_2D_latlong=src_2D_latlong,
                      dst_2D_latlong=dst_2D_latlong, conservative=conservative,
                      ignore_dst_mask=ignore_dst_mask, i=True)

        return fl
    #--- End: def

    def remove_axes(self,*args, **kwargs):
        '''Remove and return axes from each field.

``fl.remove_axes()`` is equivalent to ``cf.List(f.remove_axes() for f
in fl)``.

See `cf.Field.remove_axes` for details.

:Parameters:

    args, kwargs : *optional*
        See `cf.Field.remove_axes`.
  
:Returns:

    out : cf.List

        '''
        return List([f.remove_axes(*args, **kwargs) for f in self._list])
    #--- End: def
    
    def remove_axis(self, *args, **kwargs):
        '''Remove and return an axis from each field.

``fl.remove_axis()`` is equivalent to ``cf.List(f.remove_axis() for f
in fl)``.

See `cf.Field.remove_axis` for details.

:Parameters:

    args, kwargs : *optional*
        See `cf.Field.remove_axis`.
  
:Returns:

    out : cf.List

        '''
        return List([f.remove_axis(*args, **kwargs) for f in self._list])
    #--- End: def
    
    def remove_data(self):
        '''

Remove and return the data array from each field.

``fl.remove_data()`` is equivalent to ``cf.List(f.remove_data() for f
in fl)``.

See `cf.Field.remove_data` for details.

:Returns:

    out : cf.List
        For each field, its data array, or None if it doesn't have
        one.

'''
        return List([f.remove_data() for f in self._list])
    #--- End: def

    def remove_item(self, *args, **kwargs):
        '''Remove and return a domain item from each field.

An item is either a dimension coordinate, an auxiliary coordinate, a
cell measure or a coordinate reference object of the domain.

``fl.remove_item()`` is equivalent to ``cf.List(f.remove_item() for f
in fl)``.

See `cf.Field.remove_item` for details.

:Parameters:

    args, kwargs : *optional*
        See `cf.Field.remove_item`.
  
:Returns:

    out : cf.List
        For each field, the removed item, or None if no unique item
        could be found.

        '''
        return List([f.remove_item(*args, **kwargs) for f in self._list])
    #--- End: def

    def remove_items(self, *args, **kwargs):
        '''Remove and return domain items from each field.

An item is either a dimension coordinate, an auxiliary coordinate, a
cell measure or a coordinate reference object of the domain.

``fl.remove_items()`` is equivalent to ``cf.List(f.remove_items() for
f in fl)``.

See `cf.Field.remove_items` for details.

:Parameters:

    args, kwargs : *optional*
        See `cf.Field.remove_items`.
  
:Returns:

    out : cf.List of lists
        For each field, a list of the removed items.

        '''
        return List([f.remove_items(*args, **kwargs) for f in self._list])
    #--- End: def

    def rint(self, i=False):
        '''{+def_rint}

:Examples 2:

See `cf.Field.rint` for further examples.
''' 
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.rint(i=True)

        return fl
    #--- End: def
    format_docstring(rint)

    def roll(self, axis, shift, i=False, **kwargs):
        '''Roll each field along a cylcic axis.

:Parameters:

    axis, kwargs : *optional* 
        
        Select the axis to be rolled. See `cf.Field.roll` for details.

    shift : int
        The number of places by which the selected cyclic axis is to
        be rolled. See `cf.Field.roll` for details.

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

        '''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.roll(axis, shift, i=True, **kwargs)

        return fl
    #--- End: def

    def set_equals(self, other, rtol=None, atol=None,
                   ignore_fill_value=False, traceback=False):
        '''

True if two instances are set-wise equal, False otherwise.

Two instances are set-wise equal if their attributes are equal and
their elements are equal set-wise (i.e. the order of the lists is
irrelevant).

:Parameters:

    other : 
        The object to compare for equality.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

    ignore_fill_value : bool, optional
        If True then data arrays with different fill values are
        considered equal. By default they are considered unequal.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        instances differ.

:Returns: 

    out : bool
        Whether or not the two instances are equal.

:Examples:


'''
        # Check for object identity
        if self is other:
            return True

        # Check that each instance is the same type
        if self.__class__ != other.__class__:
            if traceback:
                print("%s: Different type: %s, %s" %
                      (self.__class__.__name__,
                       self.__class__.__name__,
                       other.__class__.__name__))
            return False
        #--- End: if

        # Check for the same number of fields
        if len(self) != len(other):
            if traceback:
                print("%s: Different numbers of fields" %
                      self.__class__.__name__)
            return False
        #--- End: if
        
        # Group the fields by identity
        self_identity  = {}
        other_identity = {}        
        for fl, d in zip((self, other),
                         (self_identity, other_identity)):
            for f in fl:
                identity = f.identity()
                if identity in d:
                    d.append(f)
                else:
                    d[identity] = [f]
        #--- End: def

        # Check that there are the same identities
        if set(self_identity) != set(other_identity):
            if traceback:
                print("%s: Different identities: %s, %s" %
                      (self.__class__.__name__,
                       set(self_identity), set(other_identity)))
            return False
        #--- End: if

        # Check that there are the same number of fields for each
        # identity
        for identity, lf in self_identity.iteritems():
            lg = other_identity[identity]
            if len(lf) != len(lg):
                if traceback:
                    print("%s: Different numbers of %r fields: %d, %d" %
                          (self.__class__.__name__, identity,
                           len(lf), len(lg)))
                return False
        #--- End: for
            
        # For each identity, check that there are matching pairs of
        # equal fields.
        for identity, lf in self_identity.iteritems():
            lg = other_identity[identity]

            found_match = False
            for f in lf:
                for i, g in enumerate(lg):
                    if f.equals(g, rtol=rtol, atol=atol,
                                ignore_fill_value=ignore_fill_value,
                                traceback=False):
                        found_match = True
                        break
                #--- End: for
                if found_match:
                    lg.remove(i)
                    continue
                elif traceback:                        
                    print("%s: No equal field: %r" %
                          (self.__class__.__name__, f))
                    return False
            #--- End: for
        #--- End: for

        # Still here? Then we have set equality.
        return True
    #--- End: def

    def where(self, condition, x, y=None):
        '''Set data array elements depending on a condition.

``fl.where(condition, x, y)`` is equivalent to ``for f in fl:
f.where(condition, x, y)``.

See `cf.Field.where` for details.

:Parameters:

    condition :
        Set the condition. See `cf.Field.where` for details.
        
    x, y :
        Specify the assignment values. See `cf.Field.where` for
        details.
         
:Returns:

    None

        '''
        for f in self._list:
            f.where(condition, x, y)
    #--- End: def

    def setprop(self, prop, value):
        '''

Set a CF property on each field.

``fl.setprop(prop, value)`` is equivalent to ``for f in fl:
f.setprop(prop, value)``.

:Parameters:

    prop : str
        The name of the CF property.

    value :
        The value for the property.
  
:Returns:

    out : None

.. seealso:: `cf.Field.setprop`, `delprop`, `getprop`, `hasprop`

'''
        for f in self._list:
            f.setprop(prop, value)
    #--- End: def

    def select(self, match=None, items=None, rank=None, ndim=None,
               exact=False, match_and=True, inverse=False):
        '''Return the fields which satisfy the given conditions.

The conditions are defined in the same manner as for `cf.Field.match`,
which tests whether or not a field satisfies the given criteria.

Note that ``fl.select()`` is equivalent to ``cf.FieldList(f for f in
fl if f.match())``.

.. seealso:: `cf.Field.match`, `match`

:Parameters:

    match : *optional*
        Set conditions on the field's CF property and attribute
        values. See the *match* parameter of `cf.Field.match` for
        details.

    items : dict, optional
        A dictionary which identifies domain items of the field
        (dimension coordinate, auxiliary coordinate, cell measure or
        coordinate reference objects) with corresponding tests on
        their elements. See the *items* parameter of `cf.Field.match`
        for details.
      
    rank : int or cf.Query, optional
        Specify a condition on the number of axes in the field's
        domain. See `cf.Field.match` for details.

    ndim : int or cf.Query, optional
        Specify a condition on the number of axes in the field's data
        array. See `cf.Field.match` for details.

    exact : bool, optional
        The exact parameter applies to the interpretation of string
        values of the *match* parameter and of keys of the *items*
        parameter. See the *exact* parameter of `cf.Field.match` for
        details.
     
    match_and : bool, optional
        By default *match_and* is True and the field matches if it
        satisfies the conditions specified by each test parameter
        (*match*, *items*, *rank* and *ndim*). If *match_and* is False
        then the field will match if it satisfies at least one test
        parameter's condition. See the *match_and* parameter of
        `cf.Field.match` for details.

    inverse : bool, optional
        If True then return the field matches if it does **not**
        satisfy the given conditions. See the *inverse* parameter of
        `cf.Field.match` for details.

:Returns:

    out : cf.FieldList
        Each field that matches the given conditions, or if *inverse*
        is True, doesn't match the conditions.

:Examples:

        '''
        return type(self)([f for f in self._list if
                           f.match(match=match, items=items,
                                   rank=rank, ndim=ndim, exact=exact,
                                   match_and=match_and, inverse=inverse)
                           ])
    #--- End: def

    def sin(self, i=False):
        '''

Take the trigonometric sine of the data array of each field.

``fl.sin()`` is equivalent to ``cf.FieldList(f.sin() for f in fl)``.

See `cf.Field.sin` for details.

:Parameters:

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.sin(i=True)

        return fl
    #--- End: def

    def sort(self, cmp=None, key=None, reverse=False):
        '''

Sort the fields in place.

This method has exactly the same functionality as the built-in
`!list.sort` method.

The sort is stable in that if multiple fields have the same *key*
value then their original order is preserved.

:Parameters:

    cmp : *optional*
       See the built-in `!list`.

    key : *optional*
       See the built-in `!list`.

    reverse : bool, optional
       See the built-in `!list`.

:Returns:

    None

:Examples:

Two ways of sorting by standard name:

>>> fl.sort(key=lambda f: f.standard_name)

>>> from operator import attrgetter
>>> fl.sort(key=attrgetter('standard_name'))

Place the fields in reverse standard name order:

>>> from operator import attrgetter
>>> fl.sort(key=attrgetter('standard_name'), reverse=True)

Sort by standard name then by long name:

>>> from operator import attrgetter
>>> fl.sort(key=attrgetter('standard_name', 'long_name'))

Sort by standard name then by the value of the second element of the
data array:

>>> fl.sort(key=lambda f: (f.standard_name, f.datum(1)))

Sort by reverse order of the first time coordinate value:

>>> fl.sort(key=lambda f: f.coord('T').Data[0], reverse=True)

'''
        self._list.sort(cmp=cmp, key=key, reverse=reverse)
    #--- End: def

    def squeeze(self, axes=None, i=False, **kwargs):
        '''

Insert size 1 axes into the data array of each field.

:Parameters:

    axes, kwargs : *optional*
        Select the axes to be squeezed. See `cf.Field.squeeze`.

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.squeeze(axes=axes, i=True, **kwargs)

        return fl
    #--- End: def

    def setitem(self, *args, **kwargs):
        raise NotImplementedError(
"cf.%s.setitem is dead. Use cf.%s.subspace or cf.%s.where instead." % 
(self.__class__.__name__, self.__class__.__name__, self.__class__.__name__))

    def setmask(self, *args, **kwargs):
        raise NotImplementedError(
"cf.%s.setmask is dead. Use cf.%s.subspace or cf.%s.where instead." %
(self.__class__.__name__, self.__class__.__name__, self.__class__.__name__))

    def subset(self, *args, **kwargs):
        raise NotImplementedError(
"cf.%s.subset is dead. Use cf.%s.select instead." %
(self.__class__.__name__, self.__class__.__name__))

    def tan(self, i=False):
        '''

Take the trigonometric tangent of the data array of each field.

``fl.tan()`` is equivalent to ``cf.FieldList(f.tan() for f in fl)``.

See `cf.Field.tan` for details.

:Parameters:

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.tan(i=True)

        return fl
    #--- End: def

    def ref(items=None, axes=None, axes_all=None,
            axes_subset=None, axes_superset=None, exact=False,
            inverse=False, match_and=True, ndim=None,
            key=False, copy=False):
        '''{+def_ref}

:Parameters: 

    {+items}

    {+ndim}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}

:Returns:

    out : cf.List   
        For each field, the unique coordinate reference object or its
        domain identifier or, if there isn't a unique item, None.

        '''
        return List([f.ref(items=items, axes=axes, axes_all=axes_all,
                           axes_subset=axes_subset,
                           axes_superset=axes_superset, ndim=ndim,
                           exact=exact, inverse=inverse,
                           match_and=match_and, key=key, copy=copy)
                     for f in self._list])
    #--- End: def
    format_docstring(ref, item='coordinate reference',
                     identity='~cf.CoordinateReference.identity')

    def refs(self, items=None, **kwargs):
        '''Return coordinate reference objects from each field.

``fl.refs()`` is equivalent to ``cf.List(f.refs() for f in fl)``.

See `cf.Field.refs` for details.

:Parameters:

    items, kwargs : *optional*
        See `cf.Field.refs` for details.
  
:Returns:

    out : cf.List of dicts
        For each field, a dictionary whose keys are domain item
        identifiers with corresponding values of coordinate reference
        objects.

        '''
        return List([f.refs(items=items, **kwargs) for f in self._list])
    #--- End: def

    def transpose(self, axes=None, i=False, **kwargs):
        '''

Permute the dimensions of the data array of each field in place.

``fl.transpose()`` is equivalent to ``cf.FieldList(f.transpose() for f
in fl)``.

See `cf.Field.transpose` for details.

:Parameters:

    axes, kwargs : *optional*
        Set the new axis order. See `cf.Field.transpose` for details.

    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.transpose(axes=axes, i=True, **kwargs)

        return fl
    #--- End: def

    def trunc(self, i=False):
        '''{+def_trunc}

:Examples 2:

See `cf.Field.trunc` for further examples.
''' 
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.trunc(i=True)

        return fl
    #--- End: def
    format_docstring(trunc)

    def unsqueeze(self, axes=None, i=False, **kwargs):
        '''

Insert size 1 axes into the data array of each field.

``fl.unsqueeze()`` is equivalent to ``cf.FieldList(f.unsqueeze() for f
in fl)``.

See `cf.Field.unsqueeze` for details.

:Parameters:

    args, kwargs : *optional*
        See `cf.Field.unsqueeze`.
  
    i : bool, optional        
        If True then update the field list and its fields in place. By
        default a new field list containing new fields is created.

:Returns:

    out : cf.FieldList

'''
        if i:
            fl = self
        else:
            fl = self.copy()

        for f in fl._list:
            f.unsqueeze(axes=axes, i=True, **kwargs)

        return fl
    #--- End: def

#--- End: class

## ====================================================================
##
## List of Fields slice object
##
## ====================================================================
#
#class SubspaceFieldList(SubspaceVariableList):
#    '''
#
#'''
#    __slots__ = []
#
#    def __call__(self, *arg, **kwargs):
#        '''
#
#Slice by fields by coordinate value.
#
#'''
#        fieldlist = self.variablelist
#        return type(fieldlist)([f.subspace(*arg, **kwargs) for f in fieldlist])
#    #--- End: def
#
##--- End: class

# ====================================================================
#
# List of Fields slice object
#
# ====================================================================

class SubspaceFieldList(object):
    '''

'''
    __slots__ = ('fieldlist',)

    def __init__(self, fieldlist):
        '''

Set the contained list of fields.

'''
        self.fieldlist = fieldlist
    #--- End: def

    def __call__(self, *args, **kwargs):
        '''

x.__call__(*args, **kwargs) <==> x(*args, **kwargs)

'''
        fieldlist = self.fieldlist
        return type(fieldlist)([f.subspace(*args, **kwargs)
                                for f in fieldlist._list])
    #--- End: def

    def __getitem__(self, index):
        '''
x.__getitem__(index) <==> x[index]

'''
        fieldlist = self.fieldlist
        return type(fieldlist)([f.subspace[index] for f in fieldlist._list])
    #--- End: def

    def __setitem__(self, index, value):
        '''
x.__setitem__(index, value) <==> x[index]=value

'''
        for f in self.fieldlist._list:
            f.subspace[index] = value
    #--- End: def

#--- End: class
