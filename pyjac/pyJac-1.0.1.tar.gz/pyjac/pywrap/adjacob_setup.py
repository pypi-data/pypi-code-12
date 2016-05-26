#! /usr/bin/env python2.7
from distutils.core import setup, Extension
import distutils.ccompiler

from Cython.Distutils import build_ext
from Cython.Build import cythonize
import parallel_compiler as pcc
import numpy
import os

sources = ['/Users/kyle/Dropbox/Research/Code/pyJac/pyjac/pywrap/adjacob_wrapper.pyx']
includes = ['/Users/kyle/Dropbox/Research/Code/pyJac/out/', '/Users/kyle/Dropbox/Research/Code/pyJac/pyjac/pywrap/']

distutils.ccompiler.CCompiler.compile = pcc.parallel_compile

os.environ["CC"] = "g++"
os.environ["CXX"] = "g++"

ext = [Extension("adjacob",
     sources=sources,
     include_dirs=includes + [numpy.get_include()],
     extra_compile_args=['-frounding-math', '-fsignaling-nans',
                         '-DADEPT_STACK_THREAD_UNSAFE', '-fopenmp'],
     language='c++',
     libraries=['adept'],
     extra_link_args=['-fopenmp'],
     extra_objects=[os.path.join('build/temp.macosx-10.11-x86_64-2.7', '/Users/kyle/Dropbox/Research/Code/pyJac/build/temp.macosx-10.11-x86_64-2.7/libad_pyjac.a')]
     )]

setup(
    name='adjacob',
    ext_modules=ext,
    cmdclass={'build_ext': build_ext},
)
