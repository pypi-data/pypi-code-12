import os

from csv import reader as csv_reader
from re  import match as re_match

from .          import __file__
from .utils     import Dict
from .functions import RTOL, ATOL, equals, allclose
from .functions import inspect as cf_inspect
from .query     import Query
from .units     import Units

from .data.data import Data

# --------------------------------------------------------------------
# Map coordinate conversion names to their CF-netCDF types
# --------------------------------------------------------------------
_type = {}
_file = os.path.join(os.path.dirname(__file__),
                     'etc/coordinate_reference/type.txt')
for x in csv_reader(open(_file, 'r'), delimiter=' ', skipinitialspace=True):
    if not x or x[0] == '#':
        continue
    _type[x[0]] = x[1]

# --------------------------------------------------------------------
# Map coordinate conversion names to their
# --------------------------------------------------------------------
_coordinates = {}
_file = os.path.join(os.path.dirname(__file__),
                     'etc/coordinate_reference/coordinates.txt')
for x in csv_reader(open(_file, 'r'), delimiter=' ', skipinitialspace=True):
    if not x or x[0] == '#':
        continue
    _coordinates[x[0]] = set(x[1:])

# --------------------------------------------------------------------
# Map coordinate conversion terms to their terms default values
# --------------------------------------------------------------------
_default_values = {}
_file = os.path.join(os.path.dirname(__file__),
                     'etc/coordinate_reference/default_values.txt')
for x in csv_reader(open(_file, 'r'), delimiter=' ', skipinitialspace=True):
    if not x or x[0] == '#':
        continue
    _default_values[x[0]] = float(x[1])

# --------------------------------------------------------------------
# Map coordinate conversion terms to their canonical units
# --------------------------------------------------------------------
_canonical_units = {}
_file = os.path.join(os.path.dirname(__file__),
                     'etc/coordinate_reference/canonical_units.txt')
for x in csv_reader(open(_file, 'r'), delimiter=' ', skipinitialspace=True):
    if not x or x[0] == '#':
        continue
    try:
        _canonical_units[x[0]] = Units(x[1])
    except:
        pass

# --------------------------------------------------------------------
# Map coordinate reference names to their terms which may take
# non-constant values (i.e. pointers to coordinate objects or
# non-scalar field objects).
# --------------------------------------------------------------------
_non_constant_terms = {}
_file = os.path.join(os.path.dirname(__file__),
                     'etc/coordinate_reference/non_constant_terms.txt')
for x in csv_reader(open(_file, 'r'), delimiter=' ', skipinitialspace=True):
    if not x or x[0] == '#' or len(x) == 1:
        continue
    _non_constant_terms[x[0]] = set(x[1:])


# ====================================================================
#
# CoordinateReference object
#
# ====================================================================

_units = {}

