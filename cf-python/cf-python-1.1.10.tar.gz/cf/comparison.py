from copy import deepcopy
from re   import search as re_search
from itertools import izip
from operator import __and__ as operator_and
from operator import __or__  as operator_or

from numpy import ndarray   as numpy_ndarray
from numpy import vectorize as numpy_vectorize

from .cfdatetime import Datetime, dt
from .functions  import inspect    as cf_inspect
from .functions  import equals     as cf_equals
from .functions  import equivalent as cf_equivalent

from .data.data  import Data

# ====================================================================
#
# Comparison object
#
# ====================================================================

class Comparison(object):
    '''Store a comparison operation.

The comparison operation is an operator with a right hand side
operand. For example, an operator could be "strictly less than" and a
right hand side operand could 3.

Such a comparison (such as "strictly less than 3") may be evaluated
for an arbitrary left hand side operand, *x* (such as "is *x* strictly
less than 3?").

The result of the comparison is dependent on the object type of left
hand side operand, *x*. For example, if *x* is an integer then
evaluating "is *x* strictly less than 3?" will result in a boolean;
but if *x* is a `numpy` array then "is *x* strictly less than 3?" will
likely produce a numpy array of booleans.

The comparison is evaluated with its `evaluate` method or equivalently
with the ``==`` operator:

>>> c = cf.Comparison('lt', 3)
>>> c.evaluate(2)
True
>>> 2 == c
True
>>> c == 2
True
>>> 4 == c
False

The inverse of the comparison may be evaluated with the ``!=`` operator:

>>> c = cf.Comparison('wi', [3, 5])
>>> c.evaluate(4)
True
>>> 4 == c
True
>>> 4 != c
False
>>> c != 6
True

The following operators are supported:

=========  =========================================================  ===========
operator   Description                                                Constructor
=========  =========================================================  ===========
``'lt'``   Is *x* strictly less than a value                          `cf.lt`

``'le'``   Is *x* less than or equal to a value                       `cf.le`

``'gt'``   Is *x* strictly greater than a value                       `cf.gt`

``'ge'``   Is *x* greater than or equal to a value                    `cf.ge`

``'eq'``   Is *x* equal to a value                                    `cf.eq`

``'ne'``   Is *x* not equal to a value                                `cf.ne`

``'wi'``   Is *x* within a given range of values (range bounds        `cf.wi`
           included) 

``'wo'``   Is *x* without a given range of values (range bounds       `cf.wo`
           excluded)       

``'set'``  Is *x* equal to any member of a collection.                `cf.set`

``'has'``  Is value in a cell of *x*, if cells are defined.           `cf.has`
           Otherwise is *x* equal to a value.
=========  =========================================================  ===========

For the ``'wi'``, ``'wo '`` and ``'set'`` operators, if the left hand
side operand supports broadcasting over its elements (such as a
`numpy` array or a `cf.Field` object) then each element is tested
independently. For example:

>>> c = cf.Comparison('wi', [3, 4])
>>> c == [2, 3, 4]
False
>>> print c == numpy.array([2, 3, 4])
[ False  True  True]

As a convenience, for each operator there is an identically named
constructor function which returns the appropriate `cf.Comparison`
object. For example:

>>> cf.lt(3)
<CF Comparison: lt 3>


**Compound comparisons**

Multiple comparisons may be logically combined with the bitwise ``&``
and ``|`` operators to form a new `cf.Comparison` object. For example:

>>> c = cf.ge(3)
>>> d = cf.lt(5)
>>> e = c & d
>>> e 
>>> <CF Comparison: [(ge 3) & (lt 5)]>
>>> 4 == e
True
>>> f = c | d
<CF Comparison: [(ge 3) | (lt 5)]>
>>> 2 == f
True

Compound comparisons may be combined further:

>>> g = e | cf.wi(1.5, 2.5)
>>> g
<CF Comparison: [[(ge 3) & (lt 5)] | (wi (1.5, 2.5))]>
>>> 2 == g
True
>>> g & f
<CF Comparison: [[[(ge 3) & (lt 5)] | (wi (1.5, 2.5))] & [(ge 3) | (lt 5)]]>

If any of the component comparisons are for left hand side operand
attributes, then these are retained in a compound comparison. For
example:

>>> c = cf.ge(3)
>>> d = cf.lt(5, attr='A')
>>> e = c & d
>>> e = e.addattr('B')
>>> e
<CF Comparison: B[(ge 3) & A(lt 5)]>

In this example,

>>> x == e

is equivalent to 

>>> (x.B == cf.ge(3)) & (x.B.A == cf.lt(5))


**Attributes**

===============  ======================================================
Attribute        Description
===============  ======================================================
`!attr`          An attribute name such that this attribute of the
                 left hand side operand is compared, rather than the
                 operand itself. If there is more than one attribute
                 name then each is interpreted as an attribute of the
                 previous attribute.

`!operator`      The comparison operation (such as ``'lt'``, for
                 example). Always ``None`` for compound comparisons.

`!regex`         Whether or not string values are to be treated as
                 regular expressions. Always ``False`` for compound
                 comparisons.
===============  ======================================================

    '''

    def __init__(self, operator, value, units=None, regex=False, attr=None):
        '''

**Initialization**

:Parameters:

    operator : str
        The comparison operation.

    value :
        The right hand side of the comparison operation.

    units : str or cf.Units, optional
        The units of *value*. By default, the same units, if any, as
        the left hand side of the comparison operation are assumed.

    regex : str, optional
        If True then string values are to be treated as regular
        expressions, which are evaluated using the :py:obj:`re.search`
        function. Ignored for all operators except ``'eq'``, ``'ne'``
        and ``'set'``.

    attr : str, optional
        Specify an attribute name such that this attribute of the left
        hand side operand is compared, rather than the operand itself.

          Example: ``cf.Comparison('ge', 2, attr='ndim')`` with return
          ``True`` when evaluated for an array with two or more
          dimensions.

**Examples**

>>> cf.Comparison('le', 5.6)
<CF Comparison: (le 5.6)>
>>> cf.Comparison('gt', 5.6, 'metres')
<CF Comparison: (gt <CF Data: 5.6 metres>)>
>>> cf.Comparison('gt', cf.Data(5.6, 'metres'))
<CF Comparison: (gt <CF Data: 5.6 metres>)>
>>> cf.Comparison('wi', [2, 56])
<CF Comparison: (wi [2, 56])>
>>> cf.Comparison('set', [2, 56], 'seconds')
<CF Comparison: (set <CF Data: [2, 56] seconds>)>
>>> cf.Comparison('set', cf.Data([2, 56], 'seconds'))
<CF Comparison: (set <CF Data: [2, 56] seconds>)>
>>> cf.Comparison('eq', 'air_temperature')
<CF Comparison: (eq 'air_temperature')>
>>> cf.Comparison('eq', 'temperature', regex=True)
<CF Comparison: (eq 'temperature')>
>>> cf.Comparison('gt', 1, attr='ndim')
<CF Comparison: ndim(gt 1)>

'''
        if units is not None:
            value_units = getattr(value, 'Units', None)
            if value_units is None:
                value = Data(value, units)
            elif not value_units.equivalent(units):
                raise ValueError("sdfsdfsd99885109^^^^")
        #--- End: if

        self._operator = operator
        self._value    = value
        self._regex    = regex
        self._compound = False
        self._attr     = () if not attr else (attr,)

        self._bitwise_operator = None

        self._NotImplemented_RHS_Data_op = True
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

