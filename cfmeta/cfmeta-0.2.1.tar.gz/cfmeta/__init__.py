# -*- coding: utf-8 -*-

"""A Python package to interact with Climate model metadata.

The ``cfmeta`` - Climate Model Metadata Extractor package makes it
easy to extract standard CMIP metadata from CMIP3/5 NetCDF
filepaths and/or the metadata contained in the NetCDF file itself.
Metadata can be manipulated with a simple interface, and
CMIP3/5 compliant file paths generated from a metadata collection.

"""

from .path import get_dir_meta
from .cmip5file import Cmip5File
from .cmip3file import Cmip3File
from .cmipfile import CmipFile
