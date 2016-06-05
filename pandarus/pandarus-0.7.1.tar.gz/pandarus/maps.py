# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *
from future.utils import python_2_unicode_compatible

from .raster import Raster
from fiona import crs as fiona_crs
from shapely.geometry import shape
from shapely.wkt import loads
import fiona
import hashlib
import rtree


class DuplicateFieldID(Exception):
    """Field ID value is duplicated and should be unique"""
    pass


def to_shape(obj):
    if isinstance(obj, str):
        # GDAL (raster)
        return loads(obj)
    elif isinstance(obj, dict):
        # Fiona (vector)
        return shape(obj)
    else:
        raise ValueError


def sha256(filepath, blocksize=65536):
    """Generate SHA 256 hash for file at `filepath`"""
    hasher = hashlib.sha256()
    fo = open(filepath, 'rb')
    buf = fo.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fo.read(blocksize)
    return hasher.hexdigest()


class Map(object):
    """Common interface to raster and vector data."""
    def __init__(self, filepath, **kwargs):
        """Define the map data.

        Requires an absolute filepath. Zipped shapefiles must be specified like ``/absolute/path/to/file.zip``, and require a layer name that starts with ``/``, e.g. ``/layername``.

        Additional metadata can be provided in `kwargs`:
            * `layer` specifies the shapefile layer
            * `band` specifies the raster band

        .. warning:: The Fiona field ``id`` is not used, as there are no real constraints on these values or values types (see `Fiona manual <http://toblerity.org/fiona/manual.html#record-id>`_), and real world data is often dirty and inconsistent. Instead, we use ``enumerate`` and integer indices.

        """
        self.filepath = filepath
        self.metadata = kwargs
        self.file = self.load()
        if self.file is None:
            raise ValueError(u"Filepath '%s' can't be loaded as vector or raster" % filepath)

    def load(self):
        """Try to load vector file, fall back to raster file"""
        try:
            self.vector, self.raster = True, False
            return self.load_vector()
        except:
            self.vector, self.raster = False, True
            return Raster(self.filepath, band=self.metadata.get("band") or 1) # `band` can't be 0

    def load_vector(self):
        """Load vector file using ``fiona``."""
        if self.filepath[:-4].lower() == ".zip":
            assert self.metadata.get("layer", None), \
                "Need layer name for zipped geodata file"
            assert self.metadata['layer'][0] == "/", \
                "First character of layer name in zipped geodata must be '/'"
            with fiona.drivers():
                shapefile = fiona.open(
                    self.metadata['layer'],
                    encoding=self.metadata.get('encoding', None),
                    vfs=u"zip://" + self.filepath
                )
            return shapefile
        else:
            with fiona.drivers():
                shapefile = fiona.open(
                    self.filepath,
                    encoding=self.metadata.get('encoding', None)
                )
            return shapefile

    def select(self, obj_indices):
        """Return a generator for a selection of geographic objects.

        Integer indices for vector files follow the vector file ordering, and start at zero."""
        obj_indices = set(obj_indices)
        for index, obj in enumerate(self):
            if index in obj_indices:
                yield obj
        raise StopIteration

    def create_rtree_index(self):
        """Create `rtree <http://toblerity.org/rtree/>`_ index for efficient spatial querying."""
        self.rtree_index = rtree.Rtree()
        for index, record in enumerate(self):
            self.rtree_index.add(
                index,
                to_shape(record['geometry']).bounds
            )
        return self.rtree_index

    def get_fieldnames_dictionary(self, fieldname):
        """Get dictionary of map indices and fieldnames, like {1: 'Ghana'}"""
        if self.vector:
            return self.get_fieldnames_vector(fieldname)
        else:
            return {index: obj['label'] for index, obj in enumerate(self.file)}

    def get_fieldnames_vector(self, fieldname):
        fieldname = fieldname or self.metadata.get('field', None)
        assert fieldname, "No field name given or in metadata"
        assert fieldname in self.file.next()['properties'], \
            "Given fieldname not in file"
        fd = {index: obj['properties'].get(fieldname, None) \
            for index, obj in enumerate(self)}
        if len(fd.keys()) != len(set(fd.values())):
            raise DuplicateFieldID(
                "Given field name not unique for all records"
            )
        return fd

    @property
    def hash(self):
        return sha256(self.filepath)

    @property
    def info(self):
        print("info!!!")

    @property
    def crs(self):
        """Coordinate reference system, as defined by vector file."""
        if self.vector:
            return fiona_crs.to_string(self.file.crs)
        else:
            return self.file.crs

    def __iter__(self):
        return iter(self.file)

    def __getitem__(self, index):
        """Incredibly awkward, but avoids loading dataset into memory."""
        if self.raster and hasattr(self.file, "loc_cache"):
            return self.file[index]
        for i, obj in enumerate(self):
            if i == index:
                return obj

    def __len__(self):
        return len(self.file)
