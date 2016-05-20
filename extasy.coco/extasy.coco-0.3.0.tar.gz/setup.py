""" Setup script. Used by easy_install and pip. """

import os
import sys
import subprocess as sp
import re

from setuptools import setup, find_packages, Command

VERSIONFILE="src/coco/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RunTimeError("Unable to find version string in {}.".format(VERSIONFILE))

#-----------------------------------------------------------------------------
# check python version. we need > 2.5, <3.x
if  sys.hexversion < 0x02050000 or sys.hexversion >= 0x03000000:
    raise RuntimeError("%s requires Python 2.x (2.5 or higher)" % name)


#-----------------------------------------------------------------------------
#
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


#-----------------------------------------------------------------------------
setup_args = {
    'name'             : "extasy.coco",
    'version'          : verstr,
    'description'      : "EXTASY Project - CoCo",
    'long_description' : "ExTASY Project - CoCo : molecular ensemble analysis and enhancement.",
    'author'           : "The EXTASY Project",
    'author_email'     : "charles.laughton@nottingham.ac.uk",
    'url'              : "https://bitbucket.org/extasy-project/extasy-project",
    'download_url'     : "https://bitbucket.org/extasy-project/coco/get/"+verstr+".tar.gz",
    'license'          : "MIT",
    'classifiers'      : [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],

    'namespace_packages': ['coco'],
    'packages'    : find_packages('src'),
    'package_dir' : {'': 'src'},
    'scripts' : ['src/pyCoCo'],
    'install_requires' : ['numpy',
                          'scipy',
    		          'pyPcazip'],
    'zip_safe'         : False,
}

#-----------------------------------------------------------------------------

setup (**setup_args)