class CoordinateReference(Dict):
    '''A CF coordinate reference construct.

A coordinate reference construct relates the field's coordinate values
to locations in a planetary reference frame.

The coordinate reference object is associated with a coordinate system
and contains links to the dimension or auxiliary coordinate constructs
to which it applies; and any additional terms, such as parameter
values and field objects which define a datum and coordinate
conversion, i.e. a formula for converting coordinate values taken from
the dimension or auxiliary coordinate objects to a different
coordinate system.

**Accessing terms**

The coordinate reference object behaves like a dictionary when it
comes to accessing its terms and their values: For example:

>>> c = cf.CoordinateReference('azimuthal_equidistant', 
...                             longitude_of_projection_origin=80.5,
...                             latitude_of_projection_origin=5, 
...                             false_easting=cf.Data(-200, 'km'),
...                             false_northing=cf.Data(-100, 'km'))
>>> c.keys()
['false_easting',
 'latitude_of_projection_origin',
 'false_northing',
 'longitude_of_projection_origin']
>>> c.items()
[('false_easting', <CF Data: -200 km>),
 ('latitude_of_projection_origin', 5),
 ('false_northing', <CF Data: -100 km>),
 ('longitude_of_projection_origin', 80.5)]
>>> c['latitude_of_projection_origin']
5
>>> c['latitude_of_projection_origin'] = -75.25
>>> c['latitude_of_projection_origin']
-75.25


**Attributes**

==============  ======================================================

Attribute       Description
==============  ======================================================
`!name`         The identity of the coordinate reference.

`!type`         The CF type of the coordinate reference. 

`!coords`       The identities of the dimension and auxiliary
                coordinate objects of the which apply to this
                coordinate reference. 

`!coord_terms`  The terms of the coordinate conversion which refer to
                dimension or auxiliary coordinate objects.
==============  ======================================================

    '''

    def __init__(self, name=None, crtype=None, coords=None,
                 coord_terms=None, **kwargs):
        '''**Initialization**

:Parameters:

    name : str, optional
        A name which describes the nature of the coordinate
        conversion. This is usually a CF grid_mapping name or the
        standard name of a CF dimensionless vertical coordinate, but
        is not restricted to these.

          Example: To create a polar stereographic coordinate
          reference: ``name='polar_stereographic'``. To create
          coordinate reference for an ocean sigma over z coordinate:
          ``name='ocean_sigma_z_coordinate'``. To create new type of
          coordinate reference: ``name='my_new_type'``.

    crtype : str, optional
        The CF type of the coordinate reference. This is either
        ``'grid_mapping'`` or ``'formula_terms'``. By default the type
        is inferred from the *name*, if possible. For example:

        >>> c = cf.CoordinateReference('transverse_mercator')
        >>> c.type
        'grid_mapping'

        >>> c = cf.CoordinateReference('my_new_type', crtype='formula_terms')
        >>> c.type
        'formula_terms'

        >>> c = cf.CoordinateReference('my_new_type')
        >>> print c.type
        None

        >>> c = cf.CoordinateReference('my_new_type', crtype='grid_mapping')
        >>> print c.type
        'grid_mapping'

    coords : sequence of str, optional
        Identify the dimension and auxiliary coordinate objects which
        apply to this coordinate reference. By default the standard
        names of those expected by the CF conventions are used. For
        example:

        >>> c = cf.CoordinateReference('transverse_mercator')
        >>> c.coords
        {'latitude', 'longitude', 'projection_x_coordinate', 'projection_y_coordinate'}

        >>> c = cf.CoordinateReference('transverse_mercator', coords=['ncvar:lat'])
        >>> c.coords
        {'ncvar:lat'}

    coord_terms : sequence of str, optional        
        The terms of the coordinate conversion which refer to
        dimension or auxiliary coordinate objects. For example:

        >>> c = cf.CoordinateReference('lambert_conformal_conic')
        >>> c.coord_terms
        set()

        >>> c = cf.CoordinateReference('atmosphere_hybrid_height_coordinate',
        ...                            coord_terms=['a', 'b'])
        >>> c.coord_terms
        {'a', 'b'}


    kwargs : *optional*
        The terms of the coordinate conversion and their values. A
        term's values may be one of the following:

          * A number or size one numeric array.

          * A string containing a coordinate object's identity.

          * A Field.
 
          * `None`, indicating that the term exists but is unset.

        For example:

        >>> c = cf.CoordinateReference('orthographic', 
        ...                            grid_north_pole_latitude=70,
        ...                            grid_north_pole_longitude=cf.Data(120, 'degreesE'))
        >>> c['grid_north_pole_longitude']
        <CF Data: 120 degreesE>

        >>> orog_field
        <CF Field: surface_altitude(latitude(73), longitude(96)) m>
        >>> c = cf.CoordinateReference('atmosphere_hybrid_height_coordinate',
        ...                            a='long_name:ak',
        ...                            b='long_name:bk',
        ...                            orog=orog_field)

'''
        super(CoordinateReference, self).__init__(**kwargs)

        

        t = _type.get(name, None)
        if t is not None:
            if crtype is not None and crtype != t:
                raise ValueError("345|")            
            crtype = t
        #--- End: if

#        standard_coords = {}
#        for coord in _coordinates.get(name, ()):
#            standard_coords[coord] = coord

        if coords is None:
            coords = set(_coordinates.get(name, ()))          