'''
        return self.copy()
    #--- End: def

    def __eq__(self, x):
        '''

x.__eq__(y) <==> x==y <==> x.evaluate(y)

'''
        return self._evaluate(x, ())
    #--- End: def

    def __ne__(self, x):
        '''

x.__ne__(y) <==> x!=y <==> (x==y)==False

'''
        return self._evaluate(x, ()) == False
    #--- End: def

    def __ge__(self, x):
        raise TypeError("Unsupported operand type(s) for >=: '%s' and '%s'" %
                        (self.__class__.__name__, x.__class__.__name__))
    #--- End: def

    def __gt__(self, x):
        raise TypeError("Unsupported operand type(s) for >: '%s' and '%s'" %
                        (self.__class__.__name__, x.__class__.__name__))
    #--- End: def

    def __le__(self, x):
        raise TypeError("Unsupported operand type(s) for <=: '%s' and '%s'" %
                        (self.__class__.__name__, x.__class__.__name__))
    #--- End: def

    def __lt__(self, x):
        raise TypeError("Unsupported operand type(s) for <: '%s' and '%s'" %
                        (self.__class__.__name__, x.__class__.__name__))
    #--- End: def

    def __and__(self, other):
        '''

x.__and__(y) <==> x&y

'''        

        C = type(self)
        new = C.__new__(C)
        
        new._operator         = None
        new._regex            = False
        new._compound         = (self, other)
        new._bitwise_operator = operator_and
        new._attr             = ()

        new._NotImplemented_RHS_Data_op = True
       
        return new
    #--- End: def

    def __iand__(self, other):
        '''

x.__iand__(y) <==> x&=y

'''        
        return self & other
    #--- End: def

    def __or__(self, other):
        '''

x.__or__(y) <==> x|y

'''                
        C = type(self)
        new = C.__new__(C)
        
        new._operator         = None
        new._regex            = False
        new._compound         = (self, other)
        new._bitwise_operator = operator_or
        new._attr             = ()

        new._NotImplemented_RHS_Data_op = True

        return new
    #--- End: def

    def __ior__(self, other):
        '''

x.__ior__(y) <==> x|=y

'''    
        return self | other            
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return '<CF %s: %s>' % (self.__class__.__name__, self)
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        attr = '.'.join(self._attr)

        if not self._compound:
            if self._regex:
                out = '%s(%s search(%r))' % (attr, self._operator, self._value)
            else:
                out = '%s(%s %r)' % (attr, self._operator, self._value) 
        else:
            bitwise_operator = repr(self._bitwise_operator)
            if '__and__' in bitwise_operator:
                bitwise_operator = '&'
            elif '__or__' in bitwise_operator:
                bitwise_operator = '|'

            out = '%s[%s %s %s]' % (attr, self._compound[0], bitwise_operator,
                                    self._compound[1])
        #--- End: if

        return out
    #--- End: def

    @property
    def attr(self):
        '''



**Examples**

>>> c = cf.Comparison('ge', 4)
>>> print c.attr
None
>>> c = cf.Comparison('le', 6, attr='year')
>>> c.attr
'year'
>>> c.addattr('foo')
>>> c.attr
'year'asdasdas

'''
        return self._attr
    #--- End: def

    @property
    def operator(self):
        '''

**Examples**

>>> c = cf.Comparison('ge', 4)
>>> c.operator
'ge'
>>> c |= cf.Comparison('le', 6)
>>> print c.operator
None

'''
#AttributeError: Compound Comparison doesn't have attribute 'operator'
#        if not self._compound:
        return self._operator

#        raise AttributeError(
#            "Compound %s doesn't have attribute 'operator'" %
#            self.__class__.__name__)
    #--- End: def

    @property
    def regex(self):
        '''


**Examples**

>>> c = cf.Comparison('eq', 'foo')
>>> c.regex
False
>>> c = cf.Comparison('eq', 'foo', regex=True)
>>> c.regex
True
>>> c |= cf.Comparison('eq', 'bar')
>>> print c.regex
False

