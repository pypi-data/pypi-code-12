from itertools import izip, izip_longest, chain
from operator  import itemgetter
from re        import search as re_search

from .coordinatereference import CoordinateReference
from .functions           import RTOL, ATOL, equals, allclose
from .functions           import inspect as cf_inspect
from .query               import Query, gt, le
from .units               import Units


# ====================================================================
#
# Domain object
#
# ====================================================================

class Domain(object):
    '''Completely describe a field's coordinate system (domain).

It contains the domain axis constructs, dimension coordinate
constructs, auxiliary coordinate constructs, cell measure constructs
and coordinate reference constructs defined by the CF data model.

    '''

    def __init__(self, axes=None, dim=None, aux=None, measure=None, 
                 ref=None, copy=True, assign_axes=None, **kwargs):
        '''**Initialization**

:Parameters:

    axes : *optional*
        Initialize axes of the domain. The *axes* parameter may be one
        of:

          * `None`. This is the default and axes are inferred from the
            dimension coordinate specified with the *dim* parameter.

        ..

          * (A sequence of) `int`. For each integer, an axis with that
            size is inserted into the domain with domain identifiers
            ``'dim0'``, ``'dim1'``, etc. for the first to the last
            axes in the sequence. If *axes* is an integer (rather than
            a sequence) then it is treated as a single element
            sequence.
            
              *Example:*
                To insert an axis of size 12 with domain identifier
                ``'dim0'``: ``axes=12``.

              *Example:*
                To insert axes of sizes 73 and 96 with domain
                identifiers ``'dim0'`` and ``'dim1'`` respectively:
                ``axes=[73, 96]``.

        ..

          * A dictionary which maps axis domain identifiers to axis
            sizes.

              *Example:*
                To insert an axis of size 12 with domain identifier
                ``'dim4'``: ``axes={'dim4': 12}``.

              *Example:*
                To insert axes of sizes 73 and 96 with domain
                identifiers ``'dim3'`` and ``'dim4'`` respectively:
                ``axes={'dim3': 73, 'dim4': 96}``.


        Note that axis initialization occurs before the initialization
        of dimension coordiante, auxiliary coordinate and cell measure
        and coordinate reference objects.

    dim : *optional*
        Initialize dimension coordinate objects of the domain.

        Inserting a dimension coordinate object into the domain will
        automatically create a domain axis of the correct size, unless
        an axis with the same domain identifier has already been
        created with the *axes* parameter. So, in general, it is not
        necessary to initialize the axes spanned by dimension
        coordinates with the *axes* parameter.

        The *dim* parameter may be one of:

          * `None`. This is the default and no dimension coordinate
            objects are inserted into the domain.

        ..

          * (A sequence of) `cf.DimensionCoordinate`. Each dimension
            coordinate object is inserted into the domain with domain
            identifiers ``'dim0'``, ``'dim1'``, etc. for the first to
            the last dimension coordinate object in the sequence. If
            *dim* is a `cf.DimensionCoordinate` (rather than a
            sequence) then it is treated as a single element sequence.
            
              *Example:*
                To insert a dimension coordinate, ``x``, with domain
                identifier ``'dim0'``: ``dim=x``.

              *Example:*
                To insert dimension coordinates, ``x`` and ``y``, with
                domain identifiers ``'dim0'`` and ``'dim1'``
                respectively: ``dim=[x, y]``.

        ..

          * A dictionary which maps dimension coordinate domain
            identifiers to `cf.DimensionCoordinate` objects.

              *Example:*
                To insert a dimension coordinate, ``t``, with domain
                identifier ``'dim4'``: ``dim={'dim4': t}``.

              *Example:*
                To insert dimension coordinates, ``x`` and ``y``, with
                domain identifiers ``'dim3'`` and ``'dim4'``
                respectively: ``dim={'dim3': x, 'dim4': y}``.

        Note that dimension coordinate initialization occurs after
        axis initialization and before the initialization of auxiliary
        coordinate and cell measure and coordinate reference objects.

    aux : *optional*
        Initialize auxiliary coordinate objects of the domain.

        The axes spanned by an auxiliary coordinate **must** be
        defined by the *axes* and/or *dim* parameters. If there is no
        ambiguity (as will be the case if all of the axes have
        different sizes) then it is not necessary to describe which
        axes an auxiliary coordinate spans, and in which
        order. Otherwise, or in any case, the auxiliary coordinate
        axes may be specified with the *assign_axes* parameter.

        The *aux* parameter may be one of:

          * `None`. This is the default and no auxiliary coordinate
            objects are inserted into the domain.

        ..

          * (A sequence of) `cf.AuxiliaryCoordinate`. Each auxiliary
            coordinate object is inserted into the domain with domain
            identifiers ``'aux0'``, ``'aux1'``, etc. for the first to
            the last auxiliary coordinate object in the sequence. If
            *aux* is a `cf.AuxiliaryCoordinate` (rather than a
            sequence) then it is treated as a single element sequence.
            
              *Example:*
                To insert an auxiliary coordinate, ``p``, with domain
                identifier ``'aux0'``: ``aux=p``.

              *Example:*
                To insert auxiliary coordinates, ``p`` and ``q``, with
                domain identifiers ``'aux0'`` and ``'aux1'``
                respectively: ``aux=[p, q]``.

        ..

          * A dictionary which maps auxiliary coordinate domain
            identifiers to `cf.AuxiliaryCoordinate` objects.

              *Example:*
                To insert an auxiliary coordinate, ``r``, with domain
                identifier ``'aux4'``: ``aux={'aux4': r}``.

              *Example:*
                To insert auxiliary coordinates, ``p`` and ``q``, with
                domain identifiers ``'aux3'`` and ``'aux4'``
                respectively: ``aux={'aux3': p, 'aux4': q}``.

        Note that auxiliary coordinate initialization occurs after
        axis and dimension coordinate initialization.

    measure : *optional*
        Initialize cell measure objects of the domain.

        The axes spanned by a cell measure object **must** be defined
        by the *axes* and/or *dim* parameters. If there is no
        ambiguity (as will be the case if all of the axes have
        different sizes) then it is not necessary to describe which
        axes a cell measure spans, and in which order. Otherwise, or
        in any case, the cell measure axes may be specified with the
        *assign_axes* parameter.

        The *measure* parameter may be one of:

          * `None`. This is the default and no cell measure objects
            are inserted into the domain.

        ..

          * (A sequence of) `cf.CellMeasure`. Each cell measure object
            is inserted into the domain with domain identifiers
            ``'msr0'``, ``'msr1'``, etc. for the first to the last
            cell measure object in the sequence. If *msr* is a
            `cf.CellMeasure` (rather than a sequence) then it is
            treated as a single element sequence.
            
              *Example:*
                To insert a cell measure, ``m``, with domain
                identifier ``'msr0'``: ``msr=m``.

              *Example:*
                To insert cell measures, ``m`` and ``n``, with domain
                identifiers ``'msr0'`` and ``'msr1'`` respectively:
                ``msr=[m, n]``.

        ..

          * A dictionary which maps cell measure domain identifiers to
            `cf.CellMeasure` objects.

              *Example:*
                To insert a cell measure, ``m``, with domain
                identifier ``'msr4'``: ``msr={'msr4': m}``.

              *Example:*
                To insert cell measures, ``m`` and ``n``, with domain
                identifiers ``'msr3'`` and ``'msr4'`` respectively:
                ``msr={'msr3': m, 'msr4': n}``.

        Note that cell measure initialization occurs after axis,
        dimension coordinate and auxiliary coordinate initialization.

    assign_axes, kwargs : dict, optional
        Map coordinate and cell measure objects to the axes which they
        span.

        Each dictionary key is a domain identifier of a dimension
        coordinate, auxiliary coordinate or cell measure object which
        has been previously defined by the *dim*, *aux* or *measure*
        parameters. Its corresponding value specifies the axes that
        the item spans, in the correct order. The axes are those
        returned by this call of the domain's `axes` method:
        ``d.axes(value, order=True, **kwargs)`` (see `cf.Field.axes`
        for details).
        
        For each dimension coordinate, auxiliary coordinate or cell
        measure object, if there is no ambiguity as to which axes it
        spans (as will be the case if all of the axes have different
        sizes) then it is not necessary provide this item to the
        *assign_axes* dictionary, as the spanning axes may be deduced
        automatically. Otherwise it is required.

          *Example:*
            Auxiliary coordinate ``'aux0'`` spans axis ``'dim0'`` and
            auxiliary coordinate ``'aux1'`` spans axes ``'dim2'`` and
            ``dim1'``, in that order: ``assign_axes={'aux0': 'dim0',
            'aux1': ['dim2', `dim1`]}``.
            
          *Example:*
            Auxiliary coordinate ``'aux0'`` spans axis the Z axis cell
            measure ``'msr1'`` spans the Y and X axes, in that order:
            ``assign_axes={'aux0': 'Z', 'msr1': ['Y', 'X']}``. In this
            case it is assumed that the axes have dimension
            coordinates with sufficient metadta to be able to define
            them as Z, Y and X axes.

    ref : *optional*
        Initialize coordinate reference objects of the domain.

        The *ref* parameter may be one of:

          * `None`. This is the default and no coordinate reference
            objects are inserted into the domain.

        ..

          * (A sequence of) `cf.CoordinateReference`. Each coordinate
            reference object is inserted into the domain with domain
            identifiers ``'ref0'``, ``'ref1'``, etc. for the first to
            the last coordinate reference object in the sequence. If
            *ref* is a `cf.CoordinateReference` (rather than a
            sequence) then it is treated as a single element sequence.
            
              *Example:*
                To insert a coordinate reference, ``b``, with domain
                identifier ``'ref0'``: ``ref=b``.

              *Example:*
                To insert coordinate references, ``b`` and ``c``, with
                domain identifiers ``'ref0'`` and ``'ref1'``
                respectively: ``ref=[b, c]``.

        ..

          * A dictionary which maps coordinate reference domain
            identifiers to `cf.CoordinateReference` objects.

              *Example:*
                To insert a coordinate reference, ``m``, with domain
                identifier ``'ref4'``: ``ref={'ref4': m}``.

              *Example:*
                To insert coordinate references, ``b`` and ``c``, with
                domain identifiers ``'ref3'`` and ``'ref4'``
                respectively: ``ref={'ref3': b, 'ref4': c}``.

        Note that coordinate reference initialization occurs after
        axis, dimension coordinate, auxiliary coordinate and cell
        measure initialization.

    copy : bool, optional
        If True (the default) then all dimension coordinate, auxiliary
        coordinate, cell measure and coordinate reference objects are
        copied prior to insertion.

:Examples:

In this example, four dots (``....``) refers to appropriate
initialization parameters of the coordinate, cell measure and
coordinate reference constructs, which are omitted here for clarity.

>>> dim_coord_A = cf.DimensionCoordinate(....)
>>> dim_coord_B = cf.DimensionCoordinate(....)
>>> dim_coord_A.size, dim_coord_B.size
(73, 96)
>>> dim_coord_A.X, dim_coord_B.Y
(True, True)
>>> aux_coord_A = cf.AuxiliaryCoordinate(....)
>>> aux_coord_A.shape
(96, 73)
>>> cell_measure_A = cf.CellMeasure(....)
>>> cell_measure_A.shape
(73, 96)
>>> ref_A = cf.CoordinateReference(name='latitude_longitude', ....)
>>> d = cf.Domain(dim=[dim_coord_A, dim_coord_B],
...               aux=aux_coord_A,
...               measure=cell_measure_A,
...               ref=ref_A)
...
>>> d.items_axes()
{'aux0': ['dim1', 'dim0'],
 'msr0': ['dim0', 'dim1'],
 'dim1': ['dim1'],
 'dim0': ['dim0']}
>>> d.refs
{'ref0' : <CF CoordinateReference: latitude_longitude>}

It was not necessary to specify the axis mappings for ``aux_coord_A``
and ``cell_measure_A`` because the two axes have unambiguous sizes.

The same domain could have been initialised using the dictionary form
of the parameters and explicitly assigning axes described by their
dimension coordinate metadata:

>>> e = cf.Domain(axes={'dim0': 73, 'dim1': 96},
...               dim={'dim0': dim_coord_A, 'dim1': dim_coord_B},
...               aux={'aux0': aux_coord_A},
...               measure={'msr0': cell_measureA},
...               ref={'ref0': ref_A},
...               assign_axes={'aux0': ['Y', 'X'],
...                            'msr0': ['X', 'Y']})
...
>>> e.equals(d)
True

        '''
        self.d = {}
        self.a = {}        
        self.m = {}
        self.r = {}
        self._map = {}
        self._axes = {}
        self._axes_sizes = {}

        # ------------------------------------------------------------
        # Initialize axes
        # ------------------------------------------------------------
        if axes or axes == 0:
            if isinstance(axes, dict):  
                for key, size in axes.iteritems():
                    self.insert_axis(size, key=key, replace=False)
            else:
                if isinstance(axes, (int, long)):
                    axes = (axes,)

                for size in axes:
                    self.insert_axis(size)
        #--- End: if

        # ------------------------------------------------------------
        # Initialize dimension coordinates
        # ------------------------------------------------------------
        if dim:
            if isinstance(dim, dict):
                for key, coord in dim.iteritems():
                    self.insert_dim(coord, key=key, copy=copy, replace=False)
            else:
                for coord in dim:
                    key = self.new_axis_identifier()
                    self.insert_dim(coord, key=key, copy=copy, replace=False)
        #--- End: if

        # ------------------------------------------------------------
        # Assign axes to auxiliary coordinates and cell measures
        # ------------------------------------------------------------
        if assign_axes:
            for key, value in assign_axes.iteritems():
                self._axes[key] = self.axes(value, ordered=True)
        #--- End: if

        # ------------------------------------------------------------
        # Initialize auxiliary coordinates
        # ------------------------------------------------------------
        if aux: 
            if isinstance(aux, dict):
                for key, coord in aux.iteritems():
                    aux_axes = self._axes.get(key, None)
                    self.insert_aux(coord, key=key, axes=aux_axes, copy=copy)
            else:
                for coord in aux:
                    key = self.new_aux_identifier()       
                    aux_axes = self._axes.get(key, None)
                    self.insert_aux(coord, key=key, axes=aux_axes, copy=copy)
        #--- End: if

        # ------------------------------------------------------------
        # Initialize cell measures
        # ------------------------------------------------------------
        if measure: 
            if isinstance(measure, dict):
                for key, msr in measure.iteritems():
                    msr_axes = self._axes.get(key, None)
                    self.insert_measure(msr, key=key, axes=msr_axes, copy=copy)
            else:
                for msr in measure:
                    key = self.new_measure_identifier()
                    msr_axes = self._axes.get(key, None)
                    self.insert_measure(msr, key=key, axes=msr_axes, copy=copy)
        #--- End: if

        # ------------------------------------------------------------
        # Initialize coordinate references
        # ------------------------------------------------------------
        if ref:
            if isinstance(ref, CoordinateReference):
                self.insert_ref(ref, copy=copy)

            elif isinstance(ref, dict):
                for key, coordref in ref.iteritems():
                    self.insert_ref(coordref, key=key, copy=copy)

            else:
                for N, coordref in enumerate(ref):
                    self.insert_ref(coordref, copy=copy)
        #--- End: if
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        data_axes = self._axes.get('data', ())
        w = sorted(["{0}({1})".format(self.axis_name(axis), size)
                    for axis, size in self._axes_sizes.iteritems()
                    if axis not in data_axes])
        x = ["{0}({1})".format(self.axis_name(axis), self._axes_sizes[axis])
             for axis in data_axes]
        axes = ', '.join(w+x)
        return '<CF {0}: {1}>'.format(self.__class__.__name__, axes)
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        mmm = {}
        def _print_coord(domain, key, variable, dimension_coord):
            '''Private function called by __str__'''

            if dimension_coord:
                name = "%s(%d)" % (domain.axis_name(key),
                                   domain._axes_sizes[key])
                mmm[key] = name
                if key not in domain.d:
                    return name
                else:
                    variable = domain.d[key]
                
                x = [name]
            #--- End: if

            # Still here?
            if not dimension_coord:               
                # Auxiliary coordinate
                shape = [mmm[dim] for dim in domain._axes[key]]
                shape = str(tuple(shape)).replace("'", "")
                shape = shape.replace(',)', ')')
                x = [variable.name('domain%'+key)]
                x.append(shape)
            #--- End: if

            try:
                variable.compress
            except AttributeError:
                if variable._hasData:
                    x.append(' = ')
                    x.append(str(variable.Data))
            else:
                x.append(' -> compressed ')
                compressed = []
                for unc in domain[key].compress:
                    shape = str(unc.size)
                    compressed.append(unc.name('unc')+'('+shape+')')
                x.append(', '.join(compressed))

            return ''.join(x)
        #--- End: def

        string = []

        x = [_print_coord(self, dim[0], None, True)
             for dim in sorted(self._axes_sizes.iteritems(), key=itemgetter(1))]
        if x:
            string.append('Axes           : ')
            string.append('\n               : '.join(x))

        x = [_print_coord(self, aux, v, False) 
             for aux, v in sorted(self.a.items())]
        if x:
            string.append('\n')
            string.append('Aux coords     : ')
            string.append('\n               : '.join(x))

        # Cell measures
        x = [_print_coord(self, msr, v, False)
             for msr, v in sorted(self.m.items())]
        if x:
            string.append('\n')
            string.append('Cell measures  : ')
            string.append('\n               : '.join(x))

        # Coordinate references
        x = [repr(ref) for ref in self.r.values()]
        if x:
            string.append('\n')
            string.append('Coord refs     : ')
            string.append('\n               : '.join(x))
        #--- End: if

        return ''.join(string)
    #--- End: def

    def _conform_ref(self, ref):
        '''Replace the content of ref.coords with domain coordinate
identifiers, where possible.

:Parameters:

    ref : cf.CoordinateReference

:Returns:

    None

:Examples:

>>> d._conform_ref(r)

        '''
        coord_map = {}
        role = ('d', 'a')
        for identifier in ref.coords:
            key = self.item(identifier, role=role, exact=True, key=True)
            if key is not None:
                coord_map[identifier] = key
