import collections

from copy import deepcopy
from re import sub    as re_sub
from re import search as re_search
from ast import literal_eval as ast_literal_eval

from .functions import equals
from .functions import inspect as cf_inspect

from .data.data import Data

from . import _found_ESMF

_collapse_cell_methods = {
    'max'            : 'maximum',
    'mean'           : 'mean',
    'mid_range'      : 'mid_range',
    'min'            : 'minimum',
    'range'          : 'range',
    'sd'             : 'standard_deviation',
    'sum'            : 'sum',
    'var'            : 'variance',
    'sample_size'    : None, 
    'sum_of_weights' : None,
    'sum_of_weights2': None,
    }

# ====================================================================
#
# _CellMethod object
#
# ====================================================================

class _CellMethod(object):
    '''**Attributes**

============  ========================================================
Attribute     Description
============  ========================================================
`!names`      
`!intervals`  
`!method`     
`!over`       
`!where`      
`!within`     
`!comment`    
`!axes`       
============  ========================================================

    '''
    def __init__(self):
        '''
'''
        self.axes      = ()
        self.names     = ()
        self.intervals = ()
        self.method    = None
        self.comment   = None
        self.where     = None
        self.within    = None
        self.over      = None
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

'''
        return self.copy()
    #--- End: def

    def __hash__(self):
        '''

x.__hash__() <==> hash(x)

'''
        return hash(str(self))
    #--- End: if

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return '<CF _CellMethod: %s>' % str(self)
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

Return a CF-netCDF-like string of the cell method.

Note that if the intention use this string in a CF-netCDF cell_methods
attribute then the cell method's `!name` attribute may need to be
modified, where appropriate, to reflect netCDF variable names.

'''
        string = []
        
        x = []
        for axis, name in zip(self.axes, self.names):
            if name is None:
                if axis is not None:
                    name = axis
                else:
                    name = '?'

            x.append('%s:' % name)
        #--- End: for
        string.extend(x)

        method = self.method
        if method is None:
            method = ''

        string.append(method)

        for portion in ('within', 'where', 'over'):
            p = getattr(self, portion, None)
            if p is not None:
                string.extend((portion, p))
        #--- End: for

        intervals = self.intervals
        if intervals:
            x = ['(']

            y = ['interval: %s' % data for data in intervals]
            x.append(' '.join(y))

            if self.comment is not None:
                x.append(' comment: %s' % self.comment)

            x.append(')')

            string.append(''.join(x))

        elif self.comment is not None:
            string.append('(%s)' % self.comment)

        return ' '.join(string)
    #--- End: def

    def __eq__(self):
        '''

x.__eq__(y) <==> x==y

'''
        return self.equals(y)
    #--- End: def

    def __ne__(self, other):
        '''

x.__ne__(y) <==> x!=y

'''
        return not self.__eq__(other)
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``c.copy()`` is equivalent to ``copy.deepcopy(c)``.

:Returns:

    out : 
        The deep copy.

:Examples:

>>> d = c.copy()

'''       
        new = _CellMethod.__new__(_CellMethod)

        new.axes    = self.axes     
        new.names   = self.names    
        new.method  = self.method   
        new.comment = self.comment  
        new.where   = self.where    
        new.within  = self.within   
        new.over    = self.over     

        new.intervals = tuple([data.copy() for data in self.intervals])

        return new
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False):
        '''

True if two cell methods are equal, False otherwise.

The `!axes` attribute is ignored in the comparison.

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

        names0 = self.names
        names1 = other.names        