'''
#AttributeError: Compound Comparison doesn't have attribute 'regex'
#        if not self._compound:
        return self._regex

#        raise AttributeError(
#            "Compound %s doesn't have attribute 'regex'" %
#            self.__class__.__name__)
    #--- End: def

    @property
    def value(self):
        '''

**Examples**

>>> c = cf.Comparison('ge', 4)
>>> c.value
4
>>> c |= cf.Comparison('le', 6)
>>> c.value
AttributeError: Compound Comparison doesn't have attribute 'value'

'''
        if not self._compound:
            return self._value

        raise AttributeError(
            "Compound %s doesn't have attribute 'value'" %
            self.__class__.__name__)
    #--- End: def

    def addattr(self, attr):
        '''Return a `cf.Comparison` object with a new left hand side operand
attribute to be used during evaluation.

If another attribute has previously been specified, then the new
attribute is considered to be an attribute of the existing attribute.

:Parameters:

    attr : str
        The attribute name.

:Returns:

    out : cf.Comparison
        The new comparison object.

**Examples**

>>> c = cf.eq(2001)
>>> c
<CF Comparison: (eq 2001)>
>>> c = c.addattr('year')
>>> c
<CF Comparison: year(eq 2001)>

>>> c = cf.lt(2)
>>> c = c.addattr('A')
>>> c = c.addattr('B')
>>> c
<CF Comparison: A.B(lt 2)>
>>> c = c.addattr('C')
>>> c
<CF Comparison: A.B.C(lt 2)>

        '''
        C = type(self)
        new = C.__new__(C)

        new.__dict__ = self.__dict__.copy()
        new._attr += (attr,)

        new._NotImplemented_RHS_Data_op = True

        return new
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``c.copy()`` is equivalent to ``copy.deepcopy(c)``.

:Returns:

    out :
        The deep copy.

**Examples**

>>> c.copy()

'''
        return self
    #--- End: def

    def dump(self, display=True):
        '''
        
Return a string containing a full description of the instance.

:Parameters:

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``c.dump()`` is equivalent to
        ``print c.dump(display=False)``.

:Returns:

    out : None or str
        A string containing the description.

**Examples**

'''      
        string = str(self)
       
        if display:
            print string
        else:
            return string
    #--- End: def

    def equals(self, other, traceback=False):
        '''
'''        
        if self._compound:
            if not other._compound:
                return False

            if self._bitwise_operator != other._bitwise_operator:
                return False
                
            if not self._compound[0].equals(other._compound[0]):
                if not self._compound[0].equals(other._compound[1]):
                    return False
                if not self._compound[1].equals(other._compound[0]):
                    return False
            elif not self._compound[1].equals(other._compound[1]):
                return False        
   
        elif other._compound:
            return False
                
        for attr in ('_NotImplemented_RHS_Data_op',
                     '_attr',
                     '_value',
                     '_operator',
                     '_regex'):
            if not cf_equals(getattr(self, attr, None),
                             getattr(other, attr, None),
                             traceback=traceback):
                return False
        #--- End: for

        return True
    #--- End: def

    def equivalent(self, other, traceback=False):
        '''
'''
        for attr, value in self.__dict__.iteritems():
            if not cf_equivalent(value, getattr(other, attr),
                                 traceback=traceback):
                return False
        #--- End: for

        return True
    #--- End: def

    def evaluate(self, x):
        '''

Evaluate the comparison operation for a given left hand side operand.

Note that for the comparison object ``c`` and any object, ``x``,
``x==c`` is equivalent to ``c.evaluate(x)`` and ``x!=c`` is equivalent
to ``c.evaluate(x)==False``.

:Parameters:

    x : 
        The object for the left hand side operand of the comparison.

:Returns:

    out : 
        The result of the comparison. The nature of the result is
        dependent on the object type of *x*.
    
**Examples**

>>> c = cf.Comparison('lt', 5.5)
>>> c.evaluate(6)
False

>>> c = cf.Comparison('wi', (1,2))
>>> array = numpy.arange(4)
>>> array
array([0, 1, 2, 3])
>>> c.evaluate(array)
array([False,  True,  True, False], dtype=bool)

'''
        return self._evaluate(x, ())
    #--- End: def

    def _evaluate(self, x, parent_attr):
        '''

Evaluate the comparison operation for a given object.

:Parameters:

    x :
        See `evaluate`.

    parent_attr : tuple
       

:Returns:

    out : 
        See `evaluate`.
    
**Examples**

See `evaluate`.

'''        
        compound = self._compound
        attr     = parent_attr + self._attr

        if compound:
            c = compound[0]._evaluate(x, attr)
            d = compound[1]._evaluate(x, attr)
            return self._bitwise_operator(c, d)
        #--- End: if

        # Still here?

        # ------------------------------------------------------------
        #
        # ------------------------------------------------------------
        for a in attr:
            x = getattr(x, a)
            
        operator = self._operator
        value    = self._value
        if operator == 'eq':
            if self._regex:
                if not isinstance(x, basestring):
                    raise ValueError("Can't regex on non string")

                return bool(re_search(value, x))
            else:
                return x == value
        #--- End: if           
        
        if operator == 'ne':
            if self._regex:
                if not isinstance(x, basestring):
                    raise ValueError("Can't regex on non string")

                return not re_search(value, x)
            else:
                return x != value
        #--- End: if
        
        if operator == 'lt':  
            _lt = getattr(x, '_comparison_lt', None)
            if _lt is not None:
                return _lt(value)

            return x < value
        #--- End: if
        
        if operator == 'le':
            _le = getattr(x, '_comparison_le', None)
            if _le is not None:
                return _le(value)

            return x <= value
        #--- End: if
        
        if operator == 'gt':            
            _gt = getattr(x, '_comparison_gt', None)
            if _gt is not None:
                return _gt(value)

            return x > value
        #--- End: if
        
        if operator == 'ge':            
            _ge = getattr(x, '_comparison_ge', None)
            if _ge is not None:
                return _ge(value)

            return x >= value
        #--- End: if

        if operator == 'wi':
            _wi = getattr(x, '_comparison_wi', None)
            if _wi is not None:
                return _wi(value[0], value[1])
            
            return (x >= value[0]) & (x <= value[1])
        #--- End: if

        if operator == 'wo':
            _wo = getattr(x, '_comparison_wo', None)
            if _wo is not None:
                return _wo(value[0], value[1])
            
            return (x < value[0]) | (x > value[1])
        #--- End: if

        if operator == 'has':
            _has = getattr(x, '_comparison_has', None)
            if _has is not None:
                return _has(value)
            else:
                return x == value
        #--- End: if           

        if operator == 'set':
            _set = getattr(x, '_comparison_set', None)
            if _set is not None:
                return _set(value, self._regex)

            i = iter(value)
            v = i.next()
            if self._regex:
                if not isinstance(x, basestring):
                    raise ValueError("Can't, as yet, regex on non string")
                
                if re_search(v, x):
                    return True
                
                for v in i:
                    if re_search(v, x):
                        return True
                    
                return False
            else:
                out = (x == v)
                for v in i:
                    out |= (x == v)

                return out
        #--- End: if    
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

