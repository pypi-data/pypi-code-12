#
# This file is part of SpectralToolbox.
#
# SpectralToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SpectralToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with SpectralToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

from setuptools import setup, find_packages
from setuptools.extension import Extension
from setuptools.command.install import install
from setuptools.command.develop import develop
import pip

import os, sys
from subprocess import Popen, PIPE

global include_dirs
include_dirs = []

deps_list = ['numpy']

def deps_install():
    for package in deps_list:
        print("[DEPENDENCY] Installing %s" % package)
        try:
            pip.main(['install', '--no-binary', ':all:', '--upgrade', package])
        except Exception as e:
            print("[Error] Unable to install %s using pip. \
                  Please read the instructions for \
                  manual installation.. Exiting" % package)
            exit(2)

class orthpolxx_install(install):
    def run(self):
        # Install deps
        deps_install()
        import numpy as np
        include_dirs.append(np.get_include())        
        # Install orthpol
        print("Installation of ORTHPOLxx")
        os.chdir("./ORTHPOLxx")
        error = os.system("chmod u+x configure")
        if error: raise Exception("Compile error of ORTHPOLxx")
        currpath = os.getcwd()
        error = os.system("CFLAGS='-fPIC -O3' FFLAGS='-fPIC -O3' CPPFLAGS='-fPIC -O3' ./configure")
        if error: raise Exception("Compile error of ORTHPOLxx")
        error = os.system("make")
        if error: raise Exception("Compile error of ORTHPOLxx")
        os.chdir("../")
        print("Installation of PyORTHPOL")
        install.run(self)

class orthpolxx_develop(develop):
    
    def run(self):
        # Install deps
        deps_install()
        import numpy as np
        include_dirs.append(np.get_include())        
        # Install orthpol
        print("Installation of ORTHPOLxx")
        os.chdir("./ORTHPOLxx")
        error = os.system("chmod u+x configure")
        if error: raise Exception("Compile error of ORTHPOLxx")
        currpath = os.getcwd()
        error = os.system("CFLAGS='-fPIC -O3' FFLAGS='-fPIC -O3' CPPFLAGS='-fPIC -O3' ./configure")
        if error: raise Exception("Compile error of ORTHPOLxx")
        error = os.system("make")
        if error: raise Exception("Compile error of ORTHPOLxx")
        os.chdir("../")
        print("Installation of PyORTHPOL")
        develop.run(self)

if __name__ == "__main__":
        
    oxx_inc = ['./ORTHPOLxx/build/include/liborthpol-1.0']
    oxx_ld = ['ORTHPOLxx/src/cheb.o', 
              'ORTHPOLxx/src/chri.o',
              'ORTHPOLxx/src/d1mach.o',
              'ORTHPOLxx/src/dcheb.o',
              'ORTHPOLxx/src/dchri.o',
              'ORTHPOLxx/src/dgauss.o',
              'ORTHPOLxx/src/dgchri.o',
              'ORTHPOLxx/src/dkern.o',
              'ORTHPOLxx/src/dknum.o',
              'ORTHPOLxx/src/dlancz.o',
              'ORTHPOLxx/src/dlob.o',
              'ORTHPOLxx/src/dmcdis.o',
              'ORTHPOLxx/src/dmcheb.o',
              'ORTHPOLxx/src/dqgp.o',
              'ORTHPOLxx/src/dradau.o',
              'ORTHPOLxx/src/drecur.o',
              'ORTHPOLxx/src/dsti.o',
              'ORTHPOLxx/src/gauss.o',
              'ORTHPOLxx/src/gchri.o',
              'ORTHPOLxx/src/i1mach.o',
              'ORTHPOLxx/src/kern.o',
              'ORTHPOLxx/src/knum.o',
              'ORTHPOLxx/src/lancz.o',
              'ORTHPOLxx/src/lob.o',
              'ORTHPOLxx/src/mccheb.o',
              'ORTHPOLxx/src/mcdis.o',
              'ORTHPOLxx/src/nu0her.o',
              'ORTHPOLxx/src/nu0jac.o',
              'ORTHPOLxx/src/nu0lag.o',
              'ORTHPOLxx/src/qgp.o',
              'ORTHPOLxx/src/r1mach.o',
              'ORTHPOLxx/src/radau.o',
              'ORTHPOLxx/src/recur.o',
              'ORTHPOLxx/src/sti.o',
              'ORTHPOLxx/src/ORTHPOLPP.o']
    
    ext_modules = [ Extension('orthpol', 
                              ['src/PyORTHPOL.cpp'],
                              include_dirs = oxx_inc,
                              extra_compile_args = ['-g', '-O3'],
                              extra_link_args = oxx_ld + ['-lgfortran', '-g', '-O3']
                          )
                ]
    
    setup(
        name='orthpol',
        version = "0.2.14",
        license = "COPYING.LESSER",
        description = "Python wrapper for the ORTHPOL package",
        long_description=open("README.rst").read(),
        url="http://www2.compute.dtu.dk/~dabi/",
        author = "Daniele Bigoni",
        author_email = "dabi@dtu.dk",
        ext_modules = ext_modules,
        cmdclass={'install': orthpolxx_install,
                  'develop': orthpolxx_develop},
        include_dirs=include_dirs,
        zip_safe = False
    )

