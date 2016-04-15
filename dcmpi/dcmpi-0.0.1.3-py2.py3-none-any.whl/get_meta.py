#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract metadata information from DICOM files and save to text files.

Note: metadata information are not easy to parse.
"""

# ======================================================================
# :: Future Imports
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# ======================================================================
# :: Python Standard Library Imports
import os  # Miscellaneous operating system interfaces
# import shutil  # High-level file operations
# import math  # Mathematical functions
import time  # Time access and conversions
import datetime  # Basic date and time types
# import operator  # Standard operators as functions
# import collections  # High-performance container datatypes
import argparse  # Parser for command-line options, arguments and sub-commands
# import itertools  # Functions creating iterators for efficient looping
# import functools  # Higher-order functions and operations on callable objects
# import subprocess  # Subprocess management
# import multiprocessing  # Process-based parallelism
# import csv  # CSV File Reading and Writing [CSV: Comma-Separated Values]
import json  # JSON encoder and decoder [JSON: JavaScript Object Notation]

# :: External Imports
# import numpy as np  # NumPy (multidimensional numerical arrays library)
# import scipy as sp  # SciPy (signal and image processing library)
# import matplotlib as mpl  # Matplotlib (2D/3D plotting library)
# import sympy as sym  # SymPy (symbolic CAS library)
# import PIL  # Python Image Library (image manipulation toolkit)
# import SimpleITK as sitk  # Image ToolKit Wrapper
# import nibabel as nib  # NiBabel (NeuroImaging I/O Library)
# import nipy  # NiPy (NeuroImaging in Python)
# import nipype  # NiPype (NiPy Pipelines and Interfaces)
import dicom as pydcm  # PyDicom (Read, modify and write DICOM files.)

# :: External Imports Submodules
# import matplotlib.pyplot as plt  # Matplotlib's pyplot: MATLAB-like syntax
# import mayavi.mlab as mlab  # Mayavi's mlab: MATLAB-like syntax
# import scipy.optimize  # SciPy: Optimization Algorithms
# import scipy.integrate  # SciPy: Integrations facilities
# import scipy.constants  # SciPy: Mathematal and Physical Constants
# import scipy.ndimage  # SciPy: ND-image Manipulation

# :: Local Imports
# import mri_tools.modules.base as mrb
# import mri_tools.modules.utils as mru
# import mri_tools.modules.nifti as mrn
# import mri_tools.modules.geometry as mrg
# from mri_tools.modules.sequences import mp2rage
import dcmpi.common as dcmlib
from dcmpi import INFO
from dcmpi import VERB_LVL
from dcmpi import D_VERB_LVL


# ======================================================================
def get_meta(
        in_dirpath,
        out_dirpath,
        method='isis',
        type_ext=False,
        force=False,
        verbose=D_VERB_LVL):
    """
    Extract metadata information from DICOM files and save to text files.

    Parameters
    ==========
    in_dirpath : str
        Path to input directory.
    out_dirpath : str
        Path to output directory.
    method : str (optional)
        | Extraction method. Accepted values:
        * isis: Use Enrico Reimer's ISIS tool.
        * pydicom: Use PyDICOM Python module.
        * strings: Use POSIX 'string' command.
    type_ext : boolean (optional)
        Add type extension to filename.
    force : boolean (optional)
        Force new processing.
    verbose : int (optional)
        Set level of verbosity.

    Returns
    =======
    None.

    """
    if verbose > VERB_LVL['none']:
        print(':: Exporting METADATA information ({})...'.format(method))
    if verbose > VERB_LVL['none']:
        print('Input:\t{}'.format(in_dirpath))
    if verbose > VERB_LVL['none']:
        print('Output:\t{}'.format(out_dirpath))
    sources_dict = dcmlib.dcm_sources(in_dirpath)
    # groups_dict = dcmlib.group_series(in_dirpath)
    # proceed only if output is not likely to be there
    if not os.path.exists(out_dirpath) or force:
        # :: create output directory if not exists and copy files there
        if not os.path.exists(out_dirpath):
            os.makedirs(out_dirpath)

        if method == 'isis':
            for src_id, in_filepath_list in sorted(sources_dict.items()):
                in_filepath = os.path.join(in_dirpath, src_id)
                out_filepath = os.path.join(
                    out_dirpath, src_id + '.' + dcmlib.ID['meta'])
                out_filepath += ('.' + dcmlib.TXT_EXT) if type_ext else ''
                if verbose > VERB_LVL['none']:
                    out_subpath = out_filepath[len(out_dirpath):]
                    print('Metadata:\t{}'.format(out_subpath))
                opts = ' -np'  # do not include progress bar
                opts += ' -rdialect withExtProtocols'  # extended prot info
                opts += ' -chunks'  # information from each chunk
                # cmd = 'isisdump -in {} {}'.format(in_filepath, opts)
                # p_stdout, p_stderr = dcmlib.execute(cmd, verbose=verbose)
                cmd = 'isisdump -in {} {} > {} &> {}'.format(
                    in_filepath, opts, out_filepath, out_filepath)
                dcmlib.execute(cmd, use_pipes=False, verbose=verbose)

        elif method == 'pydicom':
            for src_id, in_filepath_list in sorted(sources_dict.items()):
                out_filepath = os.path.join(
                    out_dirpath, src_id + '.' + dcmlib.ID['meta'])
                out_filepath += ('.' + dcmlib.JSON_EXT) if type_ext else ''
                info_dict = {}
                for in_filepath in in_filepath_list:
                    try:
                        dcm = pydcm.read_file(in_filepath)
                    except:
                        print("EE: failed processing '{}'".format(in_filepath))
                    else:
                        dcm_dict = dcmlib.dcm_dump(dcm)
                        info_dict = dcmlib.dcm_merge_info(info_dict, dcm_dict)
                if verbose > VERB_LVL['none']:
                    out_subpath = out_filepath[len(out_dirpath):]
                    print('Meta:\t{}'.format(out_subpath))
                with open(out_filepath, 'w') as info_file:
                    json.dump(info_dict, info_file, sort_keys=True, indent=4)

        elif method == 'dcm_dump':
            # TODO: implement meaningful super-robust string method.
            if verbose > VERB_LVL['none']:
                print('WW: Method \'{}\' not implemented yet.')

        elif method == 'strings':
            # TODO: implement meaningful super-robust string method.
            if verbose > VERB_LVL['none']:
                print('WW: Method \'{}\' not implemented yet.')

        else:
            if verbose > VERB_LVL['none']:
                print("WW: Unknown method '{}'.".format(method))
    else:
        if verbose > VERB_LVL['none']:
            print("II: Output path exists. Skipping. " +
                  "Use 'force' argument to override.")


# ======================================================================
def handle_arg():
    """
    Handle command-line application arguments.
    """
    # :: Define DEFAULT values
    # verbosity
    d_verbose = D_VERB_LVL
    # default input directory
    d_input_dir = '.'
    # default output directory
    d_output_dir = '.'
    # default method
    d_method = 'pydicom'
    # :: Create Argument Parser
    arg_parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='v.{} - {}\n{}'.format(
            INFO['version'], ', '.join(INFO['authors']), INFO['license']),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # :: Add POSIX standard arguments
    arg_parser.add_argument(
        '--ver', '--version',
        version='%(prog)s - ver. {}\n{}\n{} {}\n{}'.format(
            INFO['version'],
            next(line for line in __doc__.splitlines() if line),
            INFO['copyright'], ', '.join(INFO['authors']),
            INFO['notice']),
        action='version')
    arg_parser.add_argument(
        '-v', '--verbose',
        action='count', default=d_verbose,
        help='increase the level of verbosity [%(default)s]')
    # :: Add additional arguments
    arg_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='force new processing [%(default)s]')
    arg_parser.add_argument(
        '-i', '--input', metavar='DIR',
        default=d_input_dir,
        help='set input directory [%(default)s]')
    arg_parser.add_argument(
        '-o', '--output', metavar='DIR',
        default=d_output_dir,
        help='set output directory [%(default)s]')
    arg_parser.add_argument(
        '-m', '--method', metavar='METHOD',
        default=d_method,
        help='set extraction method [%(default)s]')
    arg_parser.add_argument(
        '-t', '--type_ext',
        action='store_true',
        help='add type extension [%(default)s]')
    return arg_parser


# ======================================================================
def main():
    # :: handle program parameters
    arg_parser = handle_arg()
    args = arg_parser.parse_args()
    # :: print debug info
    if args.verbose == VERB_LVL['debug']:
        arg_parser.print_help()
        print()
        print('II:', 'Parsed Arguments:', args)
    print(__doc__)
    begin_time = time.time()

    get_meta(
        args.input, args.output,
        args.method, args.type_ext,
        args.force, args.verbose)

    end_time = time.time()
    if args.verbose > VERB_LVL['low']:
        print('ExecTime: ', datetime.timedelta(0, end_time - begin_time))


# ======================================================================
if __name__ == '__main__':
    main()