#        indices0 = sorted(range(len(names0)), key=names0.__getitem__)
#        indices1 = sorted(range(len(names1)), key=names1.__getitem__)
#        names0 = sorted(names0)
 #       names1 = sorted(names1)

        if names0 != names1:
            if traceback:
                print("%s: Different names: %s != %s" %
                      (CellMethods.__name__, names0, names1))
            return False

        if None in names0 or None in names0:
            if traceback:
                print("%s: Missing names: %s, %s" %
                      (CellMethods.__name__, names0, names1))
                return False
            #--- End: if

        for attr in ('method', 'within', 'over', 'where', 'comment'):
            x = getattr(self, attr)
            y = getattr(other, attr)
            if x != y:
                if traceback:
                    print("%s: Different %s: %r != %r" %
                          (CellMethods.__name__, attr, x, y))
                return False

        intervals0 = self.intervals
        intervals1 = other.intervals
        if intervals0:
            if not intervals1:
                if traceback:
                    print("%s: Different intervals: %r != %r" %
                          (CellMethods.__name__, intervals0, intervals1))
                return False
            #--- End: if

            if len(intervals0) != len(intervals1):
                if traceback:
                    print("%s: Different intervals: %r != %r" %
                          (CellMethods.__name__, intervals0, intervals1))
                return False
            #--- End: if

            for data0, data1 in zip(intervals0, intervals1):
                if not data0.equals(data1, rtol=rtol, atol=atol,
                                    ignore_fill_value=ignore_fill_value,
                                    traceback=traceback):
                    if traceback:
                        print("%s: Different intervals: %r != %r" %
                              (CellMethods.__name__, data0, data1))
                    return False
     
        elif intervals1:
            if traceback:
                print("%s: Different intervals: %r != %r" %
                      (CellMethods.__name__, intervals0, intervals1))
            return False
        #--- End: if

        return True
    #--- End: def

    def equivalent(self, other, rtol=None, atol=None, traceback=False):
        '''

True if two cell methods are equivalent, False otherwise.

The `axes` attribute is ignored in the comparison.

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

:Examples:

'''
        if self is other:
            return True

        # Check that each instance is the same type
        if self.__class__ != other.__class__:
            if traceback:
                print("%s: Different types: %s != %s" %
                      (CellMethods.__name__,
                       self.__class__.__name__,
                       other.__class__.__name__))
            return False
        #--- End: if

        names0 = self.names
        names1 = other.names        
        indices0 = sorted(range(len(names0)), key=names0.__getitem__)
        indices1 = sorted(range(len(names1)), key=names1.__getitem__)
        names0 = sorted(names0)
        names1 = sorted(names1)

        if None in names0 or None in names1 or names0 != names1:
            if traceback:
                print("%s: Nonequivalent names: %r, %r" %
                      (CellMethods.__name__, names0, names1))
            return False
        #--- End: if

        for attr in ('method', 'within', 'over', 'where', 'comment'):
            x = getattr(self, attr)
            y = getattr(other, attr)
            if x != y:
                if traceback:
                    print("%s: Nonequivalent %s: %r, %r" %
                          (CellMethods.__name__, attr, x, y))
                return False
        #--- End: if

        intervals0 = self.intervals
        intervals1 = other.intervals
        if intervals0:
            if not intervals1:
                if traceback:
                    print("%s: Nonequivalent intervals: %r, %r" %
                          (CellMethods.__name__, intervals0, intervals1))
                return False
            #--- End: if

            if len(intervals0) == 1:
                intervals0 = intervals0 * len(names0)
                
            if len(intervals1) == 1:
                intervals1 = intervals1 * len(names1)

            if len(intervals0) != len(intervals1):
                if traceback:
                    print("%s: Nonequivalent intervals: %r, %r" %
                          (CellMethods.__name__, intervals0, intervals1))
                return False
            #--- End: if

            # Sort the intervals
            intervals0 = [intervals0[i] for i in indices0]
            intervals1 = [intervals1[i] for i in indices1]

            for data0, data1 in zip(intervals0, intervals1):
                if not data0.allclose(data1, rtol=rtol, atol=atol):
                    if traceback:                    
                        print("%s: Nonequivalent intervals: %r, %r" %
                              (CellMethods.__name__, data0, data1))
                    return False

        elif intervals1:
            if traceback:
                print("%s: Nonequivalent intervals: %r, %r" %
                      (CellMethods.__name__, intervals0, intervals1))
            return False
        #--- End: if

        return True
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

'''

    def __init__(self, cell_methods=None):
        '''

**Initialization**

:Parameters:

    string : str, optional
        Initialize new instance from a CF-netCDF-like cell methods
        string. See the `parse` method for details. By default an
        empty cell methods is created.

:Examples:

>>> c = cf.CellMethods()
>>> c = cf.CellMethods('time: max: height: mean')

