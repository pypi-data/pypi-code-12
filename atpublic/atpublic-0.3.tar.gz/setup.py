# Copyright (C) 2016 Barry Warsaw
#
# This project is licensed under the terms of the Apache 2.0 License.  See
# LICENSE.txt for details.

from setup_helpers import get_version, long_description, require_python
from setuptools import setup, find_packages, Extension

require_python(0x30400f0)
__version__ = get_version('public/__init__.py')


setup(
    name='atpublic',
    version=__version__,
    description='public -- @public for populating __all__',
    long_description=long_description('README.rst'),
    author='Barry Warsaw',
    author_email='barry@python.org',
    license='Apache 2.0',
    url='https://gitlab.com/warsaw/public',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'flake8.extension': ['B40 = public.tests.flake8:ImportOrder'],
        },
    ext_modules=[Extension('_public', ['src/public.c'])],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        ]
    )