#            else:
 #               coord_map[identifier] = ref._standard_coords.get(identifier, identifier)
        #--- End: for

        ref.change_coord_identities(coord_map, i=True)
    #--- End: def

    def _replace_refs_coord_identifier(self, key):
        '''

Replace a coordinate domain key with a coordinate identity in all
coordinate references.

If the coordinate object has no identity then the coordinate object is
effectively removed.

:Parameters:

    key : str
        A domain coordinate object identifier.

:Returns:

    None

:Examples:

>>> d._replace_refs_coord_identifier('dim1')
>>> d._replace_refs_coord_identifier('aux0')

'''
        coord_map = {key: self.get(key).identity(None)}
        for ref in self.r.itervalues():
            ref.change_coord_identities(coord_map, i=True)   
    #--- End: def

    def _set(self, key, value):
        '''

Set the item of a pre-existing identifier of the domain.

An item is either a dimension coordinate, an auxiliary coordinate, a
cell measure or a coordinate reference object.

.. note:: Consistency is NOT checked.

.. seealso:: `get`, `has`

:Parameters:

    key : str
        A domain identifier.
    
    value :
        The new item corresponding to the domain identifier given by
        *key*.
    
:Returns:

    None

:Examples:

>>> d.items().keys()
['dim0', 'aux0', 'aux1', 'ref0']
>>> d._set('aux1', cf.AuxiliaryCoordinate(....))
>>> d._set('ref0', cf.CoordinateReference(....))

'''
        getattr(self, self._map[key])[key] = value
    #--- End: def

    def _equal_refs(self, t, u, domain, rtol=None, atol=None,
                    pointer_map={}, ignore_fill_value=False,
                    traceback=False):
        '''

:Parameters:

    t : cf.CoordinateReference

    u : cf.CoordinateReference

    domain : cf.Domain
        The domain which contains *u*.

    pointer_map : dict

    ignore_fill_value : bool, optional
        If True then data arrays with different fill values are
        considered equal. By default they are considered unequal.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        instances differ.

:Returns:

    out : bool

:Examples:

>>>

'''
        if rtol is None:
            rtol = RTOL()
        if atol is None:
            atol = ATOL()              

        if not t.equals(u, rtol=rtol, atol=atol,
                        ignore_fill_value=ignore_fill_value,
                        traceback=traceback):
            if traceback:
                print(
                    "%s: Unequal coordinate references (%r != %r)" %
                    (self.__class__.__name__, t, u))
            return False

        # If coordinate references have coordinate-valued terms -
        # check them
        for term in t.coord_terms:
            if u[term] in pointer_map:
                if t[term] == pointer_map[u[term]]:
                    continue
            elif u[term] == t[term]:
                continue    

            # Still here?
            if traceback:
                print(
                    "%s: Unequal %s coordinate references %r term" %
                    (self.__class__.__name__, t.name, term))

            return False
        #--- End: for

        return True
    #--- End: def

    @property
    def rank(self):
        '''

The number of axes in the domain.

:Examples:

>>> len(d.axes())
4
>>> d.rank
4

'''
        return len(self._axes_sizes)
    #--- End: def

    def equivalent(self, other, rtol=None, atol=None, traceback=False):
        '''

True if and only if two domains are logically equivalent.

:Parameters:

    other :
        The object to compare for equivalence.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        objects differ.

:Returns: 

    out : bool
        Whether or not the two objects are equivalent.
      
'''
        if sorted(self._axes_sizes.values()) != sorted(self._axes_sizes.values()):
            if traceback:
                print("{0}: Different axis sizes: {1} != {2}".format(
                        self.__class__.__name__, 
                        sorted(self._axes_sizes.values()),
                        sorted(other._axes_sizes.values())))
            return False

        s = self.analyse()
        t = other.analyse()
        
        if sorted(s['id_to_coord']) != sorted(t['id_to_coord']):
            if traceback:
                print(
                    "{0}: Different axis identities: {1} != {2}".format(
                        self.__class__.__name__,
                        sorted(s['id_to_coord']),
                        sorted(t['id_to_coord'])))
            return False
        
        for identity, coord0 in s['id_to_coord'].iteritems():
            coord1 = t['id_to_coord'][identity]
            if not coord0._equivalent_data(coord1, rtol=rtol, atol=atol):
                if traceback:
                    print(
                        "{0}: Non-equivalent 1-d coordinate data array: {1}".format(
                            self.__class__.__name__,
                            identity))
                return False
        #--- End: for
                
        keys1 = other.r.keys()
        for ref0 in self.r.itervalues():
            found_match = False
            for key1 in keys1:
                ref1 = other_t[key1]
                
                if self.equivalent_refs(ref0, ref1,
                                        domain=other, traceback=False):
                    found_match = True
                    refs1.remove(key1)
                    break
            #--- End: for

            if not found_match:
                if traceback:
                    print(
                        "{0}: Missing coordinate reference: {1}".format(
                            self.__class__.__name__,
                            ref0))
                return False
        #--- End: for                    

        return True
    #--- End: def

    def equivalent_refs(self, t, u, domain, atol=None, rtol=None,
                             traceback=False):
        '''

True if a coordinate refencence object is the same as one in another
domain.

:Parameters:

    t : cf.CoordinateReference

    u : cf.CoordinateReference

    domain : cf.Domain
        The domain which contains *u*.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        instances differ.

:Returns:

    out : bool

:Examples:

>>>

'''
        if not t.equivalent(u, rtol=rtol, atol=atol, traceback=traceback):
            if traceback:
                print(
                    "%s: Unequivalent coordinate references (%r != %r)" %
                    (self.__class__.__name__, t, u))
            return False

        t_coord_terms = t.coord_terms.copy()
        u_coord_terms = u.coord_terms.copy()

        for term in t_coord_terms.intersection(u_coord_terms):
            # Term is coordiante-valued in both t and u
            t_coord_terms.remove(term)
            u_coord_terms.remove(term)

            tcoord = self.item(t[term], role='da', exact=True)
            ucoord = domain.item(u[term], role='da', exact=True)

            if (tcoord is None or ucoord is None or 
                not tcoord._equivalent_data(ucoord, rtol=rtol, atol=atol)):
                if traceback:
                    print(
"%s: Unequal coordinate reference %r term" % (self.__class__.__name__, term))
                return False
        #--- End: for

        for term in t_coord_terms:  
            # Term is coordiante-valued in t but missing from u
            coord = self.item(t[term], role='da', exact=True)            
            default = t.default_value(term)
            if default is None or coord is None or not allclose(coord, default):
                if traceback:
                    print(
"%s: Unequivalent coordinate reference %r term" % (self.__class__.__name__,  term))
                return False
        #--- End: for

        for term in u_coord_terms:  
            # Term is coordiante-valued in u but missing from t
            coord = self.item(u[term], role='da', exact=True)
            default = u.default_value(term)
            if default is None or coord is None or not allclose(coord, default):
                if traceback:
                    print(
"%s: Unequivalent coordinate reference %r term" % (self.__class__.__name__,  term))
                return False
        #--- End: for

        # Still here?
        return True
    #--- End: def

    def canonical_ref(self, ref):
        '''
'''
        ref = ref.copy()
        
        for term, value in ref.iteritems():
            data = getattr(value, '__data__', None)
            if data is None:
                # Value has no units
                continue

            data = data()

            units = ref.canonical_units(term)
            if units is None:
                continue
                
            if isinstance(units, basestring):
                # units is a standard_name of a coordinate
                coord = self.item(units, role='da', exact=True)
                if coord is None:
                    continue
                
                units = coord.Units
            #--- End: if            

            if units.equivalent(data.Units):
                data.Units = units
            else:
                raise ValueError("asdddddddddddddd 87236768")
        #--- End: for

        return ref
    #--- End: def

    def analyse(self):
        '''

Analyse a domain.

:Returns:

    out : dict
        A desription of the domain.

:Examples:

>>> print d
Axes           : time(3) = [1979-05-01 12:00:00, ..., 1979-05-03 12:00:00] gregorian
               : air_pressure(5) = [850.000061035, ..., 50.0000038147] hPa
               : grid_longitude(106) = [-20.5400109887, ..., 25.6599887609] degrees
               : grid_latitude(110) = [23.3200002313, ..., -24.6399995089] degrees
Aux coords     : latitude(grid_latitude(110), grid_longitude(106)) = [[67.1246607722, ..., 22.8886948065]] degrees_N
               : longitude(grid_latitude(110), grid_longitude(106)) = [[-45.98136251, ..., 35.2925499052]] degrees_E
Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>

>>> d.analyse()
{'aux_coords': {'N-d': {'aux0': <CF AuxiliaryCoordinate: latitude(110, 106) degrees_N>,
                        'aux1': <CF AuxiliaryCoordinate: longitude(110, 106) degrees_E>},
                'dim0': {'1-d': {},
                         'N-d': {}},
                'dim1': {'1-d': {},
                         'N-d': {}},
                'dim2': {'1-d': {},
                         'N-d': {'aux0': <CF AuxiliaryCoordinate: latitude(110, 106) degrees_N>,
                                 'aux1': <CF AuxiliaryCoordinate: longitude(110, 106) degrees_E>}},
                'dim3': {'1-d': {},
                         'N-d': {'aux0': <CF AuxiliaryCoordinate: latitude(110, 106) degrees_N>,
                                 'aux1': <CF AuxiliaryCoordinate: longitude(110, 106) degrees_E>}}},
 'axis_to_coord': {'dim0': <CF DimensionCoordinate: time(3) gregorian>,
                   'dim1': <CF DimensionCoordinate: air_pressure(5) hPa>,
                   'dim2': <CF DimensionCoordinate: grid_latitude(110) degrees>,
                   'dim3': <CF DimensionCoordinate: grid_longitude(106) degrees>},
 'axis_to_id': {'dim0': 'time',
                'dim1': 'air_pressure',
                'dim2': 'grid_latitude',
                'dim3': 'grid_longitude'},
 'cell_measures': {'N-d': {},
                   'dim0': {'1-d': {},
                            'N-d': {}},
                   'dim1': {'1-d': {},
                            'N-d': {}},
                   'dim2': {'1-d': {},
                            'N-d': {}},
                   'dim3': {'1-d': {},
                            'N-d': {}}},
 'id_to_aux': {},
 'id_to_axis': {'air_pressure': 'dim1',
                'grid_latitude': 'dim2',
                'grid_longitude': 'dim3',
                'time': 'dim0'},
 'id_to_coord': {'air_pressure': <CF DimensionCoordinate: air_pressure(5) hPa>,
                 'grid_latitude': <CF DimensionCoordinate: grid_latitude(110) degrees>,
                 'grid_longitude': <CF DimensionCoordinate: grid_longitude(106) degrees>,
                 'time': <CF DimensionCoordinate: time(3) gregorian>},
 'id_to_key': {'air_pressure': 'dim1',
               'grid_latitude': 'dim2',
               'grid_longitude': 'dim3',
               'time': 'dim0'},
 'undefined_axes': [],
 'warnings': [],
}

'''
        a = {}

        # ------------------------------------------------------------
        # Map each axis identity to its domain identifier, if such a
        # mapping exists.
        #
        # For example:
        # >>> id_to_axis
        # {'time': 'dim0', 'height': dim1'}
        # ------------------------------------------------------------
        id_to_axis = {}

        # ------------------------------------------------------------
        # For each dimension that is identified by a 1-d auxiliary
        # coordinate, map its dimension's its domain identifier.
        #
        # For example:
        # >>> id_to_aux
        # {'region': 'aux0'}
        # ------------------------------------------------------------
        id_to_aux = {}

        # ------------------------------------------------------------
        # 
        #
        # For example:
        # >>> id_to_key
        # {'region': 'aux0'}
        # ------------------------------------------------------------
        id_to_key = {}

        # ------------------------------------------------------------
        # Map each dimension's identity to the coordinate which
        # provides that identity.
        #
        # For example:
        # >>> id_to_coord
        # {'time': <CF Coordinate: time(12)>}
        # ------------------------------------------------------------
        id_to_coord = {}

        axis_to_coord = {}
        aux_to_coord = {}

        # ------------------------------------------------------------
        #
        # ------------------------------------------------------------
        aux_coords = {}
        aux_coords['N-d'] = {}

        cell_measures = {}
        cell_measures['N-d'] = {}

        # ------------------------------------------------------------
        # List the dimensions which are undefined, in that no unique
        # identity can be assigned to them.
        #
        # For example:
        # >>> undefined_axes
        # ['dim2']
        # ------------------------------------------------------------
        undefined_axes = []

        # ------------------------------------------------------------
        #
        # ------------------------------------------------------------
        warnings = []

        for axis in self._axes_sizes:

            # Find this axis's 1-d and N-d auxiliary coordinates
            aux_coords[axis]        = {}
            aux_coords[axis]['1-d'] = {}
            aux_coords[axis]['N-d'] = {}
            for aux, coord in self.items(role='a', axes=axis).iteritems():
                if coord.ndim > 1:
                    aux_coords['N-d'][aux] = coord
                    aux_coords[axis]['N-d'][aux] = coord
                else:
                    aux_coords[axis]['1-d'][aux] = coord
            #--- End: for

            # Find this axis's 1-d and N-d cell measures
            cell_measures[axis]        = {}
            cell_measures[axis]['1-d'] = {}
            cell_measures[axis]['N-d'] = {}
            for msr, cell_measure in self.items(role='m', axes=axis).iteritems():
                if cell_measure.ndim > 1:
                    cell_measures['N-d'][msr]       = cell_measure
                    cell_measures[axis]['N-d'][msr] = cell_measure
                else:
                    cell_measures[axis]['1-d'][msr] = cell_measure
            #--- End: for

            if axis in self.d:
                # This axis of the domain has a dimension coordinate
                dim_coord = self.d[axis]
                identity = dim_coord.identity()
                if identity is None:
                    # Dimension coordinate has no identity, but it may
                    # have a recognised axis.
                    for ctype in ('T', 'X', 'Y', 'Z'):
                        if getattr(dim_coord, ctype):
                            identity = ctype
                            break
                #--- End: if

                if identity is not None and dim_coord._hasData:
                    if identity in id_to_axis:
                        warnings.append(
                            "Domain has more than one %r axis" % identity)

                    id_to_axis[identity]  = axis
                    id_to_key[identity]   = axis
                    id_to_coord[identity] = dim_coord
                    axis_to_coord[axis]   = dim_coord
                    continue

            elif len(aux_coords[axis]['1-d']) == 1:
                # This axis of the domain does not have a dimension
                # coordinate but it does have exactly one 1-d
                # auxiliary coordinate, so that will do.
                aux       = list(aux_coords[axis]['1-d'])[0]
                aux_coord = self.a[aux]
                
                identity = aux_coord.identity()
                if identity is not None and aux_coord._hasData:
                    if identity in id_to_axis:
                        warnings.append(
                            "Domain has more than one %r axis" % identity)

                    id_to_aux[identity]   = aux
                    id_to_key[identity]   = aux
                    id_to_axis[identity]  = axis
                    id_to_coord[identity] = aux_coord
                    axis_to_coord[axis]   = aux_coord
                    continue
            #--- End: if

            # Still here? Then this axis is undefined
            undefined_axes.append(axis)
        #--- End: for

        # ------------------------------------------------------------
        # Invert the mapping between dimensions and identities
        # ------------------------------------------------------------
        axis_to_id = {}
        for k, v in id_to_axis.iteritems():
            axis_to_id[v] = k

        return {'aux_coords'    : aux_coords,
                'axis_to_id'    : axis_to_id,
                'axis_to_coord' : axis_to_coord,
                'cell_measures' : cell_measures,
                'id_to_aux'     : id_to_aux,
                'id_to_coord'   : id_to_coord,
                'id_to_axis'    : id_to_axis,
                'id_to_key'     : id_to_key,
                'undefined_axes': undefined_axes,
                'warnings'      : warnings,                
                }    
    #--- End def 

