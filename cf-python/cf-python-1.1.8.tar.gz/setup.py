from distutils.core import setup, Extension
from distutils.command.build import build
import os
import fnmatch
import sys
import imp
import subprocess

def find_package_data_files(directory):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, '*'):
                filename = os.path.join(root, basename)
#                if filename.find('/.svn') > -1:
#                    continue
                yield filename.replace('cf/', '', 1)

## Check that the dependencies are met
#for _module in ('netCDF4', 'numpy'):
#    try:
#        imp.find_module(_module)
#    except ImportError as error:
#        raise ImportError("Missing dependency. cf requires package %s. %s" %
#                          (_module, error))
##--- End: for
#
       
version      = '1.1.8'
packages     = ['cf']
etc_files    = [f for f in find_package_data_files('cf/etc')]
umread_files = [f for f in find_package_data_files('cf/um/umread/c-lib')]

package_data = etc_files + umread_files

class build_umread(build):
    '''
Adpated from https://github.com/Turbo87/py-xcsoar/blob/master/setup.py
'''
    def run(self):
        # Run original build code
        build.run(self)

        # Build umread
        print 'Running build_umread'

        build_dir = os.path.join(os.path.abspath(self.build_lib), 'cf/um/umread/c-lib')

        cmd = ['make', '-C', build_dir]

        rc = subprocess.call(cmd)

        def compile():            
            print '*' * 80
            print 'Running:', ' '.join(cmd), '\n'
            rc = subprocess.call(cmd)

            print '\n', '-' * 80
            if not rc:
                print 'SUCCESSFULLY BUILT UM read C library'
            else:
                print 'WARNING: Errors during build of UM read C library will cause failures with UKMO PP and UM format files'
                print 'HOWEVER: This will not affect any other cf-python functionality'
            #--- End: if
            print '-' * 80, '\n'

            print '*' * 80
	    print
	    print "cf build successful"
            print
        #--- End: def

        self.execute(compile, [], 'compiling umread')
#--- End: class

#with open('README.md') as ldfile:
#    long_description = ldfile.read()

long_description = """Home page
=========

* `cf-python <http://cfpython.bitbucket.org>`_

Documentation
=============

* `Online documentation for the latest stable release
  <http://cfpython.bitbucket.org/docs/latest/>`_

Dependencies
============

* The package runs on Linux and Mac OS operating systems.

* Requires a python version from 2.6 up to, but not including, 3.0.
 
* See the `README.md
  <https://bitbucket.org/cfpython/cf-python/src/master/README.md>`_
  file for further dependencies

Visualisation
=============

* The `cfplot package <https://pypi.python.org/pypi/cf-plot>`_ at
  version 1.9.10 or newer provides metadata-aware visualisation for
  cf-python fields. This is not a dependency for cf-python.


Command line utilities
======================

* The `cfdump` tool generates text representations on standard output
  of the CF fields contained in the input files.

* The `cfa` tool creates and writes to disk the CF fields contained in
  the input files.

* During installation these scripts will be copied automatically to a
  location given by the ``PATH`` environment variable.

Code license
============

* `MIT License <http://opensource.org/licenses/mit-license.php>`_"""

setup(name = "cf-python",
      long_description = long_description,
      version      = version,
      description  = "Python interface to the CF data model",
      author       = "David Hassell",
      maintainer   = "David Hassell",
      maintainer_email  = "d.c.hassell at reading.ac.uk",
      author_email = "d.c.hassell at reading.ac.uk",
      url          = "http://cfpython.bitbucket.org/",
      download_url = "https://bitbucket.org/cfpython/cf-python/downloads",
      platforms    = ["Linux", "MacOS"],
      keywords     = ['cf','netcdf','data','science',
                      'oceanography','meteorology','climate'],
      classifiers  = ["Development Status :: 5 - Production/Stable",
                      "Intended Audience :: Science/Research", 
                      "License :: OSI Approved :: MIT License", 
                      "Topic :: Scientific/Engineering :: Mathematics",
                      "Topic :: Scientific/Engineering :: Physics",
                      "Topic :: Scientific/Engineering :: Atmospheric Science",
                      "Topic :: Utilities",
                      "Operating System :: POSIX :: Linux",
                      "Operating System :: MacOS"
                      ],
      packages     = ['cf',
                      'cf.um',
                      'cf.um.umread',
                      'cf.data',
                      'cf.netcdf'],
      package_data = {'cf': package_data},
      scripts      = ['scripts/cfa',
                      'scripts/cfdump'],
      requires     = ['netCDF4 (>=1.1.1)',
                      'numpy (>=1.7)',
                      'matplotlib (>=1.4.2)',
                      'psutil (>=0.6.0)',
                      ],
      cmdclass     = {'build': build_umread}, #https://docs.python.org/2/distutils/apiref.html
  )
