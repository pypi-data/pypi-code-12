'''

`CF <http://cfconventions.org/>`_ is a `netCDF
<http://www.unidata.ucar.edu/software/netcdf>`_ convention which is in
wide and growing use for the storage of model-generated and
observational data relating to the atmosphere, ocean and Earth system.

This package is an implementation of the `CF data model
<http://cf-trac.llnl.gov/trac/ticket/95>`_, and as such it is an API
allows for the full scope of data and metadata interactions described
by the CF conventions.

With this package you can:

  * Read `CF-netCDF <http://cfconventions.org/>`_ files,
    `CFA-netCDF <http://www.met.reading.ac.uk/~david/cfa/0.4>`_ files
    and UK Met Office fields files and PP files.
  
  * Create CF fields.

  * Write fields to CF-netCDF and CFA-netCDF files on disk.

  * Aggregate collections of fields into as few multidimensional
    fields as possible using the `CF aggregation rules
    <http://cf-trac.llnl.gov/trac/ticket/78>`_.

  * Create, delete and modify a field's data and metadata.

  * Select and subspace fields according to their metadata.

  * Perform broadcastable, metadata-aware arithmetic, comparison and
    trigonometric operation with fields.

  * Collapse fields by statistical operations.

  * Sensibly deal with date-time data.

  * Allow for cyclic axes.

  * Visualize fields the `cfplot package
    <http://climate.ncas.ac.uk/~andy/cfplot_sphinx/_build/html/>`_.

All of the above use :ref:`LAMA` functionality, which allows multiple
fields larger than the available memory to exist and be manipulated.

See the `cf-python home page <http://cfpython.bitbucket.org/>`_ for
downloads, installation and source code.

'''

__Conventions__  = 'CF-1.5'
__author__       = 'David Hassell'
__date__         = '2016-05-18'
__version__      = '1.1.8'

from distutils.version import StrictVersion
import imp
import platform

# Check the version of python
if not (StrictVersion('2.6.0')
        <= StrictVersion(platform.python_version())
        < StrictVersion('3.0.0')):
    raise ValueError(
        "Bad python version: cf requires 2.6 <= python < 3.0. Got %s" %
        platform.python_version())

## Check the version of numpy
#import numpy
#if StrictVersion(numpy.__version__) < StrictVersion('1.7'):
#    raise ImportError(
#        "Bad numpy version: cf %s requires numpy >= 1.7. Got %s" %
#        (__version__, numpy.__version__))
#
## Check the version of netCDF4
#import netCDF4
#if StrictVersion(netCDF4.__version__) < StrictVersion('0.9.7'):
#    raise ImportError(
#        "Bad netCDF4 version: cf %s requires netCDF4 >= 0.9.7. Got %s" %
#        (__version__, netCDF4.__version__))

try:
    imp.find_module('ESMF')
except ImportError:
    _found_ESMF = False
else:
    _found_ESMF = True

from .variable             import Variable
from .coordinate           import Coordinate, DimensionCoordinate, AuxiliaryCoordinate
from .coordinatebounds     import CoordinateBounds
from .coordinatereference  import CoordinateReference
from .cellmeasure          import CellMeasure
from .domain               import Domain
from .field                import Field, FieldList
from .read                 import read
from .write                import write
from .utils                import Dict #List, Dict
from .units                import Units
from .cfdatetime           import Datetime, dt
from .timeduration         import TimeDuration, Y, M, D, h, m, s
from .data.data            import Data
from .aggregate            import aggregate
from .query                import (Query, lt, le, gt, ge, eq, ne, contain,
                                   wi, wo, set, year, month, day, hour, minute,
                                   second, dtlt, dtle, dtgt, dtge, dteq, dtne,
                                   cellsize, cellge, cellgt, cellle, celllt,
                                   cellwi, cellwo, djf, mam, jja, son, seasons)
from .flags                import Flags
from .cellmethods          import CellMethods
from .constants            import *
from .functions            import *


