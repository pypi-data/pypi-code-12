import collections

from copy import deepcopy

from operator import truediv  as truediv
from operator import itruediv as itruediv

from .functions import RTOL, ATOL, equals

# ====================================================================
#
# List object
#
# ====================================================================

class List(collections.MutableSequence):
    '''

A list-like object with attributes.

'''
    def __init__(self, elements=None):
        '''

**Initialization**

:Parameters:

    sequence : iterable, optional
         Define a new list with these elements.

'''
        if not elements:
            self._list = []
        elif isinstance(elements, List):
            self._list = elements._list
        else:
            self._list = list(elements)
    #--- End: def

    def __contains__(self, item):
        '''

Implement membership test operators.

x.__contains__(y) <==> y in x

Compares objects with the `cf.equals` function rather than their
`!__eq__` methods.

'''
        for x in self._list:
            if equals(item, x):
                return True
        #--- End: for

        return False
    #--- End: def
    
    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

''' 
        return self.copy()
    #--- End: def

    def __delitem__(self, index):
        '''

x.__delitem__(index) <==> del x[index]

'''
        del self._list[index]
    #--- End: def

    def __getitem__(self, index):
        '''

x.__getitem__(index) <==> x[index]

'''
        if isinstance(index, (int, long)):
            # index is an integer so return the element
            return self._list[index]
        else:
            # index is a slice, so return a List of the elements
            return type(self)(self._list[index])
    #--- End: def

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
        return repr(self._list)
    #--- End: def

#    def __setattr__(self, attr, value):
#         '''
#
#x.__setattr__(attr, value) <==> x.attr=value
#
#'''
#         if hasattr(self, attr):             
#             super(List, self).__setattr__(attr, value)
#         else:
#             raise AttributeError("'%s' object has no attribute '%s'" % 
#                                  (self.__class__.__name__, attr))
#    #--- End: def

    def __setitem__(self, index, value):        
        '''

x.__setitem__(index, value) <==> x[index]=value

'''
        if not isinstance(value, List):
            self._list[index] = value
        else:
            self._list[index] = value._list
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return str(self._list)
    #--- End: def

    def __eq__(self, y):
        '''

x.__eq__(y) <==> x==y

'''
        return type(self)([f == y for f in self._list])
    #--- End: def

    def __ne__(self, y):
        '''

x.__ne__(y) <==> x!=y

'''
        return type(self)([f != y for f in self._list])
    #--- End: def

    def __ge__(self, y):
        '''

x.__ge__(y) <==> x>=y

'''
        return type(self)([f >= y for f in self._list])
    #--- End: def

    def __gt__(self, y):
        '''

x.__gt__(y) <==> x<y

'''
        return type(self)([f > y for f in self._list])
    #--- End: def

    def __le__(self, y):
        '''

x.__le__(y) <==> x<=y


'''
        return type(self)([f <= y for f in self._list])
    #--- End: def

    def __lt__(self, y):
        '''

x.__lt__(y) <==> x<y

'''
        return type(self)([f < y for f in self._list])
    #--- End: def

    def __add__(self, y):
        '''

The binary arithmetic operation ``+``

x.__add__(y) <==> x+y

        '''
        return type(self)([f + y for f in self._list])
    #--- End: def

    def __sub__(self, y):
        '''

The binary arithmetic operation ``-``

x.__sub__(y) <==> x-y

'''
        return type(self)([f - y for f in self._list])
    #--- End: def

    def __mul__(self, y):
        '''

The binary arithmetic operation ``*``


x.__mul__(y) <==> x*y

'''
        return type(self)([f * y for f in self._list])
    #--- End: def

    def __div__(self, y):
        '''

The binary arithmetic operation ``/``

x.__div__(y) <==> x/y

'''
        return type(self)([f / y for f in self._list])
    #--- End: def

    def __floordiv__(self, y):
        '''

The binary arithmetic operation ``//``

x.__floordiv__(y) <==> x//y

'''
        return type(self)([f // y for f in self._list])
    #--- End: def

    def __truediv__(self, y):
        '''

The binary arithmetic operation ``/`` (true division)

x.__truediv__(y) <==> x/y

'''
#        return type(self)([f.__truediv__(y) for f in self._list])
        return type(self)([truediv(f, y) for f in self._list])
    #--- End: def

    def __radd__(self, y):
        '''

x.__radd__(y) <==> y+x

'''
        return type(self)([y + f for f in self._list])
    #--- End: def

    def __rsub__(self, y):
        '''

x.__rsub__(y) <==> y-x

'''
        return type(self)([y - f for f in self._list])
    #--- End: def

    def __rmul__(self, y):
        '''

x.__rmul__(y) <==> y*x

'''
        return type(self)([y*f for f in self._list])
    #--- End: def

    def __rdiv__(self, y):
        '''

x.__rdiv__(y) <==> y/x

'''
        return type(self)([y/f for f in self._list])
    #--- End: def

    def __rfloordiv__(self, y):
        '''

x.__rfloordiv__(y) <==> y//x

'''
        return type(self)([y//f for f in self._list])
    #--- End: def

    def __rtruediv__(self, y):
        '''

The binary arithmetic operation ``/`` (true division) with reflected
operands

x.__rtruediv__(y) <==> y/x

'''
        return type(self)([f.__rtruediv__(y) for f in self._list])
#        return type(self)([rtruediv(f, y) for f in self._list])
    #--- End: def

    def __iadd__(self, y):
        '''

x.__iadd__(y) <==> x+=y

'''
        for f in self._list:
            f += y
        return self
    #--- End def

    def __isub__(self, y):
        '''

x.__isub__(y) <==> x-=y

'''
        for f in self._list:
            f -= y
        return self
    #--- End def

    def __imul__(self, y):        
        '''

x.__imul__(y) <==> x*=y

'''
        for f in self._list:
            f *= y
        return self
    #--- End def

    def __idiv__(self, y):
        '''

x.__idiv__(y) <==> x/=y

'''
        for f in self._list:
            f /= y
        return self
    #--- End def

    def __ifloordiv__(self, y):
        '''

x.__ifloordiv__(y) <==> x//=y

'''
        for f in self._list:
            f //= y
        return self
    #--- End def

    def __itruediv__(self, y):
        '''

The augmented arithmetic assignment ``/=`` (true division)

x.__itruediv__(y) <==> x/=y

'''
        for f in self._list:
#            f.__itruediv__(y)
            itruediv(f, y)
        return self
    #--- End def

    def __pow__(self, y, modulo=None):
        '''

The binary arithmetic operations ``**`` and ``pow``

x.__pow__(y) <==> x**y

'''
        if modulo is not None:
            raise NotImplementedError(
                "3-argument power not supported for '%s'" %
                self.__class__.__name__)

        return type(self)([f ** y for f in self._list])
    #--- End: def

    def __ipow__(self, y, modulo=None):
        '''

The augmented arithmetic assignment ``**=``

x.__ipow__(y) <==> x**=y

'''
        if modulo is not None:
            raise NotImplementedError(
                "3-argument power not supported for '%s'" %
                self.__class__.__name__)

        for f in self._list:
            f **= y
        return self
    #--- End: def

    def __rpow__(self, y, modulo=None):
        '''

The binary arithmetic operations ``**`` and ``pow`` with reflected
operands

x.__rpow__(y) <==> y**x

'''
        if modulo is not None:
            raise NotImplementedError(
                "3-argument power not supported for '%s'" %
                self.__class__.__name__)

        return type(self)([y ** f for f in self._list])
    #--- End: def

    def __and__(self, y):
        '''

The binary bitwise operation ``&``

x.__and__(y) <==> x&y

'''
        return type(self)([f & y for f in self._list])
    #--- End: def

    def __iand__(self, y):
        '''

The augmented bitwise assignment ``&=``

x.__iand__(y) <==> x&=y

'''
        for f in self._list:
            f &= y
        return self
    #--- End: def

    def __rand__(self, y):
        '''

The binary bitwise operation ``&`` with reflected operands

x.__rand__(y) <==> y&x

'''
        return type(self)([y & f for f in self._list])
    #--- End: def

    def __or__(self, y):
        '''

The binary bitwise operation ``|``

x.__or__(y) <==> x|y

'''
        return type(self)([f | y for f in self._list])
    #--- End: def

    def __ior__(self, y):
        '''

The augmented bitwise assignment ``|=``

x.__ior__(y) <==> x|=y

'''
        for f in self._list:
            f |= y
        return self
    #--- End: def

    def __ror__(self, y):
        '''

The binary bitwise operation ``|`` with reflected operands

x.__ror__(y) <==> y|x

'''
        return type(self)([y | f for f in self._list])
    #--- End: def

    def __xor__(self, y):
        '''

The binary bitwise operation ``^``

x.__xor__(y) <==> x^y

'''
        return type(self)([f ^ y for f in self._list])
    #--- End: def

    def __ixor__(self, y):
        '''

The augmented bitwise assignment ``^=``

x.__ixor__(y) <==> x^=y

'''
        for f in self._list:
            f ^= y
        return self
    #--- End: def

    def __rxor__(self, y):
        '''

The binary bitwise operation ``^`` with reflected operands

x.__rxor__(y) <==> y^x

'''
        return type(self)([y ^ f for f in self._list])
    #--- End: def

    def __ixor__(self, y):
        '''

The augmented bitwise assignment ``^=``

x.__ixor__(y) <==> x^=y

'''
        for f in self._list:
            f ^= y
        return self
    #--- End: def

    def __rxor__(self, y):
        '''

The binary bitwise operation ``^`` with reflected operands

x.__rxor__(y) <==> y^x

'''
        return type(self)([y ^ f for f in self._list])
    #--- End: def

    def __lshift__(self, y):
        '''

The binary bitwise operation ``<<``

x.__lshift__(y) <==> x<<y

'''
        return type(self)([f << y for f in self._list])
    #--- End: def

    def __ilshift__(self, y):
        '''

The augmented bitwise assignment ``<<=``

x.__ilshift__(y) <==> x<<=y

'''
        for f in self._list:
            f <<= y
        return self
    #--- End: def

    def __rlshift__(self, y):
        '''

The binary bitwise operation ``<<`` with reflected operands

x.__rlshift__(y) <==> y<<x

'''
        return type(self)([y << f for f in self._list])
    #--- End: def

    def __rshift__(self, y):
        '''

The binary bitwise operation ``>>``

x.__rshift__(y) <==> x>>y

'''
        return type(self)([f >> y for f in self._list])
    #--- End: def

    def __irshift__(self, y):
        '''

The augmented bitwise assignment ``>>=``

x.__irshift__(y) <==> x>>=y

'''
        for f in self._list:
            f >>= y
        return self
    #--- End: def

    def __rrshift__(self, y):
        '''

The binary bitwise operation ``>>`` with reflected operands

x.__rrshift__(y) <==> y>>x

'''
        return type(self)([y >> f for f in self._list])
    #--- End: def

    def __mod__(self, y):
        '''

The binary arithmetic operation ``%``

x.__mod__(y) <==> x % y

'''
        return type(self)([f % y for f in self._list])
    #--- End: def

    def __imod__(self, y):
        '''

The binary arithmetic operation ``%=``

x.__imod__(y) <==> x %= y

'''
        for f in self._list:
            f %= y
        return self
    #--- End def

    def __rmod__(self, other):
        '''

The binary arithmetic operation ``%`` with reflected operands

x.__rmod__(y) <==> y % x

''' 
        return type(self)([y % f for f in self._list])
    #--- End: def

    def __abs__(self):
        '''

The unary arithmetic operation ``abs``

x.__abs__() <==> abs(x)

'''
        return type(self)([abs(f) for f in self._list])
    #--- End: def

    def __neg__(self):
        '''

The unary arithmetic operation ``-``

x.__neg__() <==> -x

'''
        return type(self)([-f for f in self._list])
    #--- End: def

    def __invert__(self):
        '''

The unary bitwise operation ``~``

x.__invert__() <==> ~x

'''
        return type(self)([~f for f in self._list])
    #--- End: def

    def __pos__(self):
        '''

The unary arithmetic operation ``+``

x.__pos__() <==> +x

'''
        return type(self)([+f for f in self._list])
    #--- End: def

#    def __add__(self, other):
#        '''
#
#x.__add__(y) <==> x+y
#
#'''
#        new = type(self)()
#        new._list = self._list[:]
#        new.extend(other)
#        return new
#    #--- End: def
#
#    def __iadd__(self, other):
#        '''
#x.__iadd__(y) <==> x+=y
#
#'''
#        self.extend(other)
#        return self
#    #--- End: def
#
#    def __mul__(self, other):
#        '''
#x.__mul__(n) <==> x*n
#
#'''
#        return type(self)(self._list * other)
#    #--- End: def
#
#    def __imul__(self, other):
#        '''
#x.__imul__(n) <==> x*=n
#
#'''
#        self._list = self._list * other
#        return self
#    #--- End: def
#
#    def __rmul__(self, other):
#        '''
#x.__rmul__(n) <==> x*n
#
#'''
#        return self.__mul__(other)
#    #--- End: def

    def count(self, value):
        '''

Return the number of occurrences of a value

Elements are compared with the `cf.equals` function.

``fl.count(value)`` is equivalent to ``len([None for f in fl if
cf.equals(value, f)])``.

:Parameters:

    value : 
        The value to search for in the list.

:Returns:

   out : int
       The number of occurrences of the value.

'''
        return len([None for x in self._list if equals(value, x)])
    #--- End def

    def copy(self):
        '''

Return a deep copy.

``fl.copy()`` is equivalent to ``copy.deepcopy(fl)``.

:Returns:

    out : 
        The deep copy.

:Examples:

>>> gl = fl.copy()

'''
        return type(self)(deepcopy(self._list))
    #--- End: def

    def delattr(self, attr):
         '''

Delete a named attribute on each element of the list.

``fl.delattr(attr)`` is equivalent to ``for f in fl: del f.attr``.

:Parameters:
 
    attr : str
        The attribute's name.

:Returns:

    None

.. seealso:: `getattr`, `hasattr`, `setattr`

:Examples:

>>> fl.getattr('foo')
['bar1', 'bar2']
>>> fl.delattr('foo')
>>> fl.getattr('foo', None)
[None, None]

'''
         for f in self._list:
             delattr(f, attr)
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False):
        '''

True if two instances are equal, False otherwise.

Two instances are equal if their attributes are equal and their
elements are equal pair-wise.

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

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        instances differ.

:Returns: 

    out : bool
        Whether or not the two instances are equal.

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

        # Check that the lists have the same number of elements
        if len(self) != len(other): 
            if traceback:
                print("%s: Different attributes: %s, %s" %
                      (self.__class__.__name__,
                       attrs.symmetric_difference(other.__dict__)))
            return False
        #--- End: if

        # Check the attributes
        attrs = set(self.__dict__)
        if attrs != set(other.__dict__):
            if traceback:
                print("%s: Different attributes: %s, %s" %
                      (self.__class__.__name__,
                       attrs.symmetric_difference(other.__dict__)))
            return False
        #--- End: if

        if rtol is None:
            rtol = RTOL()
        if atol is None:
            atol = ATOL()

        for attr, value in attrs - set(('_list',)):
            x = getattr(self, attr)
            y = getattr(other, attr)
            if not equals(x, y, rtol=rtol, atol=atol,
                          ignore_fill_value=ignore_fill_value,
                          traceback=traceback):
                if traceback:
                    print("%s: Different '%s': %s, %s" %
                          (self.__class__.__name__, attr, x, y))
                return False
        #--- End: for

        # Check the element values
        for x, y in zip(self._list, other._list):
            if not equals(x, y, rtol=rtol, atol=atol,
                          ignore_fill_value=ignore_fill_value,
                          traceback=traceback):
                if traceback:
                    print("%s: Different elements: %r, %r" %
                          (self.__class__.__name__, x, y))
                return False
        #--- End: for

        return True
    #--- End: def
    
    def getattr(self, attr, *default):
         '''

Get a named attribute from each element of the list.

``fl.getattr(attr, *default)`` is equivalent to ``cf.List(for f in fl:
getattr(f, attr, *default))``.

:Parameters:

    attr : str
        The attribute's name.

    default : *optional*
        When a default argument is given, it is returned when the
        attribute doesn't exist; without it, an exception is raised in
        that case.

:Returns:

    out : cf.List
        Each element's attribute value.

.. seealso:: `delattr`, `hasattr`, `setattr`

:Examples:

>>> fl.getattr('foo')
['bar1', 'bar2']
>>> del fl[1].foo
>>> fl.getattr('foo', None)
['bar1', None]

'''
         return List([getattr(f, attr, *default) for f in self._list])
    #--- End: def

    def hasattr(self, attr):
         '''

Return whether an attribute exists for each element of the list.

``fl.hasattr(attr)`` is equivalent to ``cf.List(for f in fl:
hasattr(f, attr))``.

:Parameters:

    attr : str
        The attribute's name.

:Returns:

    out : cf.List
        Whether each element has the attribute.

:Examples:

.. seealso:: `delattr`, `getattr`, `setattr`

>>> fl.getattr('foo')
['bar1', 'bar2']
>>> del fl[1].foo
>>> fl.getattr('foo', None)
['bar1', None]

'''
         return List([getattr(f, attr, *default) for f in self._list])
    #--- End: def

    def index(self, value, start=0, stop=None):
        '''

Return the first index of a value.

Elements are compared with the `cf.equals` function.

:Parameters:

    value :
        The value to search for in the list.

    start : int, optional
        Start looking from this index. By default, look from the
        beginning of the list.

    stop : int, optional
        Stop looking before this index. By default, look up to the end
        of the list.

:Returns:

    out : int
        The first index of the value.

'''      
        if start < 0:
            start = len(self) + start

        if stop is None:
            stop = len(self)
        elif stop < 0:
            stop = len(self) + stop

        for i, x in enumerate(self[start:stop]):
            if equals(value, x):
               return i + start
        #--- End: for

        raise ValueError("%s doesn't contain %r" % 
                         (self.__class__.__name__, value))
    #--- End: def

    def insert(self, index, value):
        # Insert an object before index.
        self._list.insert(index, value)
    #--- End: def

    def iter(self, name, *args, **kwargs):
        '''

Return an iterator over the results of a method applied to each
element.

``fl.iter(name, *args, **kwargs)`` is an equivalent to
``iter(f.name(*args, **kwargs) for f in fl)``.

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

'''
        return (getattr(f, method)(*args, **kwargs) for f in self._list)
    #--- End: def

    def method(self, callable_method, *args, **kwargs):
        '''

Return an list of the results of a method applied to each element.

``fl.method(name, *args, **kwargs)`` is equivalent to
``cf.List(f.name(*args, **kwargs) for f in fl)``.

:Parameters:

    name : str
        The name of the method to apply to each element.

    args, kwargs : *optional*
        The arguments to be used in the call to the named method.

:Returns:

    out : cf.List
        The results of the named method applied to each element.

.. seealso:: `iter`

:Examples:

>>> x = cf,List(['a, 'b', 'c'])
>>> x.method('upper)
['A, 'B', 'C']
>>> x.method('find', 'a')
[0, -1, -1]
>>> x
['a, 'b', 'c']

>>> x = cf.List([[3, 2, 1], [6, 5, 4]])
>>> x.method('sort')
[None, None, None]
>>> x
[[1, 2, 3], [4, 5, 6]]

'''
        return type(self)([getattr(x, callable_method)(*args, **kwargs)
                           for x in self._list])
    #--- End: def

    def setattr(self, attr, value):
         '''

Set a named attribute on each element of the list.

``fl.setattr(attr, value)`` is equivalent to ``for f in fl: f.attr =
value``.

:Parameters:

    attr : str
        The attribute's name.

    value :
        The value to set each attribute.

:Returns:

    None

.. seealso:: `delattr`, `getattr`, `hasattr`

:Examples:

>>> fl.setattr('foo', -99)
>>> fl.getattr('foo')
[-99, -99]

>>> fl.setattr('foo', [1, 2])
>>> fl.getattr('foo')
[[1, 2], [1, 2]]

'''
         for f in self._list:
             setattr(f, attr, value)
    #--- End: def

    def sort(self, cmp=None, key=None, reverse=False):
        self._list.sort(cmp=cmp, key=key, reverse=reverse)
#--- End: class


# ====================================================================
#
# Dict object
#
# ====================================================================

class Dict(collections.MutableMapping):
    '''

A dictionary-like object with attributes.

'''
    def __init__(self, *args, **kwargs):
        '''

**Initialization**

:Parameters:

    args, kwargs : *optional*
        Keys and values are initialized exactly as for a built-in
        dict.

'''
        self._dict = dict(*args, **kwargs)        
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

''' 
        return self.copy()
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return repr(self._dict)
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return str(self._dict)
    #--- End: def

    def __getitem__(self, key):
        '''

x.__getitem__(key) <==> x[key]

'''     
        return self._dict[key]
    #--- End: def

    def __setitem__(self, key, value):

        '''
x.__setitem__(key, value) <==> x[key]=value

'''
        self._dict[key] = value
    #--- End: def

    def __delitem__(self, key):
        '''

x.__delitem__(key) <==> del x[key]

'''
        del self._dict[key]
    #--- End: def

    def __iter__(self):
        '''

x.__iter__() <==> iter(x)

'''
        return iter(self._dict)
    #--- End: def

    def __len__(self):
        '''

x.__len__() <==> len(x)

'''
        return len(self._dict)
    #--- End: def

#    def __contains__(self, item):
#        '''
#Test for set membership using numerically tolerant equality.
#'''
#        for s in self:
#            if equals(item, s):
#                return True
#
#        return False
#    #--- End: def

    def __eq__(self, y):
        '''
x.__eq__(y) <==> x==y <==> x.equals(y)

'''
        return self.equals(y)
    #--- End: def

    def __ne__(self, y):
        '''
x.__ne__(y) <==> x!=y <==> not x.equals(y)

'''
        return not self.__eq__(y)
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``d.copy()`` is equivalent to ``copy.deepcopy(d)``.

:Returns:

    out : 
        The deep copy.

:Examples:

>>> e = d.copy()

'''
        new = type(self)()

        for attr, value in self.__dict__.iteritems():
            setattr(new, attr, deepcopy(value))

        return new
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False):
        '''

True if two instances are logically equal, False otherwise.

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
                print("%s: Different types: %s, %s" %
                      (self.__class__.__name__,
                       self.__class__.__name__,
                       other.__class__.__name__))
            return False
        #--- End: if

#        # Check the attributes
#        attrs = set(self.__dict__)
#        if attrs != set(other.__dict__):
#            if traceback:
#                print("%s: Different attributes: %s" %
#                      (self.__class__.__name__,
#                       attrs.symmetric_difference(other.__dict__)))
#            return False
#        #--- End: if

        if rtol is None:
            rtol = RTOL()
        if atol is None:
            atol = ATOL()

#        for attr in attrs.difference(('_dict',)):
#            x = getattr(self, attr)
#            y = getattr(other, attr)
#            if not equals(x, y, rtol=rtol, atol=atol, ignore_fill_value=ignore_fill_value, traceback=traceback):
#                if traceback:
#                    print("%s: Different '%s' attributes: %s, %s" %
#                          (self.__class__.__name__, attr, x, y))
#                return False
#        #--- End: for

        # Check that the keys are equal
        if set(self) != set(other):
            if traceback:
                print("%s: Different keys: %s" %
                      (self.__class__.__name__,
                       set(self).symmetric_difference(other)))
            return False
        #--- End: if

        # Check that the key values are equal
        for key, value in self.iteritems():
            if not equals(value, other[key], rtol=rtol, atol=atol,
                          ignore_fill_value=ignore_fill_value,
                          traceback=traceback):
                if traceback:
                    print("%s: Different '%s' values: %r, %r" %
                          (self.__class__.__name__, key,
                           value, other[key]))
                return False
        #--- End: for
                
        # Still here?
        return True
    #--- End: def

    def has_key(self, key):
        '''
'''
        return self._dict.has_key(key)
    #--- End: def

#--- End: class


# ====================================================================
#
# Set object
#
# ====================================================================

class Set(collections.MutableSet):
    '''

A dictionary-like object with attributes.

'''
    def __init__(self, arg=None):
        '''

'''
        if arg:
            self._set = set(arg)
        else:
            self._set = set()
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

''' 
        return self.copy()
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return '%s(%s)' % (self.__class__.__name__, list(self._set))
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return repr(self)
    #--- End: def

    def __iter__(self):
        '''

x.__iter__() <==> iter(x)

'''
        return iter(self._set)
    #--- End: def

    def __len__(self):
        '''

x.__len__() <==> len(x)

'''
        return len(self._set)
    #--- End: def

    def __contains__(self, item):
        '''

'''
        for x in self._set:
            if equals(item, x):
                return True

        return False
    #--- End: def
       
    def __eq__(self, y):
        '''

x.__eq__(y) <==> x==y <==> x.equals(y)

'''
        return self.equals(y)
    #--- Ens=Set(d: def

    def __ne__(self, y):
        '''

x.__ne__(y) <==> x!=y <==> not x.equals(y)

'''
        return not self.equals(y)
    #--- End: def

    def add(self, item):
        '''

Add an element to a set.
      
This has no effect if the element is already present.

'''
        self._set.add(item)
    #--- End: def

    def clear(self):
        '''

Remove all elements from this set.

'''
        self._set.clear()
    #--- End: def

    def copy(self):
        '''
        
Return a deep copy.

``s.copy()`` is equivalent to ``copy.deepcopy(s)``.

:Returns:

    out : 
        The deep copy.

:Examples:

>>> t = s.copy()

'''
        return type(self)(self._set)
    #--- End: def

    def discard(self, item):
        '''

Remove an element from a set if it is a member.
      
If the element is not a member, do nothing.

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
#
        self._set.discard(item)
    #--- End: def

    def equals(self, other, ignore_fill_value=False, traceback=False):
        '''

True if two instances are logically equal, False otherwise.

:Parameters:

    ignore_fill_value : bool, optional
        Ignored.

    traceback : bool, optional
        Ignored.

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
                print("%s: Different types: %s, %s" %
                      (self.__class__.__name__,
                       self.__class__.__name__,
                       other.__class__.__name__))
            return False
        #--- End: if

        return self._set == other._set
    #--- End: def

    def update(self, x):
        '''

Update a set with the union of itself and others.

'''
        self._set.update(x)
    #--- End: def

#--- End: class