#            coords = set(standard_coords)
        else:
            coords = set(coords)

        if coord_terms:
            coords.update([kwargs[term]
                           for term in coord_terms if term in kwargs])
            coord_terms = set(coord_terms)
        else:
            coord_terms = set()

        self.type        = crtype
        self.name        = name 
        self.coords      = coords
        self.coord_terms = coord_terms

#        self._standard_coords = standard_coords 
    #--- End: def

    def __delitem__(self, item):
        '''

x.__delitem__(key) <==> del x[key]

'''
        super(CoordinateReference, self).__delitem__(item)
        self.coord_terms.discard(item)
    #--- End: def

    def __eq__(self, other):
        '''

The rich comparison operator ``==``

x.__eq__(y) <==> x==y

'''
        return self.equals(other)
    #--- End: def

    def __ne__(self, other):
        '''

The rich comparison operator ``!=``

x.__ne__(y) <==> x!=y

'''
        return not self.equals(other)
    #--- End: def

    def __hash__(self):
        '''

x.__hash__() <==> hash(x)

'''
        if self.type == 'formula_terms':
            raise ValueError("Can't hash a formula_terms %s" %
                             self.__class__.__name__)

        h = sorted(self.items())
        h.append(self.identity())

        return hash(tuple(h))
    #--- End: def

    def __repr__(self):
        '''

The built-in function `repr`

x.__repr__() <==> repr(x)

''' 
        try:
            return '<CF %s: %s>' % (self.__class__.__name__, self.identity(''))
        except AttributeError:
            return '<CF %s: >' % self.__class__.__name__
    #--- End: def

#    def __setitem__(self, item, value):
#        '''
#
#x.__setitem__(key, value) <==> x[key]=value#
#
#'''
#        if item == 'crs_wkt':
#            # Bodge for crs_wkt
#            super(CoordinateReference, self).__setitem__(item, value)
#            return
#
#        if item in self:
#            old = self.pop(item)
#            self.coord_terms.discard(item)
#            if isinstance(old, basestring) and old not in self.values():
#                self.coords.discard(old)
#        #-- End: if
#
#        super(CoordinateReference, self).__setitem__(item, value)
#
#        # Add string values to the coordinates sets
#        if isinstance(value, basestring):
#            self.coords.add(value)
#            self.coord_terms.add(item)
#    #--- End: def

    def __str__(self):
        '''

The built-in function `str`

x.__str__() <==> str(x)

'''    
        return 'Coord reference : %r' % self
    #--- End: def

    def _parse_match(self, match):
        '''
Called by def match

'''        
        if not match:
            return ()

        if isinstance(match, (basestring, dict, Query)):
            match = (match,)

        matches = []
        for m in match:            
            if isinstance(m, dict):
                # Dictionary
                matches.append(m)
            else:
                matches.append({None: m})
        #--- End: for

        return matches
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def hasbounds(self):
        '''

False

:Examples:

>>> c.hasbounds
False

'''
        return False
    #--- End: def

    @classmethod
    def canonical_units(cls, term):
        '''Return the canonical units for a standard CF coordinate conversion
term.

:Parameters:

    term : str
        The name of the term.

:Returns:

    out : cf.Units or None
        The canonical units, or `None` if there are not any.

:Examples:

>>> cf.CoordinateReference.canonical_units('perspective_point_height')
<CF Units: m>
>>> cf.CoordinateReference.canonical_units('ptop')
None

        '''
        return _canonical_units.get(term, None)
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def T(self):
        '''

False.

Provides compatibility with the `cf.Coordinate` API.

.. seealso:: `cf.Coordinate.T`, `X`, `~cf.CoordinateReference.Y`, `Z`

:Examples:

>>> c.T
False

'''              
        return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def X(self):
        '''

Returns False.

Provides compatibility with the `cf.Coordinate` API.

.. seealso:: `cf.Coordinate.X`, `T`, `~cf.CoordinateReference.Y`, `Z`

:Examples:

>>> c.X
False

'''              
        return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def Y(self):
        '''

Returns False.

Provides compatibility with the `cf.Coordinate` API.

.. seealso:: `cf.Coordinate.Y`, `T`, `X`, `Z`

:Examples:

>>> c.Y
False

'''              
        return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def Z(self):
        '''

Returns False.

Provides compatibility with the `cf.Coordinate` API.

.. seealso:: `cf.Coordinate.Z`, `T`, `X`, `~cf.CoordinateReference.Y`

:Examples:

>>> c.Z
False

'''              
        return False
    #--- End: def

    def close(self):
        '''

Close all files referenced by coordinate conversion term values.

:Returns:

    None

:Examples:

>>> c.close()

'''
        for value in self.itervalues():
            if hasattr(value, 'close'):
                value.close()
    #--- End: def

    def copy(self, domain=None):
        '''

Return a deep copy.

``c.copy()`` is equivalent to ``copy.deepcopy(c)``.

:Examples 1:

>>> d = c.copy()

:Parameters:

    domain : cf.Domain, optional

:Returns:

    out :
        The deep copy.

:Examples 2:

>>> domain
<CF Domain: (110, 106, 3, 5)>
>>> d = c.copy(domain=domain)

'''       
        X = type(self)
        new = X.__new__(X)

        coord_terms = self.coord_terms.copy()

        new.coord_terms      = coord_terms
        new.coords           = self.coords.copy()
