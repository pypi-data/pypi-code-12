import collections

from copy import deepcopy
from re import sub    as re_sub
from re import search as re_search

from .utils     import List, Dict
from .functions import equals
from .functions import inspect as cf_inspect

from .data.data import Data

# ====================================================================
#
# CellMethod object
#
# ====================================================================

class _CellMethod(object):
    '''
'''
    def __init__(self):
        self.axes = []
        self.names = []
        self.intervals = List()
        self.comment = None
        self.where = None
        self.within = None
        self.over = None

    def inspect(self):
        '''

Inspect the attributes.

.. seealso:: `cf.inspect`

:Returns: 

    None

'''
        print cf_inspect(self)
    #--- End: def
# ====================================================================
#
# CellMethods object
#
# ====================================================================

class CellMethods(collections.MutableSequence):
    '''

A CF cell methods object to describe the characteristic of a field
that is represented by cell values.

Each cell method is stored in a dictionary and these dictionaries are
stored in a list-like object. Similarly to a CF cell_methods string,
the order of cell methods in the list is important.

The dictionary representing each cell method recognizes the following
keys (where all keys are optional; the referenced sections are from
the NetCDF Climate and Forecast (CF) Metadata Conventions and words in
double quotes ("...") refer to CF cell_methods components in the
referenced sections):


**Statistics for a combination of axes**

The names of the dimensions involved in a combination of axes are
given as a list (although their order is immaterial), with
corresponding dimension identifiers:

>>> c
<CF CellMethods: latitude: longitude: mean>
>>> list(c)
[{'method'   : 'mean',
  'name'     : ['latitude', 'longitude'],     
  'dim'      : ['dim2, 'dim3']}]

If the string 'area' is used to indicate variation over horizontal
area, then the corresponding dimension is None:

>>> c
<CF CellMethods: area: mean>
>>> list(c)
[{'method'   : 'mean',
  'name'     : ['area'],     
  'dim'      : [None]}]


**Cell methods when there are no coordinates**

These have name strings which are standard names or the string 'area',
with corresponding dimension identifiers of None:

>>> c
<CF CellMethods: time: max>
>>> list(c)
[{'method'   : 'max',
  'name'     : ['time'],     
  'dim'      : [None]}]


>>> c
<CF CellMethods: lat: longitude: mean>
>>> list(c)
[{'method'   : 'mean',
  'name'     : ['lat', 'longitude','],     
  'dim'      : ['dim1', None]}]

>>> c
<CF CellMethods: area: mean>
>>> list(c)
[{'method'   : 'minimum',
  'name'     : ['area'],     
  'dim'      : [None]}]

In the case of 'area', there is no distinction between this cell
method and one for which there appropriate dimensions exist, but the
two cases may be discerned by inspection of the field's domain.

'''

    def __init__(self, cell_methods=None):
        '''

**Initialization**

:Parameters:

    string : str, optional
        Initialize new instance from a CF-netCDF-like cell methods
        string. See the `parse` method for details. By default an
        empty cell methods is created.

**Examples**

>>> c = CellMethods()
>>> c = CellMethods('time: max: height: mean')

'''               
        if not cell_methods:
            self._list = []
        elif isinstance(cell_methods, basestring):
            self._list = []
            self.parse(cell_methods)
        else:
            self._list = list(cell_methods)
    #--- End: def

    def __delitem__(self, index):
        '''

x.__delitem__(index) <==> del x[index]

'''
        del self._list[index]
    #--- End: def

    def __deepcopy__(self, memo):
        '''
Used if copy.deepcopy is called on the variable.

'''
        return self.copy()
    #--- End: def

    def __getitem__(self, index):
        '''

x.__getitem__(index) <==> x[index]

'''     
        if isinstance(index, (int, long)):
            return type(self)(self._list[index:index+1])
        else:
            return type(self)(self._list[index])
    #--- End: def

    def __hash__(self):
        '''

x.__hash__() <==> hash(x)

'''
        return hash(self.string)
    #--- End: if

    def __len__(self):
        '''

x.__len__() <==> len(x)

'''
        return len(self._list)
    #--- End: def

    def __repr__(self):
        '''
x.__repr__() <==> repr(x)

'''
        return '<CF %s: %s>' % (self.__class__.__name__, 
                                ' '.join(self.strings()))
    #--- End: def

    def __setitem__(self, index, value):        
        '''

x.__setitem__(index, value) <==> x[index]=value

'''
        if not isinstance(value, self.__class__):
            raise ValueError("ahsdbasidh as8-80 i")
        
        if isinstance(index, (int, long)):
            index = slice(index, index+1)
            
        self._list[index] = value._list
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''        
        return ' '.join(self.strings())
    #--- End: def

    def __eq__(self, other):
        '''

x.__eq__(y) <==> x==y <==> x.equals(y)

'''
        return self.equals(other)
    #--- End: def

    def __ne__(self, other):
        '''

x.__ne__(y) <==> x!=y <==> not x.equals(y)

'''
        return not self.__eq__(other)
    #--- End: def

    def __add__(self, other):
        '''

x.__add__(y) <==> x+y

'''
        new = self.copy()
        new.extend(other)
        return new
    #--- End: def

    def __mul__(self, other):
        '''

x.__mul__(n) <==> x*n

'''
        return type(self)(self._list * other)
    #--- End: def

    def __rmul__(self, other):
        '''

x.__rmul__(n) <==> n*x

'''
        return self * other
    #--- End: def

    def __iadd__(self, other):
        '''

x.__iadd__(y) <==> x+=y

'''
        self.extend(other)
        return self
    #--- End: def

    def __imul__(self, other):
        '''

x.__imul__(n) <==> x*=n

'''
        self._list = self._list * other
        return self
    #--- End: def

    @property
    def axes(self):
        return [cm.axes for cm in self._list]
 
    @axes.setter
    def axes(self, value):
        if len(self._list) != 1:
            raise ValueError("2lskdj ")
        if not isinstance(value, list):
            raise ValueError("2lasdasdsskdj ")
        
        self._list[0].axes = value
 
    @property
    def comment(self):
        return [cm.comment for cm in self._list]

    @property
    def method(self):
        return [cm.method for cm in self._list]

    @method.setter
    def method(self, value):
        if len(self._list) != 1:
            raise ValueError("2lskdj ")
        
        self._list[0].method = value
 
    @property
    def names(self):
        return [cm.names for cm in self._list]

    @names.setter
    def names(self, value):
        if len(self._list) != 1:
            raise ValueError("2lskdj ")
        if not isinstance(value, list):
            raise ValueError("2lasdasdsskdj ")
        
        self._list[0].names = value
 
    @property
    def intervals(self):
        return [cm.intervals for cm in self._list]

    @intervals.setter
    def intervals(self, value):
        if len(self._list) != 1:
            raise ValueError("2lskdj ")
        if not isinstance(value, list):
            raise ValueError("2lasdasdsskdj ")
        
            # parse here
        self._list[0].intervals = List(value)
 
    @property
    def over(self):
        return [cm.over for cm in self._list]
 
    @over.setter
    def over(self, value):
        if len(self._list) != 1:
            raise ValueError("2lskdj ")
        
        self._list[0].over = value
 
    @property
    def string(self):
        '''

'''
        return ' '.join(self.strings())
    #--- End: def

    @property
    def where(self):
        return [cm.where for cm in self._list]
 
    @where.setter
    def where(self, value):
        if len(self._list) != 1:
            raise ValueError("2lskdj ")
        
        self._list[0].where = value
 
    @property
    def within(self):
        return [cm.within for cm in self._list]

    @within.setter
    def within(self, value):
        if len(self._list) != 1:
            raise ValueError("2lskdj ")
        
        self._list[0].within = value
 
    def copy(self):
        '''

Return a deep copy.

``c.copy()`` is equivalent to ``copy.deepcopy(c)``.

:Returns:

    out : 
        The deep copy.

**Examples**

>>> d = c.copy()

'''
        return type(self)(deepcopy(self._list))
    #--- End: def

    def dump(self, display=True, prefix=None):
         '''

Return a string containing a full description of the instance.

If a cell methods 'name' is followed by a '*' then that cell method is
relevant to the data in a way which may not be precisely defined its
corresponding dimension or dimensions.

:Parameters:

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``c.dump()`` is equivalent to
        ``print c.dump(display=False)``.

    prefix : str, optional
       Set the common prefix of component names. By default the
       instance's class name is used.

:Returns:

    out : None or str
        A string containing the description.

**Examples**

'''
         if prefix is None:
             prefix = self.__class__.__name__
                              
         string = []
         
         for i, s in enumerate(self.strings()):
             string.append('%s[%d] -> %s' % (prefix, i, s))
             
         string = '\n'.join(string)
         
         if display:
             print string
         else:
             return string
    #--- End: def

    def equals(self, other, rtol=None, atol=None, traceback=False):
        '''

True if two cell methods are equal, False otherwise.

The *dim* attribute is ignored in the comparison.

:Parameters:

    other : 
        The object to compare for equality.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        instances differ.

:Returns: 

    out : bool
        Whether or not the two instances are equal.

**Examples**

'''
        if self is other:
            return True

        # Check that each instance is the same type
        if self.__class__ != other.__class__:
            if traceback:
                print("%s: Different types: %s != %s" %
                      (self.__class__.__name__,
                       self.__class__.__name__,
                       other.__class__.__name__))
            return False
        #--- End: if

        if len(self) != len(other):
            if traceback:
                print("%s: Different numbers of methods: %d != %d" %
                      (self.__class__.__name__,
                       len(self), len(other)))
            return False
        #--- End: if

        for cm0, cm1 in zip(self._list, other._list):
            if None in cm0.names or None in cm1.names:
                if traceback:
                    print("%s: Missing names: %s, %s" %
                          (self.__class__.__name__, cm0.names, cm1.names))
                return False
            #--- End: if

            if set(cm0.names) != set(cm1.names):
                if traceback:
                    print("%s: Different names: %r, %r" %
                          (self.__class__.__name__, cm0.names, cm1.names))
                return False

            for attr in ('method', 'within', 'over', 'where', 'comment'):
                if getattr(cm0, attr) != getattr(cm1, attr):
                    if traceback:
                        print("%s: Different %s: %r, %r" %
                              (self.__class__.__name__, key, x, y))
                    return False

            if cm0.intervals is not None:                
                interval0 = cm0.intervals
                interval1 = cm1.intervals

                # Make sure that both lists of intervals are the same
                # length (if they're not, then the shorter one will
                # have length 1).
                if len(interval0) < len(name0):
                    interval0 = interval0 * len(name0)
                elif len(interval1) < len(name1):
                    interval1 = interval1 * len(name1)

                if not equals(interval0, interval1,
                              rtol=rtol, atol=atol, traceback=traceback):
                    if traceback:
                        print("%s: Different intervals: %r, %r" %
                              (self.__class__.__name__, interval0, interval1))
                        return False
            #--- End: if
        #--- End: for

        return True
    #--- End: def

    def equivalent(self, other, rtol=None, atol=None, traceback=False):
        '''

True if two cell methods are equivalent, False otherwise.

The *dim* attribute is ignored in the comparison.

:Parameters:

    other : 
        The object to compare for equality.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

:Returns: 

    out : bool
        Whether or not the two instances are equivalent.

**Examples**

'''
        if self is other:
            return True

        # Check that each instance is the same type
        if self.__class__ != other.__class__:
            return False

        if len(self) != len(other):
            return False

        for cm0, cm1 in zip(self, other):

            keys0 = set(cm0)
            keys1 = set(cm1)

            if keys0 != keys1: 
                if traceback:
                    print("%s: Nonequivalent keys: %r, %r" %
                          (self.__class__.__name__, x, y))
                return False

            name0 = cm0.names
            name1 = cm1.names
            if len(name0) != len(name1) or (None in name0 or None in name1):
                return False
            
            if 'interval' in keys0:
                keys0.remove('interval')

                interval0 = cm0['interval'][:]
                interval1 = cm1['interval'][:]

                # Make sure that both lists of intervals are the same
                # length. (If they're not, then the shorter one will
                # have length 1.)
                if len(interval0) < len(name0):
                    interval0 = interval0 * len(name0)
                elif len(interval1) < len(name1):
                    interval1 = interval1 * len(name1)

                for x, y in zip(interval0, interval1):
                    if not x.allclose(y, rtol=rtol, atol=atol):
                        if traceback:
                            print("%s: Nonequivalent 'interval' values: %r, %r" %
                                  (self.__class__.__name__, x, y))
                        return False
            #--- End: if

            keys0.discard('dim')

            key = 'method'
            if key in keys0:
                x = cm0[key]
                y = cm1[key]                
                if not equals(x, y, rtol=rtol, atol=atol, traceback=False):
                    if traceback:
                        print("%s: Nonequivalent '%s' values: %r, %r" %
                              (self.__class__.__name__, key, x, y))
                    return False
                
                keys0.discard(key)
            #--- End: if
                   

            for key in keys0:
                for x, y in zip(cm0[key], cm1[key]):
                    if not equals(x, y, rtol=rtol, atol=atol,
                                  traceback=False):
                        if traceback:
                            print("%s: Nonequivalent '%s' values: %r, %r" %
                                  (self.__class__.__name__, key, x, y))
                        return False
        #--- End: for

        return True
    #--- End: def

    def has_cellmethod(self, other):
        '''

Return True if and only if this cell methods is a super set of another.

:Parameters:
    other : CellMethods
        The other cell methods for comparison.

:Returns:
    out : bool
        Whether or not this cell methods is a super set of the other.

**Examples**

'''
        if len(other) != 1:
            return False

        found_match = False

        for i in range(len(self)):
            if other.equivalent(self[i:i+1]):
                found_match = True
                break
        #--- End: for

        return found_match
    #--- End: def

    def insert(self, index, value):
        # Insert an object before index.
        self._list.insert(index, value)
    #--- End: def

    def inspect(self):
        '''

Inspect the attributes.

.. seealso:: `cf.inspect`

:Returns: 

    None

'''
        print cf_inspect(self)
    #--- End: def

    def parse(self, string=None):
        '''

Parse a CF cell_methods string into this CellMethods instance in
place.

:Parameters:

    string : str, optional
        The CF cell_methods string to be parsed into the CellMethods
        object. By default the cell methods will be empty.

:Returns:

    None

**Examples**

>>> c = cf.CellMethods()
>>> c = c.parse('time: minimum within years time: mean over years (ENSO years)')    
>>> print c
Cell methods    : time: minimum within years
                  time: mean over years (ENSO years)

'''
        if not string:
            self._list[:] = []
            return

        # Split the cell_methods string into a list of strings ready
        # for parsing into the result list. E.g.
        #   'lat: mean (interval: 1 hour)'
        # maps to 
        #   ['lat:', 'mean', '(', 'interval:', '1', 'hour', ')']
        cell_methods = re_sub('\((?=[^\s])' , '( ', string)
        cell_methods = re_sub('(?<=[^\s])\)', ' )', cell_methods).split()

        while cell_methods:
            print cell_methods
            cm = _CellMethod()

            # List of axes
            cm.axes = []

            # List of names
            cm.names = []

            while cell_methods:
                if not cell_methods[0].endswith(':'):
                    break

                cm.names.append(cell_methods.pop(0)[:-1])            
                cm.axes.append(None)
            #--- End: while

            if not cell_methods:
                self.append(cm)
                break
            print  'a'
            # Method
            cm.method = cell_methods.pop(0)
            print  'a2'
            if not cell_methods:
                self.append(cm)
                break

            # Climatological statistics and statistics which apply to
            # portions of cells
            print cell_methods
            while cell_methods[0] in ('within', 'where', 'over'):
                term = cell_methods.pop(0)
                print term, cell_methods
                setattr(cm, term, cell_methods.pop(0))
                if not cell_methods:
                    break
            #--- End: while
            print  'a3'
            if not cell_methods: 
                self.append(cm)
                break
            print  'a4'
            # interval and comment
            if cell_methods[0].endswith('('):
                cell_methods.pop(0)

                if not (re_search('^(interval|comment):$', cell_methods[0])):
                    cell_methods.insert(0, 'comment:')
                           
                while not re_search('^\)$', cell_methods[0]):
                    term = cell_methods.pop(0)[:-1]

                    if term == 'interval':
                        if cm.intervals is None:
                            cm.intervals = List()
                        interval = cell_methods.pop(0)
                        try:
                            interval = float(interval)
                        except ValueError:
                            pass

                        if cell_methods[0] != ')':
                            units = cell_methods.pop(0)
                        else:
                            units = None

                        try:
                            cm.intervals.append(Data(interval, units))
                        except ValueError:
                            cm.intervals = None
                            print(
"WARNING: Ignoring unknown interval in %s initialization: %s %s" % \
(self.__class__.__name__, interval, units))
                            
                        continue
                    #--- End: if

                    if term == 'comment':
                        comment = []
                        while cell_methods:
                            if cell_methods[0].endswith(')'):
                                break
                            if cell_methods[0].endswith(':'):
                                break
                            comment.append(cell_methods.pop(0))
                        #--- End: while
                        cm.comment = ' '.join(comment)
                    #--- End: if

                #--- End: while 

                if cell_methods[0].endswith(')'):
                    cell_methods.pop(0)
            #--- End: if
            print 'appending'
            self.append(cm)
            print self._list
        #--- End: while

    #--- End: def

    def strings(self):
        '''

Return a list of a CF-netCDF-like string of each cell method.

Note that if the intention is to concatenate the output list into a
string for creating a CF-netCDF cell_methods attribute, then the cell
methods "name" components may need to be modified, where appropriate,
to reflect netCDF variable names.

:Returns:

    out : list
        A string for each cell method.

**Examples**

>>> c = cf.CellMethods('time: minimum within years time: mean over years (ENSO years)')
>>> c.strings()
['time: minimum within years',
 'time: mean over years (ENSO years)']

'''
        strings = []

        for cm in self._list:
            string = []

            x = []
            for dim, name in zip(cm.axes, cm.names):
                if name is None:
                    if dim is not None:
                        name = dim
                    else:
                        name = '?'

                x.append('%s:' % name)
            #--- End: for
            string.extend(x)

            string.append(cm.method)

            for portion in ('within', 'where', 'over'):
                p = getattr(cm, portion, None)
                if p is not None:
                    string.extend((portion, p))
            #--- End: for

            if cm.intervals:
                x = ['(']

                y = []
                for interval in cm.intervals:
                    y.append('interval: %s' % interval.datum(0))
                    if interval.Units:
                        y.append(interval.Units.units)
                #--- End: for
                x.append(' '.join(y))

                if cm.comment is not None:
                    x.append(' comment: %s' % cm.comment)

                x.append(')')

                string.append(''.join(x))

            elif cm.comment is not None:
                string.append('(%s)' % cm.comment)
            
            strings.append(' '.join(string))
        #--- End: for

        return strings
    #--- End: def

    def netcdf_translation(self, f):
        '''

Translate netCDF variable names.

:Parameters:

    f : Field
        The field which provides the translation.

:Returns:

    out : CellMethods
        A new cell methods instance with translated names.

**Examples**

>>> c = CellMethods('time: mean lon: mean')
>>> d = c.netcdf_translation(f)

'''
        cell_methods = self.copy()

        domain = f.domain

        # Change each 'name' value to a standard_name (or domain
        # coordinate identifier) and create the 'dim' key
            
        # From the CF conventions (1.5): In the specification of this
        # attribute, name can be a dimension of the variable, a scalar
        # coordinate variable, a valid standard name, or the word
        # 'area'.
        for cm in cell_methods._list:

            # Reset axis
            cm.axes = []

            if cm.names == ['area']:
                cm.axes.append(None)
                continue
            #--- End: if

            dim_coords = f.dims()

            # Still here?
            for i, name in enumerate(cm.names):
                axis = None
                for axis, ncdim in domain.nc_dimensions.iteritems():
                    if name == ncdim:
                        break
                    
                    axis = None
                #--- End: for                    

                if axis is not None:
                    # name is a netCDF dimension name (including
                    # scalar coordinates).
                    cm.axes.append(axis)
                    if axis in dim_coords:
                        cm.names[i] = dim_coords[axis].name('domain:%s' % axis)
                    else:
                        cm.names[i] = None
                else:                    
                    # name must be a standard name
                    cm.axes.append(domain.axis({'standard_name': name}, 
                                               role='d', exact=True))
            #--- End: for
        #--- End: for
    
        return cell_methods
    #--- End: def

#--- End: class