'''               
        if not cell_methods:
            self._list = []
        elif isinstance(cell_methods, basestring):
            self._list = []
            self._parse(cell_methods)
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
s
'''     
        if isinstance(index, (int, long)):
            return type(self)((self._list[index],))
        else:
            return type(self)(self._list[index])
    #--- End: def

    def __hash__(self):
        '''

x.__hash__() <==> hash(x)

'''
        return hash(str(self))
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
        return '<CF %s: %s>' % (self.__class__.__name__, str(self))
    #--- End: def

    def __setitem__(self, index, value):        
        '''

x.__setitem__(index, value) <==> x[index]=value

'''
        if not isinstance(value, self.__class__):
            raise ValueError(
                "Can't assign %s to %s[%s]" %
                (value.__class__.__name__, self.__class__.__name__, index))
        
        if isinstance(index, (int, long)):
            index = slice(index, index+1)
            
        self._list[index] = value._list
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''        
        return ' '.join([str(cm) for cm in self._list])
    #--- End: def

    def __eq__(self, other):
        '''

x.__eq__(y) <==> x==y

'''
        return self.equals(other)
    #--- End: def

    def __ne__(self, other):
        '''

x.__ne__(y) <==> x!=y

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

    def _parse(self, string=None):
        '''

Parse a CF cell_methods string into this `cf.CellMethods` instance in
place.

:Parameters:

    string : str, optional
        The CF cell_methods string to be parsed into the
        `cf.CellMethods` object. By default the cell methods will be
        empty.

:Returns:

    None

:Examples:

>>> c = cf.CellMethods()
>>> c = c._parse('time: minimum within years time: mean over years (ENSO years)')    
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
            cm = _CellMethod()

            axes  = []
            names = []
            while cell_methods:
                if not cell_methods[0].endswith(':'):
                    break

                # Check that "name" ebds with colon? How? ('lat: mean (area-weighted) or lat: mean (interval: 1 degree_north comment: area-weighted)')

                names.append(cell_methods.pop(0)[:-1])            
                axes.append(None)
            #--- End: while
            cm.axes  = tuple(axes)
            cm.names = tuple(names)

            if not cell_methods:
                self.append(cm)
                break

            # Method
            cm.method = cell_methods.pop(0)

            if not cell_methods:
                self.append(cm)
                break

            # Climatological statistics and statistics which apply to
            # portions of cells
            while cell_methods[0] in ('within', 'where', 'over'):
                attr = cell_methods.pop(0)
                setattr(cm, attr, cell_methods.pop(0))
                if not cell_methods:
                    break
            #--- End: while
            if not cell_methods: 
                self.append(cm)
                break

            # interval and comment
            intervals = []
            if cell_methods[0].endswith('('):
                cell_methods.pop(0)

                if not (re_search('^(interval|comment):$', cell_methods[0])):
                    cell_methods.insert(0, 'comment:')
                           
                while not re_search('^\)$', cell_methods[0]):
                    term = cell_methods.pop(0)[:-1]

                    if term == 'interval':
                        interval = cell_methods.pop(0)
                        if cell_methods[0] != ')':
                            units = cell_methods.pop(0)
                        else:
                            units = None

                        try:
