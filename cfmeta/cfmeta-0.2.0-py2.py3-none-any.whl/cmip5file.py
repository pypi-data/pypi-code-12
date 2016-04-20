# -*- coding: utf-8 -*-

"""Module to process Cmip5 file based metadata
"""

import os.path

from .cmipfile import CmipFile
from .path import get_dir_meta
from .exceptions import PathError

CMIP5_FNAME_REQUIRED_ATTS = ['variable_name','mip_table','model','experiment','ensemble_member']
CMIP5_FNAME_OPTIONAL_ATTS = ['temporal_subset', 'geographical_info']

CMIP5_FP_ATTS = [
    'activity',
    'product',
    'institute',
    'model',
    'experiment',
    'frequency',
    'modeling_realm',
    'variable_name',
    'ensemble_member',
]

CMIP5_DATANODE_FP_ATTS = [
    'activity',
    'product',
    'institute',
    'model',
    'experiment',
    'frequency',
    'modeling_realm',
    'mip_table',
    'ensemble_member',
    'version_number',
    'variable_name',
]

class Cmip5File(CmipFile):
    """Represents a Cmip5File.

    Metadata is parsed based on interpreting the following documentation as best as possible:

    - `Metadata requirements`_
    - `Data Reference Syntax`_
    - `Standard Output (CMOR Tables)`_

    .. _Metadata Requirements:
       http://cmip-pcmdi.llnl.gov/cmip5/docs/CMIP5_output_metadata_requirements.pdf
    .. _Data Reference Syntax:
       http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf
    .. _Standard Output (CMOR Tables):
       http://cmip-pcmdi.llnl.gov/cmip5/docs/standard_output.pdf

    Arguments:
        cmor_fp (Optional[str]): A file path conforming to DRS spec.
        datanode_fp (Optional[str]): A file path conforming to DRS spec.
        cmor_fname (Optional[str]): A file path conforming to DRS spec.
        **kwargs: Keyworded metadata (overrides any meta obtained from path args)

    """

    def __init__(self,
                 cmor_fp = None,
                 datanode_fp = None,
                 cmor_fname = None,
                 **kwargs):
        """Initializes a Cmip5File.

        """

        meta = {}

        # Initialize with file path
        if cmor_fp:
            meta.update(get_cmor_fp_meta(cmor_fp))
        elif datanode_fp:
            meta.update(get_datanode_fp_meta(datanode_fp))
        elif cmor_fname:
            meta.update(get_cmor_fname_meta(cmor_fname))

        meta.update(kwargs)

        super(Cmip5File, self).__init__(**meta)

    # Path generators
    @property
    def cmor_fname(self):
        """Generates a CMOR filename from object attributes.
        """

        return self.get_joined_file_name(CMIP5_FNAME_REQUIRED_ATTS, CMIP5_FNAME_OPTIONAL_ATTS)

    @property
    def cmor_dirname(self):
        """Generates a CMOR directory path from object attributes
        """

        return self.get_joined_dir_name(CMIP5_FP_ATTS)

    @property
    def cmor_fp(self):
        """Generates a CMOR file path from object attributes
        """

        return os.path.join(self.cmor_dirname, self.cmor_fname)

    @property
    def datanode_dirname(self):
        """Generates a datanode extended CMOR directory path from object attributes
        """

        return self.get_joined_dir_name(CMIP5_DATANODE_FP_ATTS)

    @property
    def datanode_fp(self):
        """Generates a datanode extended CMOR file path from object attributes
        """

        return os.path.join(self.datanode_dirname, self.cmor_fname)

def get_cmor_fp_meta(fp):
    """Processes a CMOR style file path.

    Section 3.1 of the `Data Reference Syntax`_ details:

        The standard CMIP5 output tool CMOR optionally writes output files
        to a directory structure mapping DRS components to directory names as:

            <activity>/<product>/<institute>/<model>/<experiment>/<frequency>/
            <modeling_realm>/<variable_name>/<ensemble_member>/<CMOR filename>.nc

    Arguments:
        fp (str): A file path conforming to DRS spec.

    Returns:
        dict: Metadata as extracted from the file path.

    .. _Data Reference Syntax:
       http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf
    """

    # Copy metadata list then reverse to start at end of path
    directory_meta = list(CMIP5_FP_ATTS)

    # Prefer meta extracted from filename
    meta = get_dir_meta(fp, directory_meta)
    meta.update(get_cmor_fname_meta(fp))

    return meta

def get_datanode_fp_meta(fp):
    """Processes a datanode style file path.

    Section 3.2 of the `Data Reference Syntax`_ details:

        It is recommended that ESGF data nodes should layout datasets
        on disk mapping DRS components to directories as:

            <activity>/<product>/<institute>/<model>/<experiment>/
            <frequency>/<modeling_realm>/<mip_table>/<ensemble_member>/
            <version_number>/<variable_name>/<CMOR filename>.nc

    Arguments:
        fp (str): A file path conforming to DRS spec.

    Returns:
        dict: Metadata as extracted from the file path.

    .. _Data Reference Syntax:
       http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf
    """

    # Copy metadata list then reverse to start at end of path
    directory_meta = list(CMIP5_DATANODE_FP_ATTS)

    # Prefer meta extracted from filename
    meta = get_dir_meta(fp, directory_meta)
    meta.update(get_cmor_fname_meta(fp))

    return meta

def get_cmor_fname_meta(fname):
    """Processes a CMOR style file name.

    Section 3.3 of the `Data Reference Syntax`_ details:

        filename = <variable name>_<mip_table>_<model>_<experiment>_
            <ensemble_member>[_<temporal_subset>][_<geographical_info>].nc

    Temporal subsets are detailed in section 2.4:

        Time instants or periods will be represented by a construction
        of the form “N1-N2”, where N1 and N2 are of the form
        ‘yyyy[MM[dd[hh[mm[ss]]]]][-suffix]’, where ‘yyyy’, ‘MM’, ‘dd’,
        ‘hh’ ‘mm’ and ‘ss’ are integer year, month, day, hour, minute,
        and second, respectively, and the precision with which time is
        expressed must unambiguously resolve the interval between
        timesamples contained in the file or virtual file

    Geographic subsets are also detailed in section 2.4:

        The DRS specification for this indicator is a string of the
        form g-XXXX[-YYYY]. The “g-” indicates that some spatial selection
        or processing has been done (i.e., selection of a sub-global region
        and possibly spatial averaging).

    Arguments:
        fname (str): A file name conforming to DRS spec.

    Returns:
        dict: Metadata as extracted from the filename.

    .. _Data Reference Syntax:
       http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf
    """
    if '/' in fname:
        fname = os.path.split(fname)[1]
    fname = os.path.splitext(fname)[0]
    meta = fname.split('_')

    res = {}

    try:
        for key in CMIP5_FNAME_REQUIRED_ATTS:
            res[key] = meta.pop(0)
    except IndexError:
        raise PathError(fname)

    # Determine presence and order of optional metadata
    if len(meta) > 2:
        raise PathError(fname)

    is_geo = lambda x: x[0] == 'g'

    for key in meta:
        if is_geo(key):
            res['geographical_info'] = key
        else:
            res['temporal_subset'] = key

    return res
