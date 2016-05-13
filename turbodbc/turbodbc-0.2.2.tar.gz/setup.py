from setuptools import setup

import sys
import os
import os.path as op
import distutils.spawn as ds
import distutils.dir_util as dd
import distutils.sysconfig
import distutils

import itertools
from glob import iglob

def _get_source_files():
    iterable_sources = (iglob(os.path.join(root,'*.cpp')) for root, dirs, files in os.walk('src'))
    source_files = itertools.chain.from_iterable(iterable_sources)
    return list(source_files)

def _remove_strict_prototype_option_from_distutils_config():
    strict_prototypes = '-Wstrict-prototypes'
    config = distutils.sysconfig.get_config_vars()
    for key, value in config.iteritems():
        if strict_prototypes in str(value):
            config[key] = config[key].replace(strict_prototypes, '')

_remove_strict_prototype_option_from_distutils_config()


turbodbc_intern = distutils.core.Extension('turbodbc_intern',
                                           sources=_get_source_files(),
                                           include_dirs=['include/'],
                                           extra_compile_args=['--std=c++11'],
                                           libraries=['odbc', 'boost_python'])

setup(name = 'turbodbc',
      version = '0.2.2',
      description = 'turbodbc is a Python DB API 2.0 compatible ODBC driver',
      include_package_data = True,
      url = 'https://github.com/blue-yonder/turbodbc',
      author='Michael Koenig',
      author_email = 'michael.koenig@blue-yonder.com',
      packages = ['turbodbc'],
      classifiers = ['Development Status :: 4 - Beta',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: POSIX :: Linux',
                     'Programming Language :: C++',
                     'Programming Language :: Python :: 2.7',
                     'Topic :: Database'],
      ext_modules = [turbodbc_intern]
      )