#                            parsed_interval = float(ast_literal_eval(interval))
                            parsed_interval = ast_literal_eval(interval)
                        except:
                            raise ValueError(
"Unparseable cell methods interval: {0!r}".format(
    interval+' '+units if units is not None else interval))
                            
                        try:
                            intervals.append(Data(parsed_interval, units))
                        except:
                            raise ValueError(
"Unparseable cell methods interval: {0!r}".format(
    interval+' '+units if units is not None else interval))
                            
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
            n_intervals = len(intervals)          
            if n_intervals > 1 and n_intervals != len(names):
                raise ValueError("0798798  ")

            cm.intervals = tuple(intervals)

            self.append(cm)
        #--- End: while
    #--- End: def

    @property
    def axes(self):
        return tuple([cm.axes for cm in self._list])
 
    @axes.setter
    def axes(self, value):
        if len(self._list) != 1:
            raise ValueError(
                "Must select a %s element to update. Consider c[i].axes=value" % 
                self.__class__.__name__)
        if not isinstance(value, (tuple, list)):
            raise ValueError("%s axes attribute must be a tuple or list" %
                             self.__class__.__name__)
        
        self._list[0].axes = tuple(value)
    #--- End: def

    @axes.deleter
    def axes(self):
        if len(self._list) != 1:
            raise ValueError(
                  "Must select a %s element to update. Consider del c[i].axes" %
                  self.__class__.__name__)
        
        self._list[0].axes = ()
    #--- End: def

    @property
    def comment(self):
        '''
         
Each cell method's comment keyword.

'''
        return tuple([cm.comment for cm in self._list])

    @comment.deleter
    def comment(self):
        if len(self._list) != 1:
            raise ValueError(
                  "Must select a %s element to update. Consider del c[i].comment" %
                  self.__class__.__name__)
        
        self._list[0].comment = None
    #--- End: def
 
    @property
    def method(self):
        '''

Each cell method's method keyword.

These describe how the cell values of field have been determined or
derived.

:Examples:

>>> c = cf.CellMethods('time: minimum area: mean')       
>>> c
<CF CellMethods: time: minimum area: mean>
>>> c.method
['minimum', 'mean']
>>> c[1].method = 'variance'
>>> c.method
['minimum', 'variance']
>>> c
<CF CellMethods: time: minimum area: variance>
>>> d = c[1]
>>> d
<CF CellMethods: area: variance>
>>> d.method
['variance']
>>> d.method = 'maximum'
>>> d.method
['maximum']
>>> c
<CF CellMethods: time: minimum area: maximum>

'''
        return tuple([cm.method for cm in self._list])
    #--- End: def

    @method.setter
    def method(self, value):
        if len(self._list) != 1:
            raise ValueError(
                "Must select a %s element to update. Consider c[i].method=value" %
                self.__class__.__name__)
        
        self._list[0].method = value
    #--- End: def
 
    @method.deleter
    def method(self):
        if len(self._list) != 1:
            raise ValueError(
                  "Must select a %s element to update. Consider del c[i].method" %
                  self.__class__.__name__)
        
        self._list[0].method = None
    #--- End: def
 
    @property
    def names(self):
        '''
         
Each cell method's name keyword(s).

:Examples:

>>> c = cf.CellMethods('time: minimum area: mean')       
>>> c
<CF CellMethods: time: minimum area: mean>
>>> c.names
(('time',), ('area',))
>>> c[1].names = ['lat', 'lon']
>>> c.names 
(('time',), ('lat', 'lon'))
>>> c
<CF CellMethods: time: minimum lat: lon: mean>
>>> d = c[1]
>>> d
<CF CellMethods: lat: lon: mean>
>>> d.names
(('lat', 'lon'),)
>>> d.names = ('area',)
>>> d.names
(('area',),)
>>> c
<CF CellMethods: time: minimum area: mean>

'''        
        return tuple([cm.names for cm in self._list])

    @names.setter
    def names(self, value):
        if len(self._list) != 1:
            raise ValueError(
                "Must select a %s element to update. Consider c[i].names=value" %
                self.__class__.__name__)
        if not isinstance(value, (list, tuple)):
            raise ValueError("%s names attribute must be a tuple or list" % 
                             self.__class__.__name__)

        self._list[0].names = tuple(value)

        # Make sure that axes has the same number of elements as names
        len_value = len(value)
        if len_value != len(self.axes[0]):
            self.axes = (None,) * len_value
    #--- End: def
 
    @names.deleter
    def names(self):
        if len(self._list) != 1:
            raise ValueError(
                  "Must select a %s element to update. Consider del c[i].names" %
                  self.__class__.__name__)
        
        self._list[0].names = ()
    #--- End: def
 
    @property
    def intervals(self):
        '''

Each cell method's interval keyword(s).

:Examples:

>>> c = cf.CellMethods('time: minimum (interval: 1 hr) lat: lon: mean (interval: 0.1 degree_N interval: 0.2 degree_E)')
>>> c
<CF CellMethods: time: minimum (interval: 1 hr) lat: lon: mean (interval: 0.1 degree_N interval: 0.2 degree_E)>
>>> c.intervals
[[<CF Data: 1 hr>], [<CF Data: 0.1 degree_N>, <CF Data: 0.2 degree_E>]]
>>> c[0].intervals = ['3600 seconds']
>>> c.intervals
>>> c[0].intervals
[[<CF Data: 3600 seconds>]]
>>> c[0].intervals = [cf.Data(60, 'minutes')]
>>> c[0].intervals
[[<CF Data: 60 minutes>]]
>>> c[0].intervals = [1]
>>> c[0].intervals
[[<CF Data: 1 >]]
>>> del c[0].intervals
>>> c.intervals
>>> [[], [<CF Data: 0.1 degree_N>, <CF Data: 0.2 degree_E>]]
>>> c
<CF CellMethods: time: minimum lat: lon: mean (interval: 0.1 degree_N interval: 0.2 degree_E)>

'''
        return tuple([cm.intervals for cm in self._list])

    @intervals.setter
    def intervals(self, value):
        if len(self._list) != 1:
            raise ValueError(
                "Must select a %s element to update. Consider c[i].intervals=value" %
                self.__class__.__name__)
        if not isinstance(value, (tuple, list)):
            raise ValueError(
                "%s intervals attribute must be a tuple or list, not a %s" %
                (self.__class__.__name__, value.__class__.__name__))
        
        # Parse the intervals
        values = []
        for interval in value:
            if isinstance(interval, basestring):
                i = interval.split()

                try:
                    x = ast_literal_eval(i.pop(0))
                except:
                    raise ValueError(
                        "Unparseable cell methods interval: %r" % interval)

                if interval:
                    units = ' '.join(i)
                else:
                    units = None
                    
                try:
                    d = Data(x, units)
                except:
                    raise ValueError(
                        "Unparseable cell methods interval: %r" % interval)
            else:
                try:
                    d = Data.asdata(interval, copy=True)
                except:
                    raise ValueError(
                        "Unparseable cell methods interval: %r" % interval)

            #--- End: if
            
            if d.size != 1:
                raise ValueError(
                    "Unparseable cell methods interval: %r" % interval)
                
            if d.ndim > 1:
                d.squeeze(i=True)

            values.append(d)
        #--- End: for

        self._list[0].intervals = tuple(values)
    #--- End: def
 
    @intervals.deleter
    def intervals(self):
        if len(self._list) != 1:
            raise ValueError(
                  "Must select a %s element to update. Consider del c[i].intervals" %
                  self.__class__.__name__)
        
        self._list[0].intervals = ()
    #--- End: def
 
    @property
    def over(self):
        '''
         
Each cell method's over keyword.

These describe how climatological statistics have been derived.

.. seealso:: `within`

:Examples:

>>> c = cf.CellMethods('time: minimum area: mean')       
>>> c
<CF CellMethods: time: minimum time: mean>
>>> c.over
[None, None]
>>> c[0].within = 'years'
>>> c[1].over = 'years'
>>> c.over
>>> [None, 'years']
>>> c
<CF CellMethods: time: minimum within years time: mean over years>
>>> d = c[1]
>>> d
<CF CellMethods: time: mean over years>
>>> del d.over
>>> d.over
[None]
>>> d
<CF CellMethods: time: mean>
>>> del c[0].within
>>> c.within
()        
>>> c
<CF CellMethods: time: minimum time: mean>

'''
        return tuple([cm.over for cm in self._list])
    #--- End: def

    @over.setter
    def over(self, value):
        if len(self._list) != 1:
            raise ValueError(
                  "Must select a %s element to update. Consider c[i].over=value" %
                  self.__class__.__name__)
        
        self._list[0].over = value
    #--- End: def
 
    @over.deleter
    def over(self):
        if len(self._list) != 1:
            raise ValueError(
                  "Must select a %s element to update. Consider del c[i].over" %
                  self.__class__.__name__)
        
        self._list[0].over = None
    #--- End: def
 
    @property
    def where(self):
        '''
         
Each cell method's where keyword.

'''
        return tuple([cm.where for cm in self._list])
    #--- End: def
 
    @where.setter
    def where(self, value):
        if len(self._list) != 1:
            raise ValueError("Must select a %s element to update. Consider c[i].where=value" %
                             self.__class__.__name__)
        
        self._list[0].where = value
    #--- End: def
 
    @where.deleter
    def where(self):
        if len(self._list) != 1:
            raise ValueError(
                  "Must select a %s element to update. Consider del c[i].where" %
                  self.__class__.__name__)
        
        self._list[0].where = None
    #--- End: def
 
    @property
    def within(self):
        '''
         
Each cell method's within keyword.

These describe how climatological statistics have been derived.

.. seealso:: `over`

:Examples:

>>> c = cf.CellMethods('time: minimum area: mean')       
>>> c
<CF CellMethods: time: minimum time: mean>
>>> c.within
(None, None)
>>> c[0].within = 'years'
>>> c[1].over = 'years'
>>> c.within
>>> ('years', None)
>>> c
<CF CellMethods: time: minimum within years time: mean over years>
>>> d = c[0]
>>> d
<CF CellMethods: time: minimum within years>
>>> del d.within
>>> d.within
(None,)
>>> d
<CF CellMethods: time: minimum>
>>> del c[1].over
>>> c
<CF CellMethods: time: minimum time: mean>

'''
        return tuple([cm.within for cm in self._list])
    #--- End: def

    @within.setter
    def within(self, value):
        if len(self._list) != 1:
            raise ValueError(
                "Must select a %s element to update. Consider c[i].within=value" %
                self.__class__.__name__)
        
        self._list[0].within = value
    #--- End: def
 
    @within.deleter
    def within(self):
        if len(self._list) != 1:
            raise ValueError(
                  "Must select a %s element to update. Consider del c[i].within" %
                  self.__class__.__name__)
        
        self._list[0].within = None
    #--- End: def
 
    def copy(self):
        '''

Return a deep copy.

``c.copy()`` is equivalent to ``copy.deepcopy(c)``.

:Returns:

    out : 
        The deep copy.

:Examples:

>>> d = c.copy()

'''   
        new = CellMethods.__new__(CellMethods)
        new._list = [cm.copy() for cm in self._list]
        return new
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