#    def attach_to_ref(self, ref, item, term=None, **kwargs):
#        '''
#
#Attach a coordinate construct to a coordinate reference.
#
#:Parameters:
#
#    ref : cf.CoordinateReference
#
#    item, kwargs : *optional*
#        The coordinate to attach, identified as for the `item`
#        method.
#    
#    term : sequence of str, optional
#
#    
#:Returns:
#
#    None
#
#:Examples:
#
#>>> t
#<CF CoordinateReference: asdkjhfskjfhgslghldkjgf>
#>>> d.attach_to_ref(t, 'dim2')
#>>> d.attach_to_ref(t, 'longitude', term=['b1'])
#>>> d.attach_to_ref(t, ['latitude', 'long_name:latitude'], exact=True)
#  
#'''
#        kwargs['key']  = True
#        kwargs['role'] = ('d', 'a')
#        key = self.item(item, **kwargs)
#        if key is None:
#            raise ValueError("Can't find %r coordinate object to attach to %r" % 
#                             (item, ref))
#
#        if term:
#            for t in term:
#                ref[t] = key
#        else:
#            ref.coords.add(key)
#
#    #--- End: def

    def get(self, key, *default):        
        '''Return the item corresponding to an internal identifier.

An item is a dimension coordinate, an auxiliary coordinate, a cell
measure or a coordinate reference object.

.. seealso:: `has`, `item`

:Parameters:

    key : str        
        An internal identifier.

    default : *optional*
        Return *default* if and only if the domain does not have the
        given *key*.

:Returns:

    out :
        The item of the domain with the given internal identifier. If
        none exists and *default* is set then *default* is returned.

:Examples:

>>> d.get('dim0')
<CF DimensionCoordinate: atmosphere_hybrid_height_coordinate(1)>
>>> d.get('aux1')
<CF AuxiliaryCoordinate: latitude(10, 9) degree_N>
>>> d.get('msr0')
<CF CellMeasure: area(9, 10) km 2>
>>> d.get('ref0')
<CF CoordinateReference: rotated_latitude_longitude>
>>> d.get('bad_id')
ValueError: Domain doesn't have internal identifier 'bad_id'
>>> print d.get('bad_id', None)
None

        '''  
        if key in self._map:
            return getattr(self, self._map[key])[key]
        elif default:
            return default[0]
        else:
            raise ValueError(
                "Domain doesn't have internal identifier %r" % key)
     #--- End: def

    def has(self, key):        
        '''

True if the domain has the given internal identifier.

.. seealso:: `get`, 'item`, `items`

:Parameters:

    key : str        
        An internal identifier.

:Returns:

    out : bool
        Whether or not the domain has the internal identifier.

:Examples:

>>> d.items().keys()
['dim0', 'aux0', 'aux1', 'ref0']
>>> d.has('dim0')
True
>>> d.has('aux2')
False

'''
        return key in self._map
     #--- End: def

    def axis_name(self, axes=None, **kwargs):
        '''

Return the canonical name for an axis.

:Parameters:

    axis, kwargs : optional
        Select the axis which would be selected by this call of the
        domain's `~cf.Domain.axis` method: ``d.axis(axis,
        **kwargs)``. See `cf.Domain.axis` for details.

:Returns:

    out : str
        The canonical name for the axis.

:Examples:

>>> d.axis_name('dim0')
'time'
>>> d.axis_name('dim1')
'domain%dim1'
>>> d.axis_name('dim2')
'ncdim%lat'

'''        
        axis = self.axis(axes, **kwargs)
        if axis is None:
            raise ValueError("No unique axis could be identified")

        dim = self.item(role='d', axes_all=axis)
        if dim is not None:
            # Get the name from the dimension coordinate
            return dim.name('domain%%%s' % axis) 

        aux = self.item(role='a', axes_all=axis)
        if aux is not None:
            # Get the name from the unique 1-d auxiliary coordinate
            return aux.name('domain%%%s' % axis)
        else:
            try:
                # Get the name from netCDF dimension name
                return 'ncdim%%%s' % self.nc_dimensions[axis]
            except (KeyError, AttributeError):
                # Get the name from axis domain identifier
                return 'domain%%%s' % axis
    #--- End: def

    def axis_identity(self, axis=None, **kwargs):
        '''

Return the canonical name for an axis.

:Parameters:

    axis, kwargs : optional
        Select the axis which would be selected by this call of the
        domain's `~cf.Domain.axis` method: ``d.axis(axis,
        **kwargs)``. See `cf.Domain.axis` for details.

:Returns:

    out : str
        The canonical name for the axis.

:Examples:

'''        
        axis = self.axis(axis, **kwargs)
        if axis is None:
            raise ValueError("No unique axis could be identified")

        dim = self.item(role='d', axes_all=axis)
        if dim is not None:
            # Get the identity from the dimension coordinate
            return dim.identity()

        aux = self.item(role='a', axes_all=axis)
        if aux is not None:
            # Get the identity from the unique 1-d auxiliary coordinate
            return aux.identity()

        return None
    #--- End: def

    def direction(self, axis):
        '''

Return True if an axis is increasing, otherwise return False.

An axis is considered to be increasing if its dimension coordinate
values are increasing in index space or if it has no dimension
coordinate.

.. seealso:: `directions`

:Parameters:

    axis : str
        A domain axis identifier, such as ``'dim0'``.

:Returns:

    out : bool
        Whether or not the axis is increasing.
        
:Examples:

>>> d._axes_sizes
{'dim0': 3, 'dim1': 1, 'dim2': 2, 'dim3': 2, 'dim4': 99}
>>> d.items_axes()
{'dim0': ['dim0'],
 'dim1': ['dim1'],
 'aux0': ['dim0'],
 'aux1': ['dim2'],
 'aux2': ['dim3'],
}
>>> d['dim0'].array
array([  0  30  60])
>>> d.direction('dim0')
True
>>> d['dim1'].array
array([15])
>>> d['dim1'].bounds.array
array([  30  0])
>>> d.direction('dim1')
False
>>> d['aux1'].array
array([0, -1])
>>> d.direction('dim2')
True
>>> d['aux2'].array
array(['z' 'a'])
>>> d.direction('dim3')
True
>>> d.direction('dim4')
True

'''
        if axis in self.d:
            return self.d[axis].direction()
        
        return True        
    #--- End: def
  
    def directions(self):
        '''

Return a dictionary mapping axes to their directions.

.. seealso:: `direction`

:Returns:

    out : dict
        A dictionary whose key/value pairs are axis identifiers and
        their directions.

:Examples:

>>> d.directions()
{'dim1': True, 'dim0': False}

'''
        self_direction = self.direction

        directions = {}
        for axis in self._axes_sizes:
            directions[axis] = self_direction(axis)

        return directions
    #--- End: def

    def map_axes(self, other):
        '''

Map the axis identifiers of the domain to their equivalent axis
identifiers of another.

:Parameters:

    other : cf.Domain

:Returns:

    out : dict
        A dictionary whose keys are the axis identifiers of the domain
        with corresponding values of axis identifiers of the of other
        domain.

:Examples:

>>> d.map_axes(e)
{'dim0': 'dim1',
 'dim1': 'dim0',
 'dim2': 'dim2'}

'''
        s = self.analyse()
        t = other.analyse()
        
        out = {}
        
        for identity, dim in s['id_to_axis'].iteritems():
            if identity in t['id_to_axis']:
                out[dim] = t['id_to_axis'][identity]
        #--- End: for

        return out
    #--- End: def

    def insert_axis(self, size, key=None, replace=True):
        '''

Insert an axis into the domain in place.

This method has exactly the same interface, functionality and outputs
as `cf.Field.insert_axis`. Therefore see `cf.Field.insert_axis` for
the full documentation details.

.. seealso:: `insert_aux`, insert_measure`, insert_dim`, insert_ref`

:Examples 1:

>>> d.insert_axis(24)

:Parameters:

    size : int
        The size of the new axis.

    key : str, optional
        The domain identifier for the new axis. By default a new,
        unique identifier is generated.
  
    replace : bool, optional
        If False then do not replace an existing axis with the same
        identifier but a different size. By default an existing axis
        with the same identifier is changed to have the new size.

:Returns:

    out :
        The domain identifier of the new axis.

:Examples 2:

See `cf.Field.insert_axis`.

'''
        if key is not None:
            if (key in self._axes_sizes and not replace and 
                self._axes_sizes[key] != size):
                raise ValueError(
"Can't insert axis: Existing axis %r has different size (got %d, expected %d)" %
(key, size, self._axes_sizes[key]))

            self._axes_sizes[key] = size
            return key

        # Still here? Then no identifier was specified for the
        # dimension, so create a new one.
        key = self.new_axis_identifier()
        self._axes_sizes[key] = size

        return key
    #--- End: def

    def new_axis_identifier(self):
        '''

Return a new, unique axis identifier for the domain.

.. seealso:: `new_aux_identifier`, `new_measure_identifier`,
             `new_dim_identifier`, `new_ref_identifier`

The domain is not updated.

:Returns:

    out : str
        The new identifier.

:Examples:

>>> d._axes_sizes.keys()
['dim2', 'dim0']
>>> d.new_axis_identifier()
'dim3'

>>> d._axes_sizes.keys()
[]
>>> d.new_axis_identifier()
'dim0'

'''
        dimensions = self._axes_sizes

        n = len(dimensions)
        new_key = 'dim%d' % n

        while new_key in dimensions:
            n += 1
            new_key = 'dim%d' % n
        #--- End: while

        return new_key
    #--- End: def

    def new_aux_identifier(self):
        '''

Return a new, unique auxiliary coordinate identifier for the domain.

.. seealso:: `new_measure_identifier`, `new_dimemsion_identifier`,
             `new_ref_identifier`

The domain is not updated.

:Returns:

    out : str
        The new identifier.

:Examples:

>>> d.items(role='a').keys()
['aux2', 'aux0']
>>> d.new_aux_identifier()
'aux3'

>>> d.items(role='a').keys()
[]
>>> d.new_aux_identifier()
'aux0'

'''
        keys = self.a

        n = len(keys)
        new_key = 'aux%d' % n

        while new_key in keys:
            n += 1
            new_key = 'aux%d' % n
        #--- End: while

        return new_key
    #--- End: def

    def new_measure_identifier(self):
        '''

Return a new, unique cell measure identifier for the domain.

The domain is not updated.

.. seealso:: `new_aux_identifier`, `new_axis_identifier`,
             `new_ref_identifier`

:Returns:

    out : str
        The new identifier.

:Examples:

>>> d.items(role='m').keys()
['msr2', 'msr0']
>>> d.new_measure_identifier()
'msr3'

>>> d.items(role='m').keys()
[]
>>> d.new_measure_identifier()
'msr0'


'''
        keys = self.m

        n = len(keys)
        new_key = 'msr%d' % n

        while new_key in keys:
            n += 1
            new_key = 'msr%d' % n
        #--- End: while

        return new_key
    #--- End: def

    def new_ref_identifier(self):
        '''

Return a new, unique coordinate reference identifier for the domain.

The domain is not updated.

.. seealso:: `new_aux_identifier`, `new_axis_identifier`,
             `new_measure_identifier`

:Returns:

    out : str
        The new identifier.

:Examples:

>>> d.items(role='r').keys()
['ref1']
>>> d.new_ref_identifier()
'ref2'

>>> d.items(role='r').keys()
[]
>>> d.new_ref_identifier()
'ref0'

'''
        if not self.r:
            return 'ref0'
        
        keys = self.r

        n = len(keys)
        new_key = 'ref%d' % n

        while new_key in keys:
            n += 1
            new_key = 'ref%d' % n
        #--- End: while

        return new_key
    #--- End: def

    def insert_coord(self, variable, key, copy=True, axes=None):
        '''

Insert a dimension coordinate or auxiliary coordinate into the domain
in place.

:Parameters:

    variable : cf.AuxiliaryCoordinate or cf.DimensionCoordinate or cf.Coordinate
        The new dimension coordinate or auxiliary coordinate. If
        required, it will be converted to the appropiate object type
        (dimension coordinate or auxiliary).

    key : str
        The identifier for the new coordinate. The identifier must
        start with the string ``dim`` or ``aux``, corresponding to
        whether the *variable* is to be a dimension coordinate or an
        auxiliary coordinate respectively.

    axes : list, optional
        If the *variable* is an auxiliary coordinate then the
        identities of its dimensions must be provided. Ignored if the
        *variable* is a dimension coordinate.

    copy: bool, optional
        If False then the *variable* is not copied before
        insertion. By default it is copied.

:Returns:

    None

:Examples:

>>>

'''
        if key.startswith('d'):
            self.insert_dim(variable, key=key, copy=copy)
            
        elif key.startswith('a'):
            self.insert_aux(variable, key=key, axes=axes, copy=copy)

        else:
            raise ValueError("bad key in insert_coord: %r" % key)
    #--- End: def

    def insert_dim(self, item, key=None, axis=None, copy=True, replace=True):
        '''

Insert a dimension coordinate to the domain in place.

:Parameters:

    item: cf.DimensionCoordinate or cf.Coordinate or cf.AuxiliaryCoordinate
        The new coordinate. If not a dimension coordinate object then
        it will be converted to one.

    axis : str, optional

    key : str, optional
        The identifier for the new dimension coordinate. The
        identifier is of the form ``'dimN'`` where the ``N`` part
        should be replaced by an arbitrary integer greater then or
        equal to zero. By default a unique identifier will be
        generated.

    copy: bool, optional
        If False then the dimension coordinate is not copied before
        insertion. By default it is copied.
      
    replace : bool, optional
        If False then do not replace an existing dimension coordinate
        with the same identifier. By default an existing dimension
        coordinate with the same identifier is replaced with *coord*.
    
:Returns:

    out : str
        The identifier for the new dimension coordinate (see the *key*
        parameter).

:Examples:

>>>

'''
        item = item.asdimension(copy=copy)            

        if key is None:
            key = axis            
        elif axis is not None and key != axis:
            raise ValueError("Incompatible key and axis parameters: %r, %r" %
                             (key, axis))                       

        if key is None:
            key = self.insert_axis(item.size)
        else:
            if key in self.d and not replace:
                raise ValueError(
"Can't insert dimension coordinate object: replace=%s and %r identifier already exists" %
(replace, key))

            self.insert_axis(item.size, key, replace=False)
        #--- End: if

        dimensions = self._axes

        dimensions[key] = [key]

        # ------------------------------------------------------------
        # Turn a scalar dimension coordinate into size 1, 1-d
        # ------------------------------------------------------------
        if item.isscalar:
            item.expand_dims(0, i=True)

        self.d[key] = item

        self._map[key] = 'd'

        refs = self.r
        if refs:
            for ref in refs.itervalues():
                self._conform_ref(ref)

        return key
    #--- End: def

    def _insert_item(self, variable, key, role, axes=None, copy=True,
                     replace=True):
        '''

Insert a new auxiliary coordinate into the domain in place, preserving
internal consistency.

:Parameters:

    coord :cf.Coordinate
        The new auxiliary coordinate.

    key : str
        The identifier for the auxiliary coordinate or cell
        measure.

    role : str

    axes : sequence, optional
        The ordered axes of the new coordinate. Ignored if the
        coordinate is a dimension coordinate. Required if the
        coordinate is an auxiliary coordinate.

    copy: bool, optional
        If False then the auxiliary coordinate is not copied before
        insertion. By default it is copied.

    replace : bool, optional
        If False then do not replace an existing dimension coordinate
        with the same identifier. By default an existing dimension
        coordinate with the same identifier is replaced with *coord*.

:Returns:

    out : str
        The identifier for the new auxiliary coordinate (see the 'key'
        parameter).


:Examples:

>>>

'''
        if key in self._axes and not replace:
            raise ValueError(
                "Can't insert %s: %r identifier already exists" %
                (role, key))

        ndim = variable.ndim
        if not ndim:
            ndim = 1

        if axes is None:
            # --------------------------------------------------------
            # The axes have not been set => infer the axes.
            # --------------------------------------------------------
            variable_shape = variable.shape
            if (not variable_shape or 
                len(variable_shape) != len(set(variable_shape))):
                raise ValueError(
"Ambiguous %s shape: %s. Consider setting the axes parameter." %
(variable.__class__.__name__, variable_shape))

            axes = []
            axes_sizes = self._axes_sizes.values()
            for n in variable_shape:
                if axes_sizes.count(n) == 1:
                    axes.append(self.axis(size=n))
                else:
                    raise ValueError(
"Ambiguous %s shape: %s. Consider setting the axes parameter." %
(variable.__class__.__name__, variable_shape))
            #--- End: for

        else:
            # Axes have been provided
            axes = self.axes(axes, ordered=True)

            if len(set(axes)) != ndim:
                raise ValueError(
                    "Can't insert %s: Mismatched number of axes (%d != %d)" % 
                    (role, len(set(axes)), ndim))

            aux_axes = []                
            for axis, size in izip_longest(axes, variable.shape, fillvalue=1):
                axis_size = self.axis_size(axis)
                if size != axis_size:
                    raise ValueError(
                        "Can't insert %s: Mismatched axis size (%d != %d)" % 
                        (role, size, axis_size))

                aux_axes.append(axis)
            #--- End: for
            axes = aux_axes
        #--- End: if

        n_axes = len(set(axes))
        if not (ndim == n_axes or (ndim == 0 and n_axes == 1)):
            raise ValueError(
                "Can't insert %s: Mismatched number of axes (%d != %d)" % 
                (role, n_axes, ndim))

        self._axes[key] = axes

        if not variable.ndim:
            # Turn a scalar item into size 1, 1-d, copying it
            # required.
            variable = variable.expand_dims(0, i=(not copy))
        elif copy:
            # Copy the variable
            variable = variable.copy()

        return variable
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

    def items(self, items=None, role=None, axes=None, axes_all=None,
              axes_subset=None, axes_superset=None, ndim=None,
              match_and=True, exact=False, inverse=False, copy=False,
              strict_axes=False, _restrict_inverse=False):
        '''

Return items of the domain.

.. seealso:: `axes`, `item`, `remove_items`

:Parameters:

    {+items}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+exact}

    {+match_and}

    {+inverse}

    {+copy}

:Returns:

    out : dict
        A dictionary whose keys are domain item identifiers with
        corresponding values of items of the domain. The dictionary
        may be empty.

:Examples:

See `cf.Field.items`.

All of these examples are for the same domain, whose complete
dictionary of items is shown in the first example.

>>> d.items()
{{'dim0': <CF DimensionCoordinate: grid_latitude(111) degrees>,
 'dim1': <CF DimensionCoordinate: grid_longitude(106) degrees>,
 'dim2': <CF DimensionCoordinate: time(12) days since 1997-1-1>,
 'aux0': <CF AuxiliaryCoordinate: longitude(111, 106) degrees_E>,
 'aux1': <CF AuxiliaryCoordinate: latitude(111, 106) degrees_N>,
 'aux2': <CF AuxiliaryCoordinate: forecast_reference_time(12) days since 1997-1-1>
 'msr0': <CF CellMeasure: area(111, 106) m2>,
 'ref0': <CF CoordinateReference: rotated_latitude_longitude>}}

>>> d.items(axes='grid_latitude')
{{'dim0': <CF DimensionCoordinate: grid_latitude(111) degrees>,
 'aux0': <CF AuxiliaryCoordinate: longitude(111, 106) degrees_E>,
 'aux1': <CF AuxiliaryCoordinate: latitude(111, 106)> degrees_N,
 'msr0': <CF CellMeasure: area(111, 106) m2>}}
>>> d.items(axes='grid_latitude', ndim=1)
{{'dim0': <CF DimensionCoordinate: grid_latitude(111) degrees>}}
>>> d.items(axes='grid_latitude', strict_axes=True)
{{'dim0': <CF DimensionCoordinate: grid_latitude(111) degrees>}}

>>> d.items(axes='time')
{{'dim2': <CF DimensionCoordinate: time(12) days since 1997-1-1>,
 'aux2': <CF AuxiliaryCoordinate: forecast_reference_time(12) days since 1997-1-1>}}
>>> d.items(axes='time', role='d')
{{'dim2': <CF DimensionCoordinate: time(12) days since 1997-1-1>}}

>>> d.items(axes='area')
{{'aux0': <CF AuxiliaryCoordinate: longitude(111, 106) degrees_E>,
 'aux1': <CF AuxiliaryCoordinate: latitude(111, 106) degrees_N>,
 'msr0': <CF CellMeasure: area(111, 106) m2>}}
>>> d.items(axes=['grid_latitude', 'grid_longitude'])
{{'aux0': <CF AuxiliaryCoordinate: longitude(111, 106) degrees_E>,
 'aux1': <CF AuxiliaryCoordinate: latitude(111, 106) degrees_N>,
 'msr0': <CF CellMeasure: area(111, 106) m2>}}

>>> d.items('grid')
{{'dim0': <CF DimensionCoordinate: grid_latitude(111) degrees>,
 'dim1': <CF DimensionCoordinate: grid_longitude(106) degrees>}}
>>> d.items('grid', exact=True)
{{}}

>>> d.items({{'units': 'degrees_E'}})
{{'dim0': <CF DimensionCoordinate: grid_latitude(111) degrees>,
 'dim1': <CF DimensionCoordinate: grid_longitude(106) degrees>,
 'aux0': <CF AuxiliaryCoordinate: longitude(111, 106) degrees_E>,
 'aux1': <CF AuxiliaryCoordinate: latitude(111, 106)> degrees_N}}
>>> d.items({{'units': 'degrees_E'}}, exact=True)
{{'aux0': <CF AuxiliaryCoordinate: longitude(111, 106) degrees_E>}}

>>> d.items({{'units': 'radians', 'standard_name': 'time'}})
{{}}
>>> d.items({{'units': 'radians', 'standard_name': 'time'}}, maximal_match=False)
{{'dim0': <CF DimensionCoordinate: grid_latitude(111) degrees>,
 'dim1': <CF DimensionCoordinate: grid_longitude(106) degrees>,
 'dim2': <CF DimensionCoordinate: time(12) days since 1997-1-1>,
 'aux0': <CF AuxiliaryCoordinate: longitude(111, 106) degrees_E>,
 'aux1': <CF AuxiliaryCoordinate: latitude(111, 106)> degrees_N}}
>>> d.items({{'units': 'radians', 'standard_name': 'time'}}, maximal_match=False, exact=True)
{{'dim2': <CF DimensionCoordinate: time(12) days since 1997-1-1>}}

>>> set(d.items(role='da')) == set(d.items(role='ct', inverse=True))
True

'''
        if strict_axes:
            axes_all = axes
            print "WARNING: strict_axes has been deprecated. Replace the axes parameter with the axes_all parameter instead."

        pool = {}
        for r in ('d', 'a', 'm', 'r'):
            pool.update(getattr(self, r))

        if inverse:  
            if not _restrict_inverse or role is None:
                master = pool.copy()
            else:
                master = {}                    
                for r in role:
                    master.update(getattr(self, r))
        #--- End: if

        if items is None and axes is None and role is None and ndim is None:
            out = pool.copy()
        else:            
            out = {}

        if pool and role is not None:
            # --------------------------------------------------------
            # Select items which have a given role
            # --------------------------------------------------------
            out = {}
            for r in role:
                out.update(getattr(self, r))

            if match_and:
                pool = out
            else:
                for key in out:
                    del pool[key]
        #--- End: if

        if pool and axes is not None:
            # --------------------------------------------------------
            # Select items which span at least one of the given axes,
            # and possibly others.
            # --------------------------------------------------------
            axes_out = {}
            if not isinstance(axes, dict):
                axes = {'axes': axes}

            axes_tmp = self.axes(**axes)
            if axes_tmp:
                domain_axes = self._axes
                for key, value in pool.iteritems():
                    if axes_tmp.intersection(domain_axes.get(key, ())):
                        axes_out[key] = value
            #--- End: if

            if match_and:
                out = pool = axes_out
            else:                
                for key in axes_out:
                    out[key] = pool.pop(key)
        #--- End: if

        if pool and axes_subset is not None:
            # --------------------------------------------------------
            # Select items whose data array spans all of the specified
            # axes, taken in any order, and possibly others.
            # --------------------------------------------------------
            axes_out = {}
            if not isinstance(axes_subset, dict):
                axes_subset = {'axes': axes_subset}

            axes_tmp = self.axes(**axes_subset)
            if axes_tmp:
                domain_axes = self._axes                                    
                for key, value in pool.iteritems():
                    if axes_tmp.issubset(domain_axes.get(key, ())):
                        axes_out[key] = value                            
            #--- End: if

            if match_and:
                out = pool = axes_out
            else:                
                for key in axes_out:
                    out[key] = pool.pop(key)
        #--- End: if

        if pool and axes_superset is not None:
            # --------------------------------------------------------
            # Select items whose data array spans a subset of the
            # specified axes, taken in any order, and no others.
            # --------------------------------------------------------
            axes_out = {}
            if not isinstance(axes_superset, dict):
                axes_superset = {'axes': axes_superset}

            axes_tmp = self.axes(**axes_superset)
            if axes_tmp:
                domain_axes = self._axes                                    
                for key, value in pool.iteritems():
                    if axes_tmp.issuperset(domain_axes.get(key, (None,))):
                        axes_out[key] = value                            
            #--- End: if

            if match_and:
                out = pool = axes_out
            else:                
                for key in axes_out:
                    out[key] = pool.pop(key)
        #--- End: if

        if pool and axes_all is not None:
            # --------------------------------------------------------
            # Select items which span all of the given axes and no
            # others
            # --------------------------------------------------------
            axes_out = {}
            if not isinstance(axes_all, dict):
                axes_all = {'axes': axes_all}

            axes_tmp = self.axes(**axes_all)
            if axes_tmp:
                domain_axes = self._axes                                    
                for key, value in pool.iteritems():
                    if axes_tmp == set(domain_axes.get(key, ())):
                        axes_out[key] = value                            
            #--- End: if

            if match_and:
                out = pool = axes_out
            else:                
                for key in axes_out:
                    out[key] = pool.pop(key)
        #--- End: if
                    
        if pool and ndim is not None:
            # --------------------------------------------------------
            # Select items whose number of data array axes satisfies a
            # condition
            # --------------------------------------------------------
            domain_axes = self._axes
            
            ndim_out = {}
            for key, item in pool.iteritems():
                if ndim == len(domain_axes.get(key, ())):
                    ndim_out[key] = item
            #--- End: for

            if match_and:                
                out = pool = ndim_out
            else:
                for key in ndim_out:
                    out[key] = pool.pop(key)
        #--- End: if

        if pool and items is not None:
            # --------------------------------------------------------
            # Select items whose properties satisfy conditions
            # --------------------------------------------------------
            items_out = {}

            if isinstance(items, (basestring, dict, Query)):
                items = (items,)

            if items:
                pool2 = pool.copy()

                match = []
                for m in items:
                    if m.__hash__ and m in pool:
                        # m is a domain item identifier
                        items_out[m] = pool2.pop(m)
                    else:                    
                        match.append(m)
                #--- End: for

                if match and pool:                
                    for key, item in pool2.iteritems():
                        if item.match(match, exact=exact):
                            # This item matches the critieria
                            items_out[key] = item
                #--- End: if

                if match_and:                
                    out = pool = items_out
                else:
                    for key in items_out:
                        out[key] = pool.pop(key)
            #--- End: if
        #--- End: if

        if inverse:
            # --------------------------------------------------------
            # Select items other than those previously selected
            # --------------------------------------------------------
            for key in out:
                del master[key]
                                
            out = master
        #--- End: if

        if copy:
            # --------------------------------------------------------
            # Copy the items
            # --------------------------------------------------------
            out2 = {}
            for key, item in out.iteritems():
                out2[key] = item.copy()
                
            out = out2
        #--- End: if

        # ------------------------------------------------------------
        # Return the selected items
        # ------------------------------------------------------------
        return out
    #--- End: def

    def ref_axes(self, key):
        '''Return the axes spanned by the coordinate object inputs of a
coordinate reference object.

:Parameters:

    key : str
        A coordinate reference domain identifier.
        
          *Example:*
            To select the coordinate reference with domain identifier
            "ref1": ``key='ref1'``.

:Returns:

    out : set
        A set of the domain identifiers of the axes spanned by the
        coordinate reference's coordinates.

:Examples:

>>> key = d.item('rotated_latitude_longitude', key=True)
>>> d.ref_axes(key)
set(['dim2', 'dim1'])

        '''
        axes = self._axes

        raxes = []
        for ckey in self.r[key].coords:
            raxes.extend(axes.get(ckey, ()))

        return set(raxes)
    #--- End: def

    def insert_aux(self, item, key=None, axes=None, copy=True, replace=True):
        '''

Insert a auxiliary coordinate into the domain in place.

:Parameters:

    coord : cf.AuxiliaryCoordinate or cf.Coordinate or cf.DimensionCoordinate 
        The new coordinate. If not an auxiliary coordinate object then
        it will be converted to one.

    key : str, optional
        The identifier for the new dimension coordinate. The
        identifier is of the form ``'auxN'`` where the ``N`` part
        should be replaced by an arbitrary integer greater then or
        equal to zero. By default a unique identifier will be
        generated.

    axes : list, optional
        The ordered axes of the new coordinate. Ignored if the
        coordinate is a dimension coordinate. Required if the
        coordinate is an auxiliary coordinate.

    copy: bool, optional
        If False then the auxiliary coordinate is not copied before
        insertion. By default it is copied.

    replace : bool, optional
        If False then do not replace an existing auxiliary coordinate
        with the same identifier. By default an existing auxiliary
        coordinate with the same identifier is replaced with *coord*.

:Returns:

    out : str
        The identifier for the new auxiliary coordinate (see the *key*
        parameter).


:Examples:

>>>

'''
        item = item.asauxiliary(copy=copy)

        if not key:
            key = self.new_aux_identifier()

        item = self._insert_item(item, key, 'auxiliary coordinate', axes=axes,
                                 copy=False)

        self.a[key] = item

        self._map[key] = 'a'

        refs = self.r
        if refs:
            for ref in refs.itervalues():
                self._conform_ref(ref)

        return key
    #--- End: def

    def insert_measure(self, item, key=None, axes=None, copy=True, replace=True):
        '''Insert a cell measure into the domain in place.

:Parameters:

    item : cf.CellMeasure
        The new cell measure.

    key : str, optional
        The identifier for the new cell measure. The identifier is of
        the form ``'msrN'`` where the ``N`` part should be replaced by
        an arbitrary integer greater then or equal to zero. By default
        a unique identifier will be generated.

    axes : sequence, optional
        The ordered axes of the new cell measure.

    copy : bool, optional
        If False then the cell measure is not copied before
        insertion. By default it is copied.

    replace : bool, optional
        If False then do not replace an existing cell measure with the
        same identifier. By default an existing cell measure with the
        same identifier is replaced with *item*.

:Returns:

    out : str
        The identifier for the new cell measure (see the *key*
        parameter).

:Examples:

>>>

        '''
        if key is None:
            key = self.new_measure_identifier()

        item = self._insert_item(item, key, 'cell measure', axes=axes, copy=copy)

        self.m[key] = item

        self._map[key] = 'm'

        return key
    #--- End: def

    def insert_ref(self, item, key=None, copy=True, replace=False):
        '''

Insert a coordinate reference object into the domain in place.

:Parameters:

    item : cf.CoordinateReference
        The new coordinate reference object.

    key : str, optional
        The identifier for the new coordinate reference object. By default a
        unique identifier will be generated.

    copy : bool, optional
        If False then the coordinate reference object is not copied before
        insertion. By default it is copied.

    replace : bool, optional
        If True then replace an existing coordinate reference object with the
        same identifier. By default an exception is raised if there is
        an existing coordinate reference object with the same identifier.

:Returns:

    out : str
        The internal identifier of the new coordinate reference object.

:Examples:

>>>

'''
        if key is None:
            key = self.new_ref_identifier()
        elif not replace and key in self.r:
            raise ValueError(
"Can't insert coordinate reference object: replace=%s and %r identifier already exists" %
(replace, key))
        
        if copy:
            item = item.copy()

        self._conform_ref(item)

        self.r[key] = item

        self._map[key] = 'r'

        return key
    #--- End: def

    def remove_axes(self,  axes=None, **kwargs):
        '''

Remove and return axes from the domain.

This method has exactly the same interface, functionality and outputs
as `cf.Field.remove_axes`. Therefore see `cf.Field.remove_axes` for
the full documentation details.

.. seealso:: `axes`, `remove_axis`, `remove_item`, `remove_items`

:Parameters:

    axes, kwargs : *optional*
        See `cf.Field.remove_axes`.

:Returns:

    out : set
        The removed axes. The set may be empty.

:Examples:

See `cf.Field.remove_axes`.

'''
        d = self

        # ------------------------------------------------------------
        # Find the domain axis identifiers
        # ------------------------------------------------------------
        axes = d.axes(axes, **kwargs)
        if not axes:
            return set()

        if axes.intersection(d._axes.get('data', ())):
            raise ValueError(
                "Can't remove an axis which is spanned by the data array")

        axes_sizes = d._axes_sizes

        for axis in axes:
            if (axes_sizes[axis] > 1 and
                d.items(role=('d', 'a', 'm'), ndim=gt(1), axes=axis)):
                raise ValueError(
"Can't remove an axis with size > 1 which is spanned by a multidimensional item")
        #--- End: for

        items = d.items(role=('d', 'a', 'm'), axes=axes)
        for key, item in items.iteritems():
            item_axes = d._axes[key]

            # Remove the item if it only spans removed axes
            if axes.issuperset(item_axes):
                d.remove_item(key)
                continue

            # Still here? Then squeeze removed axes from the
            # multidimensional item.
            iaxes = [item_axes.index(axis) for axis in axes
                     if axis in item_axes]
            item.squeeze(iaxes, i=True)