#        new._standard_coords = self._standard_coords.copy()
        new.name             = self.name
        new.type             = self.type

        _dict = {}
        for term, value in self._dict.iteritems():
            if (term in coord_terms or value is None or
                not hasattr(value, 'copy')):
                _dict[term] = value
            else:
                _dict[term] = value.copy()
        #--- End: for
        new._dict = _dict

        if domain is not None:
            # --------------------------------------------------------
            # Replace coordinate identifiers with coordinate names
            # derived from a domain object
            # --------------------------------------------------------
            coord_map = {}
            for name in new.coords:
                coord = domain.item(name, role=('d', 'a',), exact=True)
                if coord is not None:
                    coord_map[name] = coord.name(default=None, identity=True)
            #--- End: for
            new.change_coord_identities(coord_map, i=True)
        #--- End: if

        return new
    #---End: def

    @classmethod
    def default_value(cls, term):
        '''

Return the default value for an unset standard CF coordinate
conversion term.

The default values are stored in the file
cf/etc/coordinate_reference/default_values.txt.

:Parameters:	

    term : str
        The name of the term.

:Returns:	

    out : 
        The default value, or `None` if there is not one.

:Examples:

>>> cf.CoordinateReference.default_value('ptop')
0.0
>>> print cf.CoordinateReference.default_value('north_pole_grid_latitude')
None

        '''
        return _default_values.get(term, None)
    #--- End: def

    def dump(self, complete=False, display=True, _level=0, domain=None):
        '''

Return a string containing a full description of the coordinate
reference.

:Parameters:

    complete : bool, optional

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``c.dump()`` is equivalent to
        ``print c.dump(display=False)``.

    domain : cf.Domain, optional

:Returns:

    out : str
        A string containing the description.

:Examples:

        '''          
        indent0 = '    ' * _level
        indent1 = '    ' * (_level+1)

        try:
            string = ['%sCoordinate reference: %s' % (indent0, self.identity(''))]
        except AttributeError:
            string = ['%sCoordinate reference: ' % indent0]

        if domain:
            coord_keys = domain.items(role='da')
            for key, value in sorted(self.iteritems()):
                if value in coord_keys:
                    string.append("%s%s = %r" % (indent1, key, domain.get(value)))
                else:
                    # value is a field
                    if complete and hasattr(value, 'domain'):
                        string.append(
                            "%s%s = \n%s" % 
                            (indent1, key, 
                             value.dump(
                                 complete=False, display=False, 
                                 _level=_level+2,
                                 _title='Coordinate reference field', _q='-')))
                    else:
                        string.append("%s%s = %r" % (indent1, key, value))
        else:
             for key, value in sorted(self.iteritems()):
                if complete and hasattr(value, 'domain'):
                    # value is a field
                    string.append("%s%s = \n%s" % 
                                  (indent1, key, 
                                   value.dump(complete=False, display=False, 
                                              _level=_level+2, 
                                              _title='Coordinate reference field', _q='-')))
                else:
                    string.append("%s%s = %r" % (indent1, key, value))
        #--- End: if

        string = '\n'.join(string)
       
        if display:
            print string
        else:
            return string
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False):
        '''

True if two instances are equal, False otherwise.

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
   
        # ------------------------------------------------------------
        # Check the name
        # ------------------------------------------------------------
        if self.name != other.name:
            if traceback:
                print(
"%s: Different names (%s != %s)" %
(self.__class__.__name__, self.name, other.name))
            return False
        #--- End: if
                
        if rtol is None:
            rtol = RTOL()
        if atol is None:
            atol = ATOL()

        # ------------------------------------------------------------
        # Check that the same terms are present
        # ------------------------------------------------------------
        if set(self) != set(other):
            if traceback:
                print(
"%s: Different collections of terms (%s != %s)" %
(self.__class__.__name__, set(self), set(other)))
            return False
        #--- End: if

        # Check that the coordinate terms match
        coord_terms0 = self.coord_terms
        coord_terms1 = other.coord_terms
        if coord_terms0 != coord_terms1:
            if traceback:
                print(
"%s: Different coordinate-valued terms (%s != %s)" % 
(self.__class__.__name__, coord_terms0, coord_terms1))
            return False
        #--- End: if

        # ------------------------------------------------------------
        # Check that the term values are equal.
        #
        # If the values for a particular term are both undefined or
        # are both pointers to coordinates then they are considered
        # equal.
        # ------------------------------------------------------------
        coords0 = self.coords
        coords1 = other.coords
        if len(coords0) != len(coords1):
            if traceback:
                print(
"%s: Different sized collections of coordinates (%d != %d)" % 
(self.__class__.__name__, len(coords0), len(coords1)))
            return False
        #--- End: if

        for term, value0 in self.iteritems():            
            if term in coord_terms0 and term in coord_terms1:
                # Term values are coordinates in both coordinate
                # references
                continue
                
            value1 = other[term]  

            if value0 is None and value1 is None:
                # Term values are None in both coordinate
                # references
                continue
                
            if equals(value0, value1, rtol=rtol, atol=atol,
                      ignore_fill_value=ignore_fill_value,
                      traceback=traceback):
                # Term values are the same in both coordinate
                # references
                continue

            # Still here? Then the two coordinate references are not
            # equal.
            if traceback:
                print(
"%s: Unequal '%s' terms (%r != %r)" % 
(self.__class__.__name__, term, value0, value1))
                return False
        #--- End: for

        # ------------------------------------------------------------
        # Still here? Then the two coordinate references are as equal
        # as can be ascertained in the absence of domains.
        # ------------------------------------------------------------
        return True
    #--- End: def

    def equivalent(self, other, atol=None, rtol=None, traceback=False):
        '''True if two coordinate references are logically equal, False
