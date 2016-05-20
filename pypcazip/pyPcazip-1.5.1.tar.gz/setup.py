#!/usr/bin/env python
"""  Setup script. Used by easy_install and pip. """

import os

from setuptools import find_packages
from numpy.distutils.core import setup, Extension

import sys
import textwrap

'''Discover the package version'''
import re
VERSIONFILE="pypcazip/pcazip/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RunTimeError("Unable to find version string in {}.".format(VERSIONFILE))

'''The minimum version of NumPy required.'''
min_numpy_version = '1.0.3'
min_scipy_version = '0.10.0'

'''Some functions for showing errors and warnings.'''
def _print_admonition(kind, head, body):
    tw = textwrap.TextWrapper(
        initial_indent='   ', subsequent_indent='   ')

    print ".. %s:: %s" % (kind.upper(), head)
    for line in tw.wrap(body):
        print line

def exit_with_error(head, body=''):
    _print_admonition('error', head, body)
    sys.exit(1)

def print_warning(head, body=''):
    _print_admonition('warning', head, body)

print "Checking python version!"
if not (sys.version_info[0] >= 2 and sys.version_info[1] >= 4):
    exit_with_error("You need Python 2.4 or greater to install pyPcazip!")
print "Python version checked."

''' Check for required Python packages. '''
def check_import(pkgname, pkgver):
    try:
        mod = __import__(pkgname)
    except ImportError:
        exit_with_error(
            "Can't find a local %s Python installation." % pkgname,
            "Please read carefully the ``README`` file "
            "and remember that pyPcazip needs the %s package "
            "to compile and run." % pkgname )
    else:
        if mod.__version__ < pkgver:
            exit_with_error(
                "You need %(pkgname)s %(pkgver)s or greater to run pyPcazip!"
                % {'pkgname': pkgname, 'pkgver': pkgver} )

    print ( "* Found %(pkgname)s %(pkgver)s package installed."
            % {'pkgname': pkgname, 'pkgver': mod.__version__} )
    globals()[pkgname] = mod
    
check_import('numpy', min_numpy_version)
check_import('scipy', min_scipy_version)

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup_args = {
    'name'             : "pyPcazip",
    'version'          : verstr,
    'description'      : "PCA-based molecular dynamics trajectory file compression and analysis.",
    'long_description' : "PCA-based molecular dynamics trajectory file compression and analysis.",
    'author'           : "The University of Nottingham & BSC",
    'author_email'     : "charles.laughton@nottingham.ac.uk",
    'url'              : "https://bitbucket.org/ramonbsc/pypcazip/overview",
    'download_url'     : "https://bitbucket.org/ramonbsc/pypcazip/get/{}.tar.gz".format(verstr),
    'license'          : "BSD license.",
    'classifiers'      : [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],

    'packages'    : find_packages('pypcazip'),
    'package_dir' : {'': 'pypcazip'},
    'scripts' : ['pypcazip/pyPcazip',
                 'pypcazip/pyPcaunzip',
                 'pypcazip/pyPczcomp',
                 'pypcazip/pyPczdump',
                 'pypcazip/pyPczplot',
                 'pypcazip/pyPczclust'],
    'install_requires' : ['numpy',
                          'scipy',
    		          'mdtraj',
                          'h5py',
                          'netCDF4',
                          'cython',
                          'argparse'],

    'zip_safe'         : False,
    'ext_modules'      : [Extension(name='MDPlus.core.fastfitting',
                              sources=['pypcazip/MDPlus/f2py/fastfitting.f90', 
                                       'pypcazip/MDPlus/f2py/matfit.f'],
                              f2py_options=['only:','fitted_avg','fitted_traj',
                                            'fitted','rmsd_traj', 'rmsd',
                                            'rv',':'])],
}

setup(**setup_args)