:Examples:

'''
         if prefix is None:
             prefix = self.__class__.__name__
                              
         string = []
         
         for i, cm in enumerate(self._list):
             string.append('%s[%d] -> %s' % (prefix, i, cm))
             
         string = '\n'.join(string)
         
         if display:
             print string
         else:
             return string
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False):
        '''

True if two cell methods are equal, False otherwise.

The `axes` attribute is ignored in the comparison.

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

        if len(self._list) != len(other._list):
            if traceback:
                print("%s: Different numbers of methods: %d != %d" %
                      (self.__class__.__name__,
                       len(self._list), len(other._list)))
            return False
        #--- End: if
    
        for cm0, cm1 in zip(self._list, other._list):
            if not cm0.equals(cm1, rtol=rtol, atol=atol,
                              ignore_fill_value=ignore_fill_value,
                              traceback=traceback):
                return False 
        #--- End: for

        return True
    #--- End: def

    def equivalent(self, other, rtol=None, atol=None, traceback=False):
        '''

True if two cell methods are equivalent, False otherwise.

The `axes` attributes are ignored in the comparison.

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

:Examples:

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

        if len(self._list) != len(other._list):
            if traceback:
                print("%s: Different numbers of methods: %d != %d" %
                      (self.__class__.__name__,
                       len(self._list), len(other._list)))
            return False
        #--- End: if
    
        for cm0, cm1 in zip(self._list, other._list):
            if not cm0.equivalent(cm1, rtol=rtol, atol=atol,
                                  traceback=traceback):
                return False 
        #--- End: for

        return True
    #--- End: def

    def has_cellmethod(self, other):
        '''