#--- End: class


def lt(value, units=None, attr=None):
    '''Return a `cf.Comparison` object for a variable for being strictly less
than a value.

:Parameters:

    value : object
        The value which a variable is to be compared with.

    units : str or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    attr : str, optional
        Return a comparison object for a variable's *attr* attribute.

:Returns: 

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`, `cf.le`, `cf.set`, `cf.wi`, `cf.wo`

**Examples**

>>> c = cf.lt(5)
>>> c
<CF Comparison: x lt 5>
>>> c.evaluate(4)
True
>>> c.evaluate(5)
False

    '''
    return Comparison('lt', value, units=units, attr=attr)
#--- End: def
    
def le(value, units=None, attr=None):
    '''
    
Return a `cf.Comparison` object for a variable for being less than or equal
to a value.

:Parameters:

    value : object
        The value which a variable is to be compared with.

    units : str or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    attr : str, optional
        Return a comparison object for a variable's *attr* attribute.

:Returns: 

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`, `cf.lt`, `cf.set`, `cf.wi`, `cf.wo`

**Examples**

>>> c = cf.le(5)
>>> c
<CF Comparison: x le 5>
>>> c.evaluate(5)
True
>>> c.evaluate(6)
False

'''
    return Comparison('le', value, units=units, attr=attr)
#--- End: def
    
def gt(value, units=None, attr=None):
    '''
      
Return a `cf.Comparison` object for a variable for being strictly greater
than a value.

:Parameters:

    value : object
        The value which a variable is to be compared with.

    units : str or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    attr : str, optional
        Return a comparison object for a variable's *attr* attribute.

:Returns: 

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.eq`, `cf.ge`, `cf.ne`, `cf.le`, `cf.lt`, `cf.set`,
             `cf.wi`, `cf.wo`

**Examples**

>>> c = cf.gt(5)
>>> c
<CF Comparison: x gt 5>
>>> c.evaluate(6)
True
>>> c.evaluate(5)
False

'''
    return Comparison('gt', value, units=units, attr=attr)
#--- End: def
    
def ge(value, units=None, attr=None):
    '''
     
Return a `cf.Comparison` object for a variable for being greater than or
equal to a value.

:Parameters:

    value 
        The value which a variable is to be compared with.

    units : str or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    attr : str, optional
        Return a comparison object for a variable's *attr* attribute.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.eq`, `cf.gt`, `cf.ne`, `cf.le`, `cf.lt`, `cf.set`,
             `cf.wi`, `cf.wo`

**Examples**

>>> c = cf.ge(5)
>>> c
<CF Comparison: x ge 5>
>>> c.evaluate(5)
True
>>> c.evaluate(4)
False

'''
    return Comparison('ge', value, units=units, attr=attr)
#--- End: def

def eq(value, units=None, regex=False, attr=None):
    '''
    
Return a `cf.Comparison` object for a variable for being equal to a value.

:Parameters:

    value 
        The value which a variable is to be compared with.

    units : str or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    regex : str, optional
        If True then string values are to be treated as regular
        expressions, which are evaluated using the :py:obj:`re.search`
        function.

    attr : str, optional
        Return a comparison object for a variable's *attr* attribute.

:Returns:

    out : cf.Comparison
        The comparison object.
 
.. seealso:: `cf.ge`, `cf.gt`, `cf.ne`, `cf.le`, `cf.lt`, `cf.set`,
             `cf.wi`, `cf.wo`

**Examples**

>>> c = cf.eq(5)
>>> c
<CF Comparison: x eq 5>
>>> c.evaluate(5)
True
>>> c.evaluate(4)
False

'''
    return Comparison('eq', value, units=units, regex=regex, attr=attr)
#--- End: def
    
def ne(value, units=None, regex=False, attr=None):
    '''
    
Return a `cf.Comparison` object for a variable for being equal to a value.

:Parameters:

    value : object
        The value which a variable is to be compared with.

    units : str or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    regex : str, optional
        If True then string values are to be treated as regular
        expressions, which are evaluated using the :py:obj:`re.search`
        function.

    attr : str, optional
        Return a comparison object for a variable's *attr* attribute.

:Returns: 

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.eq`, `cf.ge`, `cf.gt`, `cf.le`, `cf.lt`, `cf.set`,
             `cf.wi`, `cf.wo`

**Examples**

>>> c = cf.ne(5)
>>> c
<CF Comparison: x ne 5>
>>> c.evaluate(4)
True
>>> c.evaluate(5)
False

'''
    return Comparison('ne', value, units=units, regex=regex, attr=attr)
