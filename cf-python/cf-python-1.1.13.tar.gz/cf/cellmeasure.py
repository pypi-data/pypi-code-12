from .variable import Variable

# ====================================================================
#
# CellMeasure object
#
# ====================================================================

class CellMeasure(Variable):
    '''
    
A CF cell measure construct containing information that is needed
about the size, shape or location of the field's cells.

It is a variable which contains a data array and metadata comprising
properties to describe the physical nature of the data.


**Attributes**

==========  =======  =================================================
Attribute   Type     Description
==========  =======  =================================================
`!measure`  ``str``  The spatial measure being represented. Either
                     ``'area'`` or ``'volume'`` are allowed by the CF
                     conventions.
==========  =======  =================================================

'''   
    @property
    def ismeasure(self): 
        '''

Always True.

.. seealso:: `isauxiliary`, `isdimension`

:Examples: 

>>> c.ismeasure
True

'''
        return True
    #--- End: def

    def dump(self, display=True, domain=None, key=None, _level=0):
        '''

Return a string containing a full description of the cell measure.

:Parameters:

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``c.dump()`` is equivalent to
        ``print c.dump(display=False)``.

:Returns:

    out : None or str
        A string containing the description.

:Examples:

'''
        indent1 = '    ' * _level
        indent2 = '    ' * (_level+1)

        if hasattr(self, 'measure'):
            string = ['%sCell measure: %s' % (indent1, self.measure)]
        elif hasattr(self.Units, 'units'):
            string = ['%sCell measure: %s' % (indent1, self.units)]
        else:
            string = ['%sCell measure: %s' % (indent1, self.name(default=''))]

        if self._hasData:
            if domain:
                x = ['%s(%d)' % (domain.axis_name(axis), domain.axis_size(axis))
                     for axis in domain.item_axes(key)]
                string.append('%sData(%s) = %s' % (indent2, ', '.join(x), str(self.Data)))
            else:
                x = [str(s) for s in self.shape]
                string.append('%sData(%s) = %s' % (indent2, ', '.join(x), str(self.Data)))
        #--- End: if

        if self._simple_properties():
            string.append(self._dump_simple_properties(_level=_level+1))
          
        string = '\n'.join(string)
       
        if display:
            print string
        else:
            return string
    #--- End: def

    def identity(self, default=None):
        '''

Return the cell measure's identity.

The identity is first found of:

* The `!measure` attribute.

* The `standard_name` CF property.

* The `!id` attribute.

* The value of the *default* parameter.

:Parameters:

    default : optional
        If none of `measure`, `standard_name` and `!id` exist then
        return *default*. By default, *default* is None.

:Returns:

    out :
        The identity.

:Examples:

'''
        return super(CellMeasure, self).identity(default)
    #--- End: def

    def name(self, default=None, identity=False, ncvar=False):
        '''Return a name for the cell measure.

By default the name is the first found of the following:

  1. The `!measure` attribute.
  
  2. The `standard_name` CF property.
  
  3. The `!id` attribute.

  4. The `long_name` CF property, preceeded by the string
     ``'long_name:'``.

  5. The `!ncvar` attribute, preceeded by the string ``'ncvar:'``.

  6. The value of the *default* parameter.

Note that ``c.name(identity=True)`` is equivalent to ``c.identity()``.

.. seealso:: `identity`

:Parameters:

    default : *optional*
        If no name can be found then return the value of the *default*
        parameter. By default the default is None.

    identity : bool, optional
        If True then 3. and 4. are not considered as possible names.

    ncvar : bool, optional
        If True then 1., 2., 3. and 4. are not considered as possible
        names.

:Returns:

    out : str
        A  name for the cell measure.

:Examples:

>>> f.standard_name = 'air_temperature'
>>> f.long_name = 'temperature of the air'
>>> f.ncvar = 'tas'
>>> f.name()
'air_temperature'
>>> del f.standard_name
>>> f.name()
'long_name:temperature of the air'
>>> del f.long_name
>>> f.name()
'ncvar:tas'
>>> del f.ncvar
>>> f.name()
None
>>> f.name('no_name')
'no_name'
>>> f.standard_name = 'air_temperature'
>>> f.name('no_name')
'air_temperature'

        '''      
        if ncvar:
            if identity:
                raise ValueError(
"Can't find name: ncvar and identity parameters can't both be True")

            n = getattr(self, 'ncvar', None)
            if n is not None:
                return 'ncvar%%%s' % n
            
            return default
        #--- End: if

        n = getattr(self, 'measure', None)
        if n is not None:
            return n

        return super(CellMeasure, self).name(default,
                                             identity=identity, ncvar=False)
    #--- End: def

#--- End: class
