#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==============================================================================
"""
author
======

Novimir Antoniuk Pablant
- npablant@pppl.gov
- novimir.pablant@amicitas.com


purpose
=======
Build the mirpyidl module.


description
===========

This is a standard python setup script that can be used to build and
install the mirpyidl module.  This suports all of the standard distuils 
commands. If setuputils is installed, the extended commands will work as 
well.

To install mirpyidl use the following command:
python setup.py install

To build the mirpyidl module as a library (*.so) that can be directly
imported from python use:
python setup.py build_ext --inplace


This setup script also includes a custom clean command which will remove
any build files from the source directory.  The optional keword all will
also remove the built library.  For example:
python setup.py clean --all


requirements
============

Python 2.7, 3.0 or later
Cython

Python Packages:
  numpy

All of these dependencies are available on all platforms using your
favorite package manager (macports, easy_install, apt-get, etc.)
   

"""

import os
import platform
import subprocess
import numpy

try:
    from setuptools.core import setup
except:
    from distutils.core import setup

from distutils.cmd import Command
from distutils.extension import Extension

exec(open('_version.py').read())

# Since mirpyidl is still in the development stage I am going
# to always use cython if it is available.
use_cython = True
try:
    from Cython.Build import cythonize
except ImportError:
    use_cython = False

if platform.architecture()[0] == '32bit':
    machine = 'i386'
elif platform.architecture()[0] == '64bit':
    machine = 'x86_64'
else:
    raise Exception("Platform type could not be determined.")


def renameDarwinLibraries(libname_in, idl_bin_dir):
    """
    On OS X, the linker will only find libaries in the rpath directory if
    they have an installation name starting with @rpath.  Since this is not
    the default for libidl_rpc or libidl or related libraries, we change the
    name here.
    
    Original and final installation names:
      libidl.8.3.dylib     -> @rpath/libidl.8.3.dylib
      libidl_rpc.8.3.dylib -> @rpath/libidl_rpc.8.3.dylib
      libMesaGL6_2.dylib   -> @rpath/libMesaGL6_2.dylib
      libMesaGLU6_2.dylib  -> @rpath/libMesaGLU6_2.dylib
      libOSMesa6_2.dylib   -> @rpath/libOSMesa6_2.dylib
       
    
    This has no know negative side effects and IDL works just as before.
    """
    
    # Find the name of the libidl.dylib and libidl_rpc.dylib libraries
    # for the current IDL version.
    libpath = os.path.join(idl_bin_dir, libname_in)
    libpath = os.path.realpath(libpath)
    libname = os.path.basename(libpath)


    otool_output = subprocess.check_output(['otool', '-D', libpath])
    libname_orig = otool_output.splitlines()[1].decode()
    if libname_orig.find('@rpath') != 0:
        # The idl_rpc library does not have the correct name. Rename it now.
        print('\nThe installation name of {name:} must be changed to\n' 
              '@rpath/{name:} for pyidlrpc to properly link to the library.\n'
              'Renaming requires root privalages. (Press control-c to abort.)\n'.format(name=libname))
        try:
            subprocess.check_call(['sudo', 'install_name_tool', '-id', '@rpath/'+libname, libpath])

            otool_output = subprocess.check_output(['otool', '-D', libpath])
            libname_new = otool_output.splitlines()[1].decode()
            if libname_new.find('@rpath') != 0:
                raise Exception
            print('Renamed an IDL shared library from {} to {}.'.format(libname_orig, libname_new))

        except:
            print('\nUnable to change the installation name of the {name:} library.\n'
                  'This can be done manually by using the command:\n'
                  '   sudo install_name_tool -id @rpath/{name:} {path:}\n'
                  'Alternively add the following line to your .bashrc file:\n'
                  '   export DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH:$IDL_DIR/bin/bin.darwin.'+machine+'\n'
                  '\n'.format(name=name, path=path))

            
def fixDarwinIDLLibraryNames(libname_change_in, libname_fix_in, idl_bin_dir):
    """
    In addition to changing the installation names of the IDL libraries we also
    to change names of the libraries that are linked by the IDL libraries to
    also use the standard OS X @rpath convension.
    """
    
    # Find the name of the libidl.dylib and libidl_rpc.dylib libraries
    # for the current IDL version.
    libpath_fix = os.path.join(idl_bin_dir, libname_fix_in)
    libpath_fix = os.path.realpath(libpath_fix)
    libname_fix = os.path.basename(libpath_fix)

    libpath_change = os.path.join(idl_bin_dir, libname_change_in)
    libpath_change = os.path.realpath(libpath_change)
    libname_change = os.path.basename(libpath_change)

    libname_change_orig = libname_change
    libname_change_new = '@rpath/'+libname_change

    if not '@rpath/'+libname_change in subprocess.check_output(['otool', '-L', libpath_fix]).decode():
        subprocess.check_call(['sudo'
                               ,'install_name_tool'
                               ,'-change'
                               ,libname_change_orig
                               ,libname_change_new
                               ,libpath_fix])

        print('Changed the linked library name from {} to {} in the file {}.'.format(
            libname_change_orig
            ,libname_change_new
            ,libpath_fix))
            
    