#--- End: def
    
def wi(value0, value1, units=None, attr=None):
    '''
    
Return a `cf.Comparison` object for a variable being within a range.

``x == cf.wi(a, b)`` is equivalent to ``x == cf.ge(a) & cf.le(b)``.

``x == cf.wi(a, b, attr='foo')`` is equivalent to ``x.foo == cf.ge(a)
& cf.le(b)``.

:Parameters:

    value0 : scalar object
         The lower bound of the range which a variable is to be
         compared with.

    value1 : scalar object
         The upper bound of the range which a variable is to be
         compared with.

    units : str or cf.Units, optional
        If applicable, the units of *value0* and *value1*. By default,
        the same units as the variable being tested are assumed.

    attr : str, optional
        Return a comparison object for a variable's *attr* attribute.

:Returns: 

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`, `cf.le`, `cf.lt`,
             `cf.set`, `cf.wo`

**Examples**

>>> c = cf.wi(5, 7)
>>> c
<CF Comparison: wi (5, 7)>
>>> c.evaluate(6)
True
>>> c.evaluate(4)
False

'''
    return Comparison('wi', [value0, value1], units=units, attr=attr)
#--- End: def

def wo(value0, value1, units=None, attr=None):
    '''

Return a `cf.Comparison` object for a variable for being without a
range.

``x == cf.wo(a, b)`` is equivalent to ``x == cf.lt(a) | cf.gt(b)``.

:Parameters:

    value0 : object
         The lower bound of the range which a variable is to be
         compared with.

    value1 : object
         The upper bound of the range which a variable is to be
         compared with.

    units : str or cf.Units, optional
        If applicable, the units of *value0* and *value1*. By default,
        the same units as the variable being tested are assumed.

    attr : str, optional
        Return a comparison object for a variable's *attr* attribute.

:Returns: 

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`, `cf.le`, `cf.lt`,
             `cf.set`, `cf.wi`

**Examples**

>>> c = cf.wo(5)
>>> c
<CF Comparison: x wo (5, 7)>
>>> c.evaluate(4)
True
>>> c.evaluate(6)
False

'''
    return Comparison('wo', [value0, value1], units=units, attr=attr)
#--- End: def

def set(values, units=None, regex=False, attr=None):
    '''
    
Return a `cf.Comparison` object for a variable for being equal to any
member of a collection.

:Parameters:

    values : sequence
    
    units : str or cf.Units, optional
        The units of each element of *values*. By default, the same
        units as the variable being tested are assumed, if applicable.

    regex : str, optional
        If True then each element of *values* is assumed to be a
        string containing a regular expression, which is evaluated
        using the :py:obj:`re.search` function.

    attr : str, optional
        Return a comparison object for a variable's *attr* attribute.

:Returns: 

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`, `cf.le`, `cf.lt`,
             `cf.wi`, `cf.wo`

**Examples**

>>> c = cf.set([3, 5])
>>> c
<CF Comparison: set [3, 5]>
>>> c == 4
False
>>> c == 5
True
>>> print c == numpy.array([2, 3, 4, 5])
[False  True False  True]

'''
    return Comparison('set', values, units=units, regex=regex, attr=attr)
#--- End: def

def year(value):
    '''Return a `cf.Comparison` object for date-time years.

In this context, any object which has a `!year` attribute is
considered to be a date-time variable.

If *value* is a `cf.Comparison` object then ``cf.year(value)`` is
equivalent to ``value.addattr('year')``. Otherwise ``cf.year(value)``
is equivalent to ``cf.eq(value, attr='year')``.

:Parameters:

    value :   
       Either the value that the year is to be compared with, or a
       `cf.Comparison` object for testing the year.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtle`, `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.year(2002)
True
>>> d == cf.year(cf.le(2003))
True
>>> d == cf.year(2001)
False
>>> d == cf.year(cf.wi(2003, 2006))
False

    '''
    if isinstance(value, Comparison):
        return value.addattr('year')
    else:
        return Comparison('eq', value, attr='year')
#--- End: def

def month(value):
    '''Return a `cf.Comparison` object for date-time months.

In this context, any object which has a `!month` attribute is
considered to be a date-time variable.

If *value* is a `cf.Comparison` object then ``cf.month(value)`` is
equivalent to ``value.addattr('month')``. Otherwise
``cf.month(value)`` is equivalent to ``cf.eq(value, attr='month')``.

:Parameters:

    value :   
       Either the value that the month is to be compared with, or a
       `cf.Comparison` object for testing the month.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.day`, `cf.hour`, `cf.minute`, `cf.second`,
             `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.month(6)
True
>>> d == cf.month(cf.le(7))
True
>>> d == cf.month(7)
False
>>> d == cf.month(cf.wi(1, 6))
True

    '''
    if isinstance(value, Comparison):
        return value.addattr('month')
    else:
        return Comparison('eq', value, attr='month')
#--- End: def

def day(value):
    '''Return a `cf.Comparison` object for date-time days.

In this context, any object which has a `!day` attribute is considered
to be a date-time variable.

If *value* is a `cf.Comparison` object then ``cf.day(value)`` is
equivalent to ``value.addattr('day')``. Otherwise ``cf.day(value)`` is
equivalent to ``cf.eq(value, attr='day')``.

:Parameters:

    value :   
       Either the value that the day is to be compared with, or a
       `cf.Comparison` object for testing the day.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtle`, `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.day(16)
True
>>> d == cf.day(cf.le(19))
True
>>> d == cf.day(7)
False
>>> d == cf.day(cf.wi(1, 21))
True

    '''
    if isinstance(value, Comparison):
        return value.addattr('day')
    else:
        return Comparison('eq', value, attr='day')
#--- End: def