Return True if and only if this cell methods is a super set of another.

:Parameters:

    other : cf.CellMethods
        The other cell methods for comparison.

:Returns:
    out : bool
        Whether or not this cell methods is a super set of the other.

:Examples:

'''
        if len(other) != 1:
            return False

        found_match = False

        cm1 = other._list[0]
        for cm in self._list:
            if cm.equivalent(cm1):
                found_match = True
                break
        #--- End: for

        return found_match
    #--- End: def

    def extend(self, value):
        self._list.extend(value._list)
    #--- End: def

    def insert(self, index, value):
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

    def netcdf_translation(self, f):
        '''

Translate netCDF variable names stored in the `!names` attribute into 
`axes` and `names` attributes.

:Parameters:

    f : cf.Field
        The field which provides the translation.

:Returns:

    out : cf.CellMethods
        A new cell methods instance with translated names.

:Examples:

>>> c = cf.CellMethods('t: mean lon: mean')
>>> c.names = (('t',), ('lon',))
>>> c.axes = ((None,), (None,))
>>> d = c.netcdf_translation(f)
>>> d.names = (('time',), ('longitude',))
>>> d.axes = (('dim0',), ('dim2',))
>>> d
<CF CellMethods: 'time: mean longitude: mean')

        '''
        cell_methods = self.copy()

        domain = f.domain

        # Change each names value to a standard_name (or domain
        # coordinate identifier) and create the axes attribute.
            
        # From the CF conventions (1.5): In the specification of this
        # attribute, name can be a dimension of the variable, a scalar
        # coordinate variable, a valid standard name, or the word
        # 'area'.
        for cm in cell_methods._list:
            names = cm.names

            if names == ('area',):
                cm.axes = (None,)
                continue
            #--- End: if

            names = list(names)
            axes  = []

            dim_coords = f.dims()

            # Still here?
            for i, name in enumerate(names):
                axis = None
                for axis, ncdim in domain.nc_dimensions.iteritems():
                    if name == ncdim:
                        break
                    
                    axis = None
                #--- End: for                    

                if axis is not None:
                    # name is a netCDF dimension name (including
                    # scalar coordinates).
                    axes.append(axis)
                    if axis in dim_coords:
                        names[i] = dim_coords[axis].name('domain:%s' % axis)
                    else:
                        names[i] = None
                else:                    
                    # name must be a standard name
                    axes.append(domain.axis({'standard_name': name}, 
                                            role='d', exact=True))
            #--- End: for

            cm.names = tuple(names)
            cm.axes  = tuple(axes)
        #--- End: for
    
        return cell_methods
    #--- End: def

    def netcdf_names(self, axis_to_ncdim, axis_to_ncscalar):
        '''