# Find the idl installation directory. And setup shared libraries.
#
# The installaiton directory can almost always be found using the 'IDL_DIR' 
# environment variable. The problem though is that installation will sometimes 
# require the use of sudo, which on some systems does not preserve environment 
# variables.
if platform.system() == 'Darwin':
    if 'IDL_DIR' in os.environ:
        idl_dir = os.environ['IDL_DIR']
    elif os.path.exists('/Applications/itt/idl/idl/bin/'):
        idl_dir = '/Applications/itt/idl/idl/'
    elif os.path.exists('/Applications/exelis/idl/bin/'):
        idl_dir = '/Applications/exelis/idl/'
    else:
        raise Exception("Could not find idl installation directory.  Please set the the 'IDL_DIR' environmental variable.")
                        
    idl_bin_dir = idl_dir+'/bin/bin.darwin.'+machine

    extra_link_args = ['-Wl,-rpath,'+idl_bin_dir]
    extra_compile_args = ['-Wno-unused-function']
    
    libraries = ['idl', 'idl_rpc', 'Xm', 'MesaGL6_2', 'MesaGLU6_2', 'OSMesa6_2', 'freetype']

    # Change the Darwin installation name of the IDL libraries if necessary.
    renameDarwinLibraries('libidl.dylib', idl_bin_dir)
    renameDarwinLibraries('libidl_rpc.dylib', idl_bin_dir)
    renameDarwinLibraries('libMesaGL6_2.dylib', idl_bin_dir)
    renameDarwinLibraries('libMesaGLU6_2.dylib', idl_bin_dir)
    renameDarwinLibraries('libOSMesa6_2.dylib', idl_bin_dir)

    fixDarwinIDLLibraryNames('libMesaGL6_2.dylib', 'libidl.dylib', idl_bin_dir)
    fixDarwinIDLLibraryNames('libMesaGLU6_2.dylib', 'libidl.dylib', idl_bin_dir)
    fixDarwinIDLLibraryNames('libOSMesa6_2.dylib', 'libidl.dylib', idl_bin_dir)
    fixDarwinIDLLibraryNames('libXm.3.0.2.dylib', 'libidl.dylib', idl_bin_dir)
    fixDarwinIDLLibraryNames('libMesaGL6_2.dylib', 'libMesaGLU6_2.dylib', idl_bin_dir)
    fixDarwinIDLLibraryNames('libMesaGL6_2.dylib', 'libOSMesa6_2.dylib', idl_bin_dir)
    
elif platform.system() == 'Linux':
    if 'IDL_DIR' in os.environ:
        idl_dir = os.environ['IDL_DIR']
    elif os.path.exists('/usr/local/itt/idl/idl/bin/'):
        idl_dir = '/usr/local/itt/idl/idl/'
    elif os.path.exists('/usr/local/exelis/idl/bin/'):
        idl_dir = '/usr/local/exelis/idl/'
    elif os.path.exists('/opt/exelis/idl/bin/'):
        idl_dir = '/opt/exelis/idl/'
    else:
        raise Exception("Could not find idl installation directory.  Use the --idl-dir option.")
    
    idl_bin_dir = idl_dir+'/bin/bin.linux.'+machine

    extra_link_args = []
    extra_compile_args = ['-Wno-unused-function']

    libraries = ['idl', 'idl_rpc']
        
else:
    raise Exception("Location of IDL bin directory unknown for platform: {}.".format(platform.system()))




include_dirs = [idl_dir+'/external/include'
                ,numpy.get_include()]
library_dirs = [idl_bin_dir]


# Define the extension.
#
# There is a bug in cython that does not allow me to create
# certain numpy objects if language="c++".  With c I get
# warnings instead of errors. 
# (I don't know if this is still true 2014-01-06)

if use_cython:
    ext = '.pyx'
else:
    ext = '.c'
    
extensions = [
    Extension('mirpyidl'
              ,['mirpyidl'+ext]
              ,include_dirs=include_dirs
              ,libraries=libraries
              ,library_dirs=library_dirs
              ,runtime_library_dirs=[idl_bin_dir]
              ,extra_compile_args=extra_compile_args
              ,extra_link_args=extra_link_args
              )
    ]
        
# Cythonize.
if use_cython:
    extensions = cythonize(extensions)


class CleanCommand(Command):
    description = "custom clean command that forcefully removes dist/build directories"
    user_options = [("all", None, "Clean all files.")]
    def initialize_options(self):
        self.cwd = None
        self.all = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        os.system('rm -rf ./build ./mirpyidl.c ./mirpyidl.cpp ./setup.cfg')
        if self.all:
            os.system('rm -rf ./mirpyidl.so ./mirpyidl.egg-info ./dist')


# Read in the README file to use as a long description.
with open('README') as file:
    long_description = file.read()

# Options for PyPI
classifiers=[
    "Development Status :: 4 - Beta"
    ,"License :: OSI Approved :: MIT License"
    ,"Topic :: Software Development :: Interpreters"
    ,"Programming Language :: Cython"
    ,"Programming Language :: Python"
    ,"Programming Language :: Other"
    ]

# Setup options for setup.
params = {'name':'mirpyidl'
          ,'version':__version__
          ,'description':'A library to call IDL (Interactive Data Language) from python.'
          ,'long_description':long_description
          ,'author':'Novimir Antoniuk Pablant'
          ,'author_email':'novimir.pablant@amicitas.com'
          ,'url':'http://amicitas.bitbucket.org/mirpyidl/'
          ,'license':'MIT'
          ,'ext_modules':extensions
          ,'py_modules':['mirpyidlrpc']
          ,'packages':None
          ,'classifiers':classifiers
          ,'install_requires':['numpy', 'psutil']
          }

# Override the C-extension building so that it knows about '.pyx'
# Cython files
params['cmdclass'] = dict(clean=CleanCommand)

# Call the actual building/packaging function (see distutils docs)
setup(**params)