def hour(value):
    '''Return a `cf.Comparison` object for date-time hours.

In this context, any object which has a `!hour` attribute is
considered to be a date-time variable.

If *value* is a `cf.Comparison` object then ``cf.hour(value)`` is
equivalent to ``value.addattr('hour')``. Otherwise ``cf.hour(value)``
is equivalent to ``cf.eq(value, attr='hour')``.

:Parameters:

    value :   
       Either the value that the hour is to be compared with, or a
       `cf.Comparison` object for testing the hour.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtle`, `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16, 18)
>>> d == cf.hour(18)
True
>>> d == cf.hour(cf.le(19))
True
>>> d == cf.hour(7)
False
>>> d == cf.hour(cf.wi(6, 23))
True

    '''
    if isinstance(value, Comparison):
        return value.addattr('hour')
    else:
        return Comparison('eq', value, attr='hour')
#--- End: def

def minute(value):
    '''

Return a `cf.Comparison` object for date-time minutes.

In this context, any object which has a `!minute` attribute is
considered to be a date-time variable.

If *value* is a `cf.Comparison` object then ``cf.minute(value)`` is
equivalent to ``value.addattr('minute')``. Otherwise
``cf.minute(value)`` is equivalent to ``cf.eq(value, attr='minute')``.

:Parameters:

    value :   
       Either the value that the minute is to be compared with, or a
       `cf.Comparison` object for testing the minute.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.second`,
             `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16, 18, 30, 0)
>>> d == cf.minute(30)
True
>>> d == cf.minute(cf.le(45))
True
>>> d == cf.minute(7)
False
>>> d == cf.minute(cf.wi(15, 45))
True

'''
    if isinstance(value, Comparison):
        return value.addattr('minute')
    else:
        return Comparison('eq', value, attr='minute')
#--- End: def

def second(value):
    '''

Return a `cf.Comparison` object for date-time seconds.
    
In this context, any object which has a `!second` attribute is
considered to be a date-time variable.

If *value* is a `cf.Comparison` object then ``cf.second(value)`` is
equivalent to ``value.addattr('second')``. Otherwise
``cf.second(value)`` is equivalent to ``cf.eq(value, attr='second')``.

:Parameters:

    value :   
       Either the value that the second is to be compared with, or a
       `cf.Comparison` object for testing the second.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16, 18, 30, 0)
>>> d == cf.second(0)
True
>>> d == cf.second(cf.le(30))
True
>>> d == cf.second(30)
False
>>> d == cf.second(cf.wi(0, 30))
True

'''
    if isinstance(value, Comparison):
        return value.addattr('second')
    else:
        return Comparison('eq', value, attr='second')
#--- End: def

def cellsize(value, units=None):
    '''

Return a `cf.Comparison` object for the cell size of a coordinate object.

In this context, a coordinate is any object which has a `!cellsize`
attribute.

If *value* is a `cf.Comparison` object then ``cf.cellsize(value)`` is
equivalent to ``value.addattr('cellsize')``. Otherwise
``cf.cellsize(value)`` is equivalent to ``cf.eq(value,
attr='cellsize')``.

:Parameters:

    value :   
       Either the value that the cell size is to be compared with, or a
       `cf.Comparison` object for testing the cell size.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.celllt`, `cf.cellle`,
             `cf.cellwi`, `cf.cellwo`, `cf.eq`

**Examples**

>>> cf.cellsize(cf.lt(5, 'km'))
<CF Comparison: cellsize(lt <CF Data: 5 km>)>
>>> cf.cellsize(5) 
<CF Comparison: cellsize(eq 5)>
>>> cf.cellsize(cf.Data(5, 'km'))
<CF Comparison: cellsize(eq <CF Data: 5 km>)>
>>> cf.cellsize(cf.Data(5, 'km'))  
<CF Comparison: cellsize(eq <CF Data: 5 km>)>
>>> cf.cellsize(5, units='km')   
<CF Comparison: cellsize(eq <CF Data: 5 km>)>

    '''
    if isinstance(value, Comparison):
        return value.addattr('cellsize')
    else:
        return Comparison('eq', value, units=units, attr='cellsize')
#--- End: def

def dtge(*args, **kwargs):
    '''

Return a `cf.Comparison` object for a variable being not earlier
than a date-time.

``cf.dtge(*args, **kwargs)`` is equivalent to ``cf.ge(cf.dt(*args,
**kwargs))``.

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtge(1990, 1, 1)
True
>>> d == cf.dtge(2002, 6, 16)
True
>>> d == cf.dtge('2100-1-1')
False
>>> d == cf.dtge('2001-1-1') & cf.dtle(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Comparison('ge', dt(*args, **kwargs))
#--- End: def

def dtgt(*args, **kwargs):
    '''

Return a `cf.Comparison` object for a variable being later than a
date-time.