otherwise.

:Parameters:

    other : cf.CoordinateReference
        The object to compare for equality.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `cf.ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `cf.RTOL` function is used.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        instances differ.

:Returns:

    out : bool
        Whether or not the two objects are equivalent.

:Examples:

>>>

        '''
        if self is other:
            return True
        
        # Check that each instance is the same type
        if self.__class__ != other.__class__:
            if traceback:
                print("%s: Different types (%r != %r)" %
                      (self.__class__.__name__,
                       self.__class__.__name__, other.__class__.__name__))
            return False
        #--- End: if
   
        # ------------------------------------------------------------
        # Check the name
        # ------------------------------------------------------------
        if self.name != other.name:
            if traceback:
                print("%s: Different names (%r != %r)" %
                      (self.__class__.__name__, self.name, other.name))
            return False
        #--- End: if
                
        if rtol is None:
            rtol = RTOL()
        if atol is None:
            atol = ATOL()

        # Check that the term values are equal.
        #
        # If the values for a particular key are both undefined or
        # pointers to coordinates, then they are considered equal.
        coords0 = self.coords
        coords1 = other.coords

        for term in set(self).union(other):

            if term in self.coord_terms and term in other.coord_terms:
                # ----------------------------------------------------
                # Both terms are coordinates
                # ---------------------------------------------------- 
                continue

            value0 = self.get(term, None)
            value1 = other.get(term, None)

            if value1 is None and value0 is None:
                # ----------------------------------------------------
                # Both terms are undefined
                # ----------------------------------------------------
                continue

            if value1 is None:
                t, value = self, value0
            elif value0 is None:
                t, value = other, value1
            else:
                t = None

            if t is not None:
                # ----------------------------------------------------
                # Exactly one term is undefined
                # ----------------------------------------------------
                if term in t.coord_terms:
                    # Term is a coordinate
                    continue

                default = t.default_value(term)
                if default is None:
                    if traceback:
                        print("%s: Unequivalent %r term" %
                              (self.__class__.__name__,  term))
                    return

                if not allclose(value, default, rtol=rtol, atol=atol): 
                    if traceback:
                        print("%s: Unequivalent %r term" %
                              (self.__class__.__name__,  term))
                    return
            #--- End: if

            # ----------------------------------------------------
            # Both terms are defined and are not coordinates
            # ---------------------------------------------------- 
            if not allclose(value0, value1, rtol=rtol, atol=atol):
                if traceback:
                    print("%s: Unequivalent %r term (%r != %r)" % 
                          (self.__class__.__name__, term, value0, value1))
                return False
        #--- End: for

        # Still here?
        return True
    #--- End: def

    def identity(self, default=None):
        '''Return the identity of the coordinate reference.

The identity is the standard_name of a formula_terms-type coordinate
reference or the grid_mapping_name of grid_mapping-type coordinate
reference.

:Parameters:

    default : optional
        If the coordinate reference has no identity then return
        *default*. By default, *default* is None.

:Returns:

    out :
        The identity.

:Examples:

>>> c.identity()
'rotated_latitude_longitude'
>>> c.identity()
'atmosphere_hybrid_height_coordinate'

        '''
        return getattr(self, 'name', default)
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

    def match(self, match=None, exact=False, match_all=True, inverse=False):
        '''Test whether or not the coordinate reference satisfies the given
conditions.

:Returns:

    out : bool
        True if the coordinate reference satisfies the given criteria,
        False otherwise.

:Examples:

        '''
        conditions_have_been_set = False
        something_has_matched    = False

        matches = self._parse_match(match)

        if not match:
            return True

        if isinstance(match, (basestring, dict, Query)):
            match = (match,)

        if matches:
            conditions_have_been_set = True

        found_match = True
        for match in matches:
            found_match = True

            for prop, value in match.iteritems():
                if prop is None:
                    if isinstance(value, basestring):
                        if value in ('T', 'X', 'Y', 'Z'):
                            # Axis type
                            x = getattr(self, value)
                            value = True
                        elif '%' in value:
                            # Python attribute (string-valued)
                            value = value.split('%')
                            x = getattr(self, value[0], None)
                            value = '%'.join(value[1:])
                        else:
                            # Identity (string-valued)
                            x = self.identity(None)
                    else:   
                        # Identity (not string-valued, e.g. cf.Query)
                        x = self.identity(None)
                else:
                    # CF term name                    
                    x = self.get(prop, None)

                if x is None:
                    found_match = False
                elif isinstance(x, basestring) and isinstance(value, basestring):
                    if exact:
                        found_match = (value == x)
                    else:
                        found_match = re_match(value, x)
                else:	
                    found_match = (value == x)
                    try:
                        found_match == True
                    except ValueError:
                        found_match = False
                #--- End: if

                if found_match:
                    break
            #--- End: for

            if found_match:
                something_has_matched = True
                break
        #--- End: for

        if match_all and not found_match:
            return bool(inverse)

        if conditions_have_been_set:
            if something_has_matched:            
                return not bool(inverse)
            else:
                return bool(inverse)
        else:
            return not bool(inverse)
    #--- End: def

    def change_coord_identities(self, coord_map, i=False):
        '''Change the idientifier of all coordinates.

If a coordinate identifier is not in the provided mapping then it is
set to `None` and thus effectively removed from the coordinate
reference.

:Parameters:

    coord_map : dict
        For example: ``{'dim2': 'dim3', 'aux2': 'latitude', 'aux4': None}``

    i : bool, optional

:Returns:

    None

:Examples:

>>> r = cf.CoordinateReference('atmosphere_hybrid_height_coordinate',
...                             coord_terms=['a', 'b'],
...                             a='ncvar:ak',
...                             b='ncvar:bk')
>>> r.coords
{'atmosphere_hybrid_height_coordinate', 'ncvar:ak', 'ncvar:bk'}
>>> r.change_coord_identitiers({'atmosphere_hybrid_height_coordinate', 'dim1',
...                             'ncvar:ak': 'aux0'})
>>> r.coords
{'dim1', 'aux0'}

        '''
        if i:
            r = self
        else:
            r = self.copy()

#        if keep_unmapped:
        if not coord_map:
            return r

#        coord_map = coord_map.copy()
#        for name in r.coords:
#            if name not in coord_map:
#                coord_map[name] = name
#        #--- End: for

        for term in self.coord_terms:
            coord = r[term]
            r[term] = coord_map.get(coord, coord)

#        coords = set([coord_map.get(coord, None) for coord in r.coords])
        coords = set([coord_map.get(coord, coord) for coord in r.coords])
        coords.discard(None)
        r.coords = coords

#        _standard_coords = [(coord_map.get(name, name), sn) 
#                            for name, sn in r._standard_coords.iteritems()]
#        r._standard_coords = dict(_standard_coords)

        return r
    #---End: def

#    def reset_coords(self, *identifiers, i=False):
#        coord_map = {}
#        for identifier in identifiers:
#            coord_map[identifier] = self._reset_coords.get(identifier, None)
#
#        return self.change_coord_identities(coord_map, i=i)
#    #--- End: def

#    def reset_coord(self, identifier, i=False):
#        '''
##        '''
#        new_name = self._standard_coords.get(identifier, None)    
#        coord_map = {identifier: new_name}
#        return self.change_coord_identities(coord_map, i=i)
#    #--- End: def

    def remove_all_coords(self):
        '''Remove all links to coordinate objects.

All terms linked to coordinate objects are set to `None`.

:Returns:

    None

:Examples:

>>> c.remove_all_coords()

        '''
        self.coords.clear()

        for term in self.coord_terms:
            self[term] = None                  
    #---End: def

    def setcoord(self, term, value):
        '''


'''
        super(CoordinateReference, self).__setitem__(term, value)
        self.coord_terms.add(term)
        self.coords.add(value)
    #--- End: def

    def set(self, term, value):
        '''


'''
        super(CoordinateReference, self).__setitem__(term, value)
    #--- End: def

    def structural_signature(self, rtol=None, atol=None):
        '''
'''     
        name = self.name
        s = [name]
        append = s.append
        
        coord_terms = self.coord_terms
        non_constant_terms = _non_constant_terms.get(name, ())

        for term, value in sorted(self.iteritems()):
            if term in non_constant_terms:
                continue

            if term in coord_terms:
                continue

            if isinstance(value, basestring):
                append((term, value))
                continue
                
            value = Data.asdata(value)

            cu = _canonical_units.get(term, None)
            if cu is not None:
                if value.Units.equivalent(cu):
                    value.Units = cu
                elif value.Units:
                    cu = value.Units
            else:
                cu = value.Units

            if str(cu) in _units:
                cu = _units[str(cu)]
            else:    
                ok = 0
                for units in _units.itervalues():
                    if cu.equals(units):
                        _units[str(cu)] = units
                        cu = units
                        ok = 1
                        break
                if not ok:
                    _units[str(cu)] = cu 


            default = self.default_value(term)
            if (default is not None and 
                allclose(value, default, rtol=rtol, atol=atol)):
                continue
            
            append((term, value, cu))
        #--- End: for                
                
        return tuple(s)
    #---End: def

#--- End: class
