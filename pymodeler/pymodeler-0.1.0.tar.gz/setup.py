import sys
import os
try: 
    from setuptools import setup, find_packages
except ImportError: 
    from distutils.core import setup
    def find_packages():
        return []

import versioneer

if sys.version_info[:2] < (2, 7):
    raise RuntimeError("Python version >= 2.7 required.")

NAME = 'pymodeler'
CLASSIFIERS = """\
Development Status :: 2 - Pre-Alpha
Intended Audience :: Science/Research
Intended Audience :: Developers
Programming Language :: Python
Natural Language :: English
Topic :: Scientific/Engineering
"""
URL = 'https://github.com/kadrlica/pymodeler'
DESCR = "Infrastructure for creating parametrized models in python."
LONG_DESCR = "See %s for more details."%URL

setup(
    name=NAME,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url=URL,
    author='Alex Drlica-Wagner',
    author_email='kadrlica@fnal.gov',
    scripts = [],
    install_requires=[
        'numpy >= 1.9.0',
        'pyyaml >= 3.10',
    ],
    packages=find_packages(),
    package_data={},
    description=DESCR,
    long_description=LONG_DESCR,
    platforms='any',
    classifiers = [_f for _f in CLASSIFIERS.split('\n') if _f]
)