``cf.dtgt(*args, **kwargs)`` is equivalent to ``cf.gt(cf.dt(*args,
**kwargs))``.

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtgt(1990, 1, 1)
True
>>> d == cf.dtgt(2002, 6, 16)
False
>>> d == cf.dtgt('2100-1-1')
False
>>> d == cf.dtgt('2001-1-1') & cf.dtle(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Comparison('gt', dt(*args, **kwargs))
#--- End: def

def dtle(*args, **kwargs):
    '''

Return a `cf.Comparison` object for a variable being not later than a
date-time.

``cf.dtle(*args, **kwargs)`` is equivalent to ``cf.le(cf.dt(*args,
**kwargs))``.

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtle(1990, 1, 1)
True
>>> d == cf.dtle(2002, 6, 16)
True
>>> d == cf.dtle('2100-1-1')
False
>>> d == cf.dtle('2001-1-1') & cf.dtle(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Comparison('le', dt(*args, **kwargs))
#--- End: def

def dtlt(*args, **kwargs):
    '''

Return a `cf.Comparison` object for a variable being earlier than a
date-time.

``cf.dtlt(*args, **kwargs)`` is equivalent to ``cf.lt(cf.dt(*args,
**kwargs))``.

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtle`

**Examples**

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtlt(1990, 1, 1)
True
>>> d == cf.dtlt(2002, 6, 16)
True
>>> d == cf.dtlt('2100-1-1')
False
>>> d == cf.dtlt('2001-1-1') & cf.dtlt(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Comparison('lt', dt(*args, **kwargs))
#--- End: def

def dteq(*args, **kwargs):
    '''

Return a `cf.Comparison` object for a variable being equal to a
date-time.

``cf.dteq(*args, **kwargs)`` is equivalent to ``cf.eq(cf.dt(*args,
**kwargs))``.

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dtge`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dteq(1990, 1, 1)
True
>>> d == cf.dteq(2002, 6, 16)
True
>>> d == cf.dteq('2100-1-1')
False
>>> d == cf.dteq('2001-1-1') & cf.dteq(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Comparison('eq', dt(*args, **kwargs))
#--- End: def

def dtne(*args, **kwargs):
    '''

Return a `cf.Comparison` object for a variable being not equal to a
date-time.

``cf.dtne(*args, **kwargs)`` is equivalent to ``cf.ne(cf.dt(*args,
**kwargs))``.

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out : cf.Comparison
        The comparison object.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtle`,
             `cf.dtlt`

**Examples**

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtne(1990, 1, 1)
True
>>> d == cf.dtne(2002, 6, 16)
True
>>> d == cf.dtne('2100-1-1')
False
>>> d == cf.dtne('2001-1-1') & cf.dtne(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Comparison('ne', dt(*args, **kwargs))
#--- End: def

def cellwi(value0, value1, units=None):
    '''Return a `cf.Comparison` object for coordinate cell bounds being within
a range.

In this context, a coordinate is any object which has `!lower_bounds`
and `!upper_bounds` attributes.

``cf.cellwi(value0, value1)`` is equivalent to ``cf.ge(value0,
attr='lower_bounds') & cf.le(value1, attr='upper_bounds')``.

:Parameters:

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.cellle`, `cf.celllt`,
             `cf.cellsize`, `cf.cellwo`, `cf.wi`

**Examples**

    ''' 
    return (Comparison('ge', value0, units=units, attr='lower_bounds') &
            Comparison('le', value1, units=units, attr='upper_bounds'))
#--- End: def

def cellwo(value0, value1, units=None):
    '''Return a `cf.Comparison` object for coordinate cell bounds being
outside a range.

In this context, a coordinate is any object which has `!lower_bounds`
and `!upper_bounds` attributes.

``cf.cellwo(value0, value1)`` is equivalent to ``cf.lt(value0,
attr='lower_bounds') & cf.gt(value1, attr='upper_bounds')``.

:Parameters:

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.cellle`, `cf.celllt`,
             `cf.cellsize`, `cf.cellwi`, `cf.wo`

**Examples**

    ''' 
    return (Comparison('lt', value0, units=units, attr='lower_bounds') &
            Comparison('gt', value1, units=units, attr='upper_bounds'))
#--- End: def

def cellgt(value, units=None):
    '''Return a `cf.Comparison` object for coordinate cell bounds being
strictly greater than a value.

In this context, a coordinate is any object which has a
`!lower_bounds` attribute.

``cf.cellgt(value)`` is equivalent to ``cf.gt(value,
attr='lower_bounds')``.

:Parameters:

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellle`, `cf.celllt`, `cf.cellsize`,
             `cf.cellwi`,`cf.cellwo`, `cf.gt`

**Examples**

    ''' 
    return Comparison('gt', value, units=units, attr='lower_bounds')
#--- End: def

def cellge(value, units=None):
    '''Return a `cf.Comparison` object for coordinate cell bounds being
greater than or equal to a value.

In this context, a coordinate is any object which has a
`!lower_bounds` attribute.

``cf.cellge(value)`` is equivalent to ``cf.ge(value,
attr='lower_bounds')``.

:Parameters:

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.cellgt`, `cf.cellle`, `cf.celllt`, `cf.cellsize`,
             `cf.cellwi`,`cf.cellwo`, `cf.gt`

**Examples**

    ''' 
    return Comparison('ge', value, units=units, attr='lower_bounds')
#--- End: def

def celllt(value, units=None):
    '''Return a `cf.Comparison` object for coordinate cell bounds being
strictly less than a value.

In this context, a coordinate is any object which has a
`!upper_bounds` attribute.

``cf.celllt(value)`` is equivalent to ``cf.lt(value,
attr='upper_bounds')``.

:Parameters:

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.cellle`, `cf.cellsize`,
             `cf.cellwi`,`cf.cellwo`, `cf.le`

**Examples**

    ''' 
    return Comparison('lt', value, units=units, attr='upper_bounds')
#--- End: def

def cellle(value, units=None):
    '''Return a `cf.Comparison` object for coordinate cell bounds being
less than or equal to a value.

In this context, a coordinate is any object which has a
`!upper_bounds` attribute.

``cf.cellle(value)`` is equivalent to ``cf.le(value,
attr='upper_bounds')``.

:Parameters:

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.celllt`, `cf.cellsize`,
             `cf.cellwi`,`cf.cellwo`, `cf.lt`

**Examples**

    ''' 
    return Comparison('le', value, units=units, attr='upper_bounds')
#--- End: def

def jja():
    '''Return a `cf.Comparison` object for season June, July, August.

``cf.jja()`` is equivalent to ``cf.month(cf.wi(6, 8))``.

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.djf`, `cf.mam`, `cf.son`, `cf.ssns`, `cf.month`,
             `cf.wi`

**Examples**

>>> f
<CF Field: air_temperature(time(365), latitude(64), longitude(128)) K>
>>> f.subspace(time=cf.jja())
<CF Field: air_temperature(time(92), latitude(64), longitude(128)) K>

    '''
    return Comparison('wi', (6, 8), attr='month')
#--- End: def

def son():
    '''Return a `cf.Comparison` object for season September, October,
November.

``cf.son()`` is equivalent to ``cf.month(cf.wi(9, 11))``.

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.djf`, `cf.mam`, `cf.jja`, `cf.ssns`, `cf.month`,
             `cf.wi`

**Examples**

>>> f
<CF Field: air_temperature(time(365), latitude(64), longitude(128)) K>
>>> f.subspace(time=cf.son())
<CF Field: air_temperature(time(91), latitude(64), longitude(128)) K>

    '''
    return Comparison('wi', (9, 11), attr='month')
#--- End: def

def djf():
    '''Return a `cf.Comparison` object for season December, January, February.

``cf.djf()`` is equivalent to ``cf.month(cf.ge(12) | cf.le(2))``.

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.mam`, `cf.jja`, `cf.son`, `cf.ssns`, `cf.month`,
             `cf.ge`, `cf.le`

**Examples**

>>> f
<CF Field: air_temperature(time(365), latitude(64), longitude(128)) K>
>>> f.subspace(time=cf.djf())
<CF Field: air_temperature(time(90), latitude(64), longitude(128)) K>

    '''
    c =  Comparison('ge', 12) | Comparison('le', 2)
    return c.addattr('month')
#--- End: def

def mam():
    '''Return a `cf.Comparison` object for season March, April, May.

``cf.mam()`` is equivalent to ``cf.month(cf.wi(3, 5))``.

:Returns:

    out : cf.Comparison
        The comparison object.

.. versionadded:: 1.0

.. seealso:: `cf.djf`, `cf.jja`, `cf.son`, `cf.ssns`, `cf.month`,
             `cf.wi`

**Examples**

>>> f
<CF Field: air_temperature(time(365), latitude(64), longitude(128)) K>
>>> f.subspace(time=cf.mam())
<CF Field: air_temperature(time(92), latitude(64), longitude(128)) K>

    '''
    return Comparison('wi', (3, 5), attr='month')

#--- End: def

def ssns(n=4, start=12):
    '''Return a list `cf.Comparison` objects for all seasons in a year.

:Parameters:

    n : int, optional
        The number of seasons in the year. By default there are four
        seasons.

    start : int, optional
        The start month of the first season of the year. By default
        this is 12 (December).

:Returns:

    out : list of cf.Comparison
        The comparison objects.

.. versionadded:: 1.0

.. seealso:: `cf.mam`, `cf.jja`, `cf.son`, `cf.djf`

**Examples**

>>> cf.ssns()
[<CF Comparison: month[(ge 12) | (le 2)]>,
 <CF Comparison: month(wi (3, 5))>,
 <CF Comparison: month(wi (6, 8))>,
 <CF Comparison: month(wi (9, 11))>]

>>> cf.ssns(4, 1)
[<CF Comparison: month(wi (1, 3))>,
 <CF Comparison: month(wi (4, 6))>,
 <CF Comparison: month(wi (7, 9))>,
 <CF Comparison: month(wi (10, 12))>]

>>> cf.ssns(3, 6)
[<CF Comparison: month(wi (6, 9))>,
 <CF Comparison: month[(ge 10) | (le 1)]>,
 <CF Comparison: month(wi (2, 5))>]

>>> cf.ssns(3)
[<CF Comparison: month[(ge 12) | (le 3)]>,
 <CF Comparison: month(wi (4, 7))>,
 <CF Comparison: month(wi (8, 11))>]

>>> cf.ssns(3, 6)
[<CF Comparison: month(wi (6, 9))>,
 <CF Comparison: month[(ge 10) | (le 1)]>,
 <CF Comparison: month(wi (2, 5))>]

>>> cf.ssns(12)
[<CF Comparison: month(eq 12)>,
 <CF Comparison: month(eq 1)>,
 <CF Comparison: month(eq 2)>,
 <CF Comparison: month(eq 3)>,
 <CF Comparison: month(eq 4)>,
 <CF Comparison: month(eq 5)>,
 <CF Comparison: month(eq 6)>,
 <CF Comparison: month(eq 7)>,
 <CF Comparison: month(eq 8)>,
 <CF Comparison: month(eq 9)>,
 <CF Comparison: month(eq 10)>,
 <CF Comparison: month(eq 11)>]

>>> cf.ssns(1, 4)
[<CF Comparison: month[(ge 4) | (le 3)]>]

    '''
    if 12 % n:
        raise ValueError(
            "Number of seasons must divide into 12. Got %s" % n)

    if not 1 <= start <= 12 or int(start) != start:
        raise ValueError(
            "Start month must be integer between 1 and 12. Got %s" % start)

    out = []

    inc = int(12 / n)

    start = int(start)

    m0 = start
    for i in range(int(n)):
        m1 = ((m0 + inc) % 12) - 1
        if not m1:
            m1 = 12
        elif m1 == -1:
            m1 = 11

        if m0 < m1: 
            c = Comparison('wi', (m0, m1))
        elif m0 > m1: 
            c = Comparison('ge', m0) | Comparison('le', m1)
        else:
            c = Comparison('eq', m0)

        out.append(c.addattr('month'))
    
        m0 = m1 + 1
        if m0 > 12:
            m0 = 1
    #--- End: for

    return out
#--- End: def

# --------------------------------------------------------------------
# Vectorized 
# --------------------------------------------------------------------
def _search(regex, x):
    return bool(re_search(regex, x))
_array_search = numpy_vectorize(_search, otypes=[bool])