#            item.squeeze(axes.intersection(item_axes))
#            if not item.ndim:
#                # Remove the multidimensional item if it doesn't span
#                # any axes after being squeezed
#                d.remove_item(key)
#            else:

            # Remove the removed axes from the multidimensional item's
            # list of axes
            for axis in axes.intersection(item_axes):
                item_axes.remove(axis)
                ##--- End: for
                #if not item_axes:  
                #    # Remove the item if it doesn't span any axes
                #    # after being squeezed
                #    d.remove_item(key)
        #--- End: for

        # ------------------------------------------------------------
        # Remove the axes
        # ------------------------------------------------------------
        for axis in axes:
            del axes_sizes[axis]

        return axes
    #--- End: def

    def remove_axis(self, axes=None, **kwargs):
        '''

Remove and return an axis from the domain.

This method has exactly the same interface, functionality and outputs
as `cf.Field.remove_axis`. Therefore see `cf.Field.remove_axis` for
the full documentation details.

.. seealso:: `axis`, `remove_axes`, `remove_item`, `remove_items`

:Parameters:

    axes, kwargs : *optional*
        See `cf.Field.remove_axis`.

:Returns:

    out : 
        The domain identifier of the removed axis, or None if there
        isn't one.

:Examples:

See `cf.Field.remove_axis`.

'''
        axis = self.axis(axes, **kwargs)
        if axis is None:
            return

        return self.remove_axes(axis).pop()
    #--- End: def

    def remove_item(self, items=None, key=False, **kwargs):
        '''

Remove and return an item from the domain.

This method has exactly the same interface, functionality and outputs
as `cf.Field.remove_item`. Therefore see `cf.Field.remove_item` for
the full documentation details.

.. seealso:: `item`, `remove_axes`, `remove_axis`, `remove_items`

:Parameters:

    items, kwargs : *optional*
        See `cf.Field.remove_item`.

:Returns:

    out : 
        The removed item, or None if no unique item could be found.

:Examples:

See `cf.Field.remove_item`.

>>> d.items()
{'dim0': <CF DimensionCoordinate: grid_latitude(111) degrees>,
 'dim1': <CF DimensionCoordinate: grid_longitude(106) degrees>,
 'dim2': <CF DimensionCoordinate: time(12) days since 1997-1-1>,
 'aux0': <CF AuxiliaryCoordinate: longitude(111, 106) degrees_E>,
 'aux1': <CF AuxiliaryCoordinate: latitude(111, 106) degrees_N>,
 'aux2': <CF AuxiliaryCoordinate: forecast_reference_time(12) days since 1997-1-1>
 'msr0': <CF CellMeasure: area(111, 106) m2>,
 'ref0': <CF CoordinateReference: rotated_latitude_longitude>}
>>> d.remove_item('grid_long')
>>> d.remove_item('aux1')
>>> d.remove_item('T')
>>> d.remove_item('longitude', role='a', exact=True)
>>> d.remove_item('rotated_latitude_longitude')
>>> d.remove_item({None: 'area', 'units': 'km2'})
>>> d.items()
{'dim0': <CF DimensionCoordinate: grid_latitude(111) degrees>}

'''
        items = self.items(items, **kwargs)
        if not items:
            return

        item_key = items.popitem()[0]
        if items:
            return

        items = self.remove_items(item_key).popitem()
        if key:
            return items[0]
        else:
            return items[1]
    #--- End: def

    def remove_items(self, items=None, **kwargs):
        '''Remove and return items from the domain.

This method has exactly the same interface, functionality and outputs
as `cf.Field.remove_items`. Therefore see `cf.Field.remove_items` for
the full documentation details.

.. seealso:: `items`, `remove_axes`, `remove_axis`, `remove_item`

:Parameters:

    items, kwargs : *optional*
        See `cf.Field.remove_items`.

:Returns:

    out : dict
        A dictionary whose keys are domain item identifiers with
        corresponding values of the removed items of the domain. The
        dictionary may be empty.

:Examples:

See `cf.Field.remove_items`.

        '''
        out = {}
        for key, item in self.items(items, **kwargs).iteritems():
            x = self._map[key]
            
            # If the removed item is a dimension of auxiliary
            # coordinate then .....
            if x in 'da':
                self._replace_refs_coord_identifier(key)
                
            del self._map[key]
      
            self._axes.pop(key, None)

            del getattr(self, x)[key]

            out[key] = item
        #--- End: if        

        return out
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
        X = type(self)
        new = X.__new__(X)

        new._axes = {}
        for key, value in self._axes.iteritems():
            new._axes[key] = value[:]
            
        new._axes_sizes = self._axes_sizes.copy()

        new._map = self._map.copy()

        new.d = {}
        for key, value in self.d.iteritems():
            new.d[key] = value.copy()

        new.a = {}
        for key, value in self.a.iteritems():
            new.a[key] = value.copy()

        new.m = {}
        for key, value in self.m.iteritems():
            new.m[key] = value.copy()

        new.r = {}
        for key, value in self.r.iteritems():
            new.r[key] = value.copy()

        nc_dimensions = getattr(self, 'nc_dimensions', None)
        if nc_dimensions:            
            new.nc_dimensions = nc_dimensions.copy()
        else:
            new.nc_dimensions = {}

        return new
    #--- End: def

    def close(self):
        '''

Close all referenced open data files.

:Returns:

    None

:Examples:

>>> d.close()

'''
        for item in self.items().itervalues():
            item.close()
    #--- End: def

    def item(self, items=None, key=False, **kwargs):
        '''

Return an item of the domain, or its domain identifier.

This method has exactly the same interface, functionality and outputs
as `cf.Field.item`. Therefore see `cf.Field.item` for the full
documentation details.

.. seealso:: `axis`, `items`, `remove_item`

:Parameters:

    items, kwargs : *optional*
        See `cf.Field.item`.

    key : bool, option
        See `cf.Field.item`.

:Returns:

    out : 
        See `cf.Field.item`.
     
:Examples:

See `cf.Field.items`.

The following examples are base on the following domain:

>>> d.items()
{'dim0': <CF DimensionCoordinate: grid_latitude(73)
 'dim1': <CF DimensionCoordinate: grid_longitude(96)>,
 'dim2': <CF DimensionCoordinate: time(12)>,
 'aux0': <CF AuxiliaryCoordinate: latitude(73, 96)>,
 'aux1': <CF AuxiliaryCoordinate: longitude(73, 96)>,
 'msr0':  <CF CellMeasure: area(96, 73)>,
 'ref0': <CF CoordinateReference: rotated_latitude_longitude>}

>>> d.item('longitude')
<CF DimensionCoordinate: longitude(360)>
>>> d.item('long')
<CF DimensionCoordinate: longitude(360)>
>>> d.item('long', key=True)
'dim2'

>>> d.item('lon', exact=True)
None
>>> d.item('longitude', exact=True)
<CF DimensionCoordinate: longitude(360)>

>>> d.item('msr0')
<CF CellMeasure: area(96, 73)>

>>> d.item({'units': 'degrees'})
None
>>> d.item({'units': 'degreeN'})
<CF AuxiliaryCoordinate: latitude(73, 96)>

>>> d.item(axes='time')
<CF DimensionCoordinate: time(12)>
>>> d.item(axes='grid_latitude')
None
>>> d.item(axes='grid_latitude', strict_axes=True)
<CF DimensionCoordinate: grid_latitude(73)
>>> d.item(axes='grid_longitude', ndim=1, key=True)
'dim1'

'''    
        d = self.items(items, **kwargs)
        if not d:
            return

        items = d.popitem()

        if d:
            return

        if key:
            return items[0]
        else:
            return items[1]
    #--- End: def

    def items_axes(self, items=None, **kwargs):
        '''

Return the axes of a domain item.

This method has exactly the same interface, functionality and outputs
as `cf.Field.item_axes`. Therefore see `cf.Field.item_axes` for the
full documentation details.

.. seealso:: `axes`, `data_axes`, `item`

:Parameters:

    item, kwargs : *optional*
         See `cf.Field.item_axes`.

:Returns:

    out : list or None
        The ordered list of axes for the item or, if there is no
        unique item or the item is a coordinate reference, then None is returned.
       
:Examples:

See `cf.Field.item_axes`.

'''   
        kwargs.setdefault('role', ('d', 'a', 'm'))    
        keys = self.items(items, **kwargs).keys()

        _items_axes = self._axes

        out = {}
        for key in keys:
            out[key] = _items_axes[key][:]

        return out
    #--- End: def

    def item_axes(self, items=None, **kwargs):
        '''

Return the axes of a domain item.

This method has exactly the same interface, functionality and outputs
as `cf.Field.item_axes`. Therefore see `cf.Field.item_axes` for the
full documentation details.

.. seealso:: `axes`, `data_axes`, `item`

:Parameters:

    items, kwargs : *optional*
         See `cf.Field.item_axes`.

:Returns:

    out : list or None
        The ordered list of axes for the item or, if there is no
        unique item or the item is a coordinate reference, then None is returned.
       
:Examples:

See `cf.Field.item_axes`.

'''    
        kwargs['key'] = True
        key = self.item(items, **kwargs)

        if key is not None and self._map[key] != 'r':
            return self._axes[key][:]
    #--- End: def

    def data_axes(self):
        '''

Return the axes of the field's data array.

This method has exactly the same interface, functionality and outputs
as `cf.Field.data_axes`. Therefore see `cf.Field.data_axes` for the
full documentation details.

.. seealso:: `axes`, `item_axes`

:Returns:

    out : list or None
        The ordered axes of the field's data array. If there is no
        data array then None is returned.
       
:Examples:

See `cf.Field.data_axes`.

'''    
        axes = self._axes.get('data', None)
        if axes is not None:
            return axes[:]
    #--- End: def

    def axes(self, axes=None, size=None, ordered=False, **kwargs):
        '''

Return domain axis identifiers.

This method has exactly the same interface, functionality and outputs
as `cf.Field.axes`.

See `cf.Field.axes` for details.

.. seealso:: `axis`, `items`, `remove_axes`

:Parameters:

    axes, kwargs: *optional*
        See `cf.Field.axes`.

    size : int or cf.Query, optional
        See `cf.Field.axes`.

    ordered : bool, optional
        See `cf.Field.axes`.

:Returns:

    out : set or list
        A set of domain axis identifiers, or a list if *ordered* is
        True. The set or list may be empty.

:Examples:

See `cf.Field.axes`.

'''
        def _axes(self, axes, size, item_axes, axes_sizes, kwargs):

            a = None

            if axes is not None:
                if axes.__hash__:
                    if isinstance(axes, slice):
                        try:
                            a = tuple(item_axes.get('data', ())[axes])
                        except IndexError:
                            a = ()
                    elif axes in axes_sizes:
                        # --------------------------------------------
                        # axes is a domain axis identifier
                        # --------------------------------------------
                        a = (axes,)
                    elif axes in item_axes and not kwargs:
                        # --------------------------------------------
                        # axes is a domain item identifier
                        # --------------------------------------------
                        a = item_axes[axes]
                    elif isinstance(axes, slice):
                        # --------------------------------------------
                        # axes is a slice object
                        # --------------------------------------------
                        a = item_axes.get('data', ())[axes]
                    else:
                        # --------------------------------------------
                        # See if axes is an integer
                        # --------------------------------------------
                        try:
                            a = (item_axes.get('data', ())[axes],)
                        except IndexError:
                            a = ()
                        except TypeError:
                            pass
                #--- End: if
 
            elif not kwargs:
                a = tuple(axes_sizes)
            #--- End: if

            if a is None:
                # ----------------------------------------------------
                # Assume that axes is a value accepted by the items
                # method
                # ----------------------------------------------------
                a = [] 
                for key in self.items(axes, **kwargs):                
                    a += item_axes.get(key, ())
            #--- End: if

            if size:
                a = [axis for axis in a if size == axes_sizes[axis]]

            return a
        #--- End: def

        if kwargs:
            kwargs['axes'] = None

        item_axes  = self._axes
        axes_sizes = self._axes_sizes

        if axes is None or isinstance(axes, (basestring, dict, slice, int, long)):
            # --------------------------------------------------------
            # axes is not a sequence or a set
            # --------------------------------------------------------
            a = _axes(self, axes, size, item_axes, axes_sizes, kwargs)
        else:   
            # --------------------------------------------------------
            # axes is a sequence or a set
            # --------------------------------------------------------
            a = []
            for x in axes:
                a += _axes(self, x, size, item_axes, axes_sizes, kwargs)
        #--- End: if

        if not ordered:
            return set(a)
        else:
            return list(a)
    #--- End: def
        
    def axis(self, axes=None, size=None, **kwargs):
        '''

Return a domain axis identifier.

The axis may be selected with the keyword arguments. When multiple
criteria are given, the axis will be the intersection of the
selections. If no unique axis can be found then None is returned.

.. seealso:: `axes`, `item`, `items`, `remove_item`

:Parameters:

    {+axes, kwargs}

:Returns:

    out : str
        The unique domain axis identifier. If there isn't a unique
        axis then None is returned.

:Examples:

'''
        axes = self.axes(axes, size=size, **kwargs)
        if not axes:
            return

        axis = axes.pop()

        if not axes:
            return axis
        else:
            return
    #--- End: def

    def axes_sizes(self, axes=None, size=None, key=False, **kwargs):
        '''
'''
        out = {}
        
        axes = self.axes(axes, size=size, **kwargs)

        for axis in axes:
            out[axis] = self._axes_sizes[axis]
                
        if not key:
            out2 = {}
            for axis, size in out.iteritems():
                out2[self.axis_name(axis)] = size

            return out2
        #--- End: if

        return out
    #--- End: def

    def axis_size(self,  axes=None, **kwargs):
        '''
'''
        axis = self.axis(axes, **kwargs)
        if axis is None:
            return None

        return self._axes_sizes[axis]
    #--- End: def

    def expand_dims(self, coord=None, size=1, copy=True):
        '''

Expand the domain with a new dimension in place.

The new dimension may by of any size greater then 0.

:Parameters:

    coord : cf.Coordinate, optional
        A dimension coordinate for the new dimension. The new
        dimension's size is set to the size of the coordinate's array.

    size : int, optional
        The size of the new dimension. By default a dimension of size
        1 is introduced. Ignored if *coord* is set.

:Returns:

    None

:Examples:

>>> d.expand_dims()
>>> d.expand_dims(size=12)
>>> c
<CF DimensionCoordinate: >
>>> d.expand_dims(coord=c)

'''
        if coord:            
            self.insert_dim(coord, copy=copy)
        else:
            self.insert_axis(size)
    #--- End: def

    def dump_axes(self, display=True, _level=0):
        '''
        
Return a string containing a description of the domain.

:Parameters:

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed.

:Returns:

    out : str
        A string containing the description.

:Examples:

'''
        indent1 = '    ' * _level
        indent2 = '    ' * (_level+1)

        string = ['%sAxes:' % indent1]
        
        data_axes = self._axes.get('data', ())
        w = sorted(["{0}{1}({2})".format(indent2, self.axis_name(axis), size)
                    for axis, size in self._axes_sizes.iteritems()
                    if axis not in data_axes])
        x = ["{0}{1}({2})".format(indent2, self.axis_name(axis), 
                                  self._axes_sizes[axis])
             for axis in data_axes]

        string = '\n'.join(string + w + x)
       
        if display:
            print string
        else:
            return string
    #--- End: def
         
    def dump_components(self, complete=False, display=True, _level=0):
        '''
        
Return a string containing a full description of the domain.

:Parameters:

    complete : bool, optional

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed.

:Returns:

    out : str
        A string containing the description.

:Examples:

'''
        indent1 = '    ' * _level

        string = []
         
        # Dimension coordinates
        for key, value in sorted(self.d.iteritems()):
            string.append('')
            string.append('%sDimension coordinate: %s' %
                          (indent1, value.name('')))
            string.append(value.dump(display=False, domain=self, key=key, _level=_level+1))

        # Auxiliary coordinates
        for key, value in sorted(self.a.iteritems()):
            string.append('')
            string.append('%sAuxiliary coordinate: %s' % 
                          (indent1, value.name('')))
            string.append(value.dump(display=False, domain=self, key=key,
                                     _level=_level+1))
               
        # Cell measures
        for key, value in sorted(self.m.iteritems()):
            string.append('')
            string.append(value.dump(display=False, domain=self, key=key,
                                     _level=_level))

        # Coordinate references
        for key, value in sorted(self.r.iteritems()):
            string.append('')
            string.append(value.dump(display=False, complete=complete,
                                     domain=self, _level=_level))

        return '\n'.join(string)
    #--- End: def

    def dump(self, complete=False, display=True, _level=0):
        '''

Return a string containing a full description of the domain.

:Parameters:

    complete : bool, optional
        Output a complete dump. Fields contained in coordinate reference are
        themselves described with their dumps.

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``d.dump()`` is equivalent to
        ``print d.dump(display=False)``.

:Returns:

    out : None or str
        A string containing the description.

complete : bool, optional

:Examples:

'''
        string = (self.dump_axes(display=False, _level=_level),
                  self.dump_components(complete=complete, display=False,
                                       _level=_level),
                  )

        string = '\n'.join(string)
       
        if display:
            print string
        else:
            return string
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False,
               verbose=False):
        '''

True if two domains are equal, False otherwise.

Equality is defined as follows:

* There is one-to-one correspondence between dimensions and dimension
  sizes between the two domains.

* For each domain component type (dimension coordinate, auxiliary
  coordinate and cell measures), the set of constructs in one domain
  equals that of the other domain. The component identifiers need not
  be the same.

* The set of coordinate references in one domain equals that of the other
  domain. The coordinate reference identifiers need not be the same.

Equality of numbers is to within a tolerance.

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

>>> d.equals(s)
True

>>> d.equals(t)
False

>>> d.equals(t, traceback=True)


'''
        if self is other:
            return True
        
        # Check that each instance is the same type
        if type(self) != type(other):
            print("%s: Different types: %s, %s" %
                  (self.__class__.__name__,
                   self.__class__.__name__,
                   other.__class__.__name__))
            return False
        #--- End: if

        if (sorted(self._axes_sizes.values()) != 
            sorted(other._axes_sizes.values())):
            # There is not a 1-1 correspondence between dimensions and
            # dimension sizes between the two domains.           
            if traceback:
                print("%s: Different domain ranks: %s != %s" %
                      (self.__class__.__name__,
                       sorted(self._axes_sizes.values()),
                       sorted(other._axes_sizes.values())))
            return False
        #--- End: if

        if rtol is None:
            rtol = RTOL()
        if atol is None:
            atol = ATOL()              

        # ------------------------------------------------------------
        # Test the coordinates and cell measures. Don't worry about
        # coordinate references yet - we'll do so later.
        # ------------------------------------------------------------
        key_map = {}
        for self_keys, other_keys in izip((self.d,  self.a,  self.m),
                                          (other.d, other.a, other.m)):
            self_items  = self_keys.items()
            other_items = other_keys.items()
            for key0, value0 in self_items:
                found_match = False
                for i, (key1, value1) in enumerate(other_items):
                    if value0.equals(value1, rtol=rtol, atol=atol,
                                     ignore_fill_value=ignore_fill_value,
                                     traceback=verbose):
                        found_match = True
                        key_map[key1] = key0
                        other_items.pop(i)
                        break
                #--- End: for

                if not found_match:
                    if traceback:
                        print("{0}: No {1} equal to: {2!r}".format(
                                self.__class__.__name__,
                                value1.__class__.__name__,
                                value0))
                    return False
            #--- End: for
        #--- End: for

        # ------------------------------------------------------------
        # Test the coordinate references
        # ------------------------------------------------------------
        self_t  = self.r
        other_t = other.r
        if not self_t:
            if other_t:
                # Self doesn't have any coordinate references but other does
                if traceback:
                    print(
"%s: Different numbers of coordinate references: 0 != %d" %
(self.__class__.__name__, len(other_t)))
                return False
        else:
            if not other_t:
                # Other doesn't have any coordinate references but self does
                if traceback:
                    print(
"%s: Different numbers of coordinate references: %d != 0" %
(self.__class__.__name__, len(self_t)))
                return False
            #--- End: if

            refs1 = other_t.keys()

            for key0, ref0 in self_t.iteritems():
                found_match = False

                for key1 in refs1:
                    ref1 = other_t[key1]

                    if self._equal_refs(ref0, ref1, domain=other,
                                        pointer_map=key_map,
                                        ignore_fill_value=ignore_fill_value,
                                        traceback=verbose): 
                        # This coordinate reference is also in other
                        found_match = True
                        refs1.remove(key1)
                        break
                #--- End: for

                if not found_match:
                    # This coordinate reference was not found in other
                    if traceback:
                        print("%s: Missing coordinate reference: %r" %
                              (self.__class__.__name__, ref0))
                    return False
            #--- End: for                    
        #--- End: if

        # ------------------------------------------------------------
        # Still here? Then the two domains are equal
        # ------------------------------------------------------------
        return True
    #--- End: def

#--- End: class