Translate `names` to CF-netCDF names.

:Parameters:

    axis_to_ncdim: dict
        The first dictionary which provides the translation.

    axis_to_ncscalar: dict
        The alternative dictionary which provides the translation.

:Returns:

    out : cf.CellMethods
        A new cell methods instance with translated names.

:Examples:

>>> c = cf.CellMethods('t: mean lon: mean')
>>> c.names = (('t',), ('lon',))
>>> c.axes = ((None,), (None,))
>>> d = c.netcdf_translation(f)
>>> d.names = (('time',), ('longitude',))
>>> d.axes = (('dim0',), ('dim2',))
>>> d
<CF CellMethods: 'time: mean longitude: mean')

        '''
        new = self.copy()

        for cm in new._list:
            if cm.names == ('area',):
                continue

            names = []
            for axis, name in zip(cm.axes, cm.names):
                names.append(
                    axis_to_ncdim.get(axis,
                                      axis_to_ncscalar.get(axis,
                                                           name)))
            #--- End: for
            cm.names = tuple(names)
        #--- End: for

        return new
    #--- End: def

    def set_axes(self, f, override=False):
        '''Create new cell methods with `axes` inferred from `names`.

:Parameters:

    f : cf.Field
        The field providing the translation.
        
    override : bool, optional
        If True then change existing `axes` elements. By default
        exisiting `axes` elements are not changed.

:Returns:

    out : cf.CellMethods
        A new cell methods instance

:Examples:

>>> c = cf.CellMethods('t: mean lon: mean')
>>> c.names = (('t',), ('lon',))
>>> c.axes = ((None,), (None,))
>>> d = c.netcdf_translation(f)
>>> d.names = (('time',), ('longitude',))
>>> d.axes = (('dim0',), ('dim2',))
>>> d
<CF CellMethods: 'time: mean longitude: mean')

        '''
        new = self.copy()

        for cm in new._list:
            names = cm.names

            if names == ('area',):
                cm.axes = (None,)
                continue
                
            cm.axes = tuple([(f.domain.axis(name)
                              if axis is None or override else
                              axis)
                             for axis, name in zip(cm.axes, names)])
        #--- End: for

        return new
    #--- End: def

#--- End: class
