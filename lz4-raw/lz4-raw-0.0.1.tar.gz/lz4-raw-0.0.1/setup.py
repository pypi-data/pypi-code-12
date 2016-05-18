#!/usr/bin/env python

from setuptools import setup, find_packages, Extension
import subprocess
import os
from distutils import ccompiler

VERSION = (0, 0, 1)
VERSION_STR = ".".join([str(x) for x in VERSION])
LZ4_VERSION = "r131"

# Use the bundled lz4 libs, and set the compiler flags as they
# historically have been set. We do set LZ4_VERSION here, since it
# won't change after compilation.
if ccompiler.get_default_compiler() == "msvc":
    extra_compile_args = ["/Ot", "/Wall"]
    define_macros = [("VERSION","\\\"%s\\\"" % VERSION_STR), ("LZ4_VERSION","\\\"%s\\\"" % LZ4_VERSION)]
else:
    extra_compile_args = ["-std=c99","-O3","-Wall","-W","-Wundef"]
    define_macros = [("VERSION","\"%s\"" % VERSION_STR), ("LZ4_VERSION","\"%s\"" % LZ4_VERSION)]

lz4mod = Extension('lz4_raw',
                   [
                       'src/lz4.c',
                       'src/python-lz4-raw.c'
                   ],
                   extra_compile_args=extra_compile_args,
                   define_macros=define_macros,
)


setup(
    name='lz4-raw',
    version=VERSION_STR,
    description="Raw Python Bindings for LZ4",
    long_description=open('README.rst', 'r').read(),
    author='Haohui Mai',
    author_email='haohui.mai@gmail.com',
    url='https://github.com/haohui/python-lz4-raw',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    ext_modules=[lz4mod,],
    tests_require=["nose>=1.0"],
    test_suite = "nose.collector",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
