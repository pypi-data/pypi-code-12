# -*- coding: utf-8 -*-

"""Module to process Cmip3 file based metadata
"""

import os.path

from .cmipfile import CmipFile
from .path import get_dir_meta
from .exceptions import PathError

FNAME_ATTS = ['model','experiment','variable_name','ensemble_member']
FNAME_OPTIONAL_ATTS = ['temporal_subset']

DIR_ATTS = [
    'experiment',
    'variable_name',
    'model',
    'ensemble_member',
]

class Cmip3File(CmipFile):
    """Represents a Cmip3File.

    Arguments:
        fp (Optional[str]): A file path conforming to CMIP3 spec.
        **kwargs: Keyworded metadata (overrides any meta obtained from path args)

    """

    def __init__(self, fp = None, **kwargs):
        """Initializes a Cmip3File.

        """

        meta = {}
        if fp:
            meta.update(get_fp_meta(fp))

        meta.update(kwargs)

        super(Cmip3File, self).__init__(**meta)

    def get_joined_file_name(self, atts, optional_atts = None):
        """Returns a joined path populated with the supplied attribute names

        """

        return '-'.join(
            [getattr(self, x) for x in atts] +
            [getattr(self, x) for x in optional_atts if x in self.__dict__]
        ) + '.nc'

    # Path generators
    @property
    def fname(self):
        """Generates a CMOR filename from object attributes.
        """

        return self.get_joined_file_name(FNAME_ATTS, FNAME_OPTIONAL_ATTS)

    @property
    def dirname(self):
        """Generates a standard CMOR file path from object attributes
        """

        return self.get_joined_dir_name(DIR_ATTS)

    @property
    def fp(self):
        return os.path.join(self.dirname, self.fname)


def get_fp_meta(fp):
    """Processes a CMIP3 style file path.

    The standard CMIP3 directory structure:

        <experiment>/<variable_name>/<model>/<ensemble_member>/<CMOR filename>.nc

    Filename is of pattern:

        <model>-<experiment>-<variable_name>-<ensemble_member>.nc

    Arguments:
        fp (str): A file path conforming to CMIP3 spec.

    Returns:
        dict: Metadata as extracted from the file path.

    """

    # Copy metadata list then reverse to start at end of path
    directory_meta = list(DIR_ATTS)

    # Prefer meta extracted from filename
    meta = get_dir_meta(fp, directory_meta)
    meta.update(get_fname_meta(fp))

    return meta

def get_fname_meta(fp):
    """Processes a CMIP3 style file name.

    Filename is of pattern:

        <model>-<experiment>-<variable_name>-<ensemble_member>.nc

    Arguments:
        fp (str): A file path/name conforming to DRS spec.

    Returns:
        dict: Metadata as extracted from the filename.

    .. _Data Reference Syntax:
       http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf
    """

    # Strip directory, extension, then split
    if '/' in fp:
        fp = os.path.split(fp)[1]
    fname = os.path.splitext(fp)[0]
    meta = fname.split('-')

    res = {}

    try:
        for key in FNAME_ATTS:
            res[key] = meta.pop(0)
    except IndexError:
        raise PathError(fname)

    return res
