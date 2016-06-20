"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import sys
import os

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

datafiles = []


def list_directories (initial, d):

    for root, dirs, files in os.walk(initial):
        print (root)
        if '/.' in root or '\\.' in root:
            continue
        for current_file in files:
            if current_file[0] == '.':
                continue
            path = root [7:]
            d.append(os.path.join (path,current_file))


def get_revision():
    i = 0
    revision = '0'
    for arg in sys.argv:
        if arg.startswith ('--revision='):
            sys.argv.pop(i)
            revision = arg [len('--revision='):]
            return revision
        i = i + 1
    return revision


list_directories('wagent/php',datafiles)

arg_revision = get_revision()
package_author = 'Vinicius Jarina'
package_version = None

if arg_revision != '0':
    package_version = '1.0.' + arg_revision
    with open(path.join(here,'wagent','__init__.py'), "w", encoding='utf-8') as init_file:
        init_file.write("__version__ = \"{0}\"\n".format(package_version))
        init_file.write("__author__ = \"{0}\"\n".format(package_author))
else:
    with open(path.join(here,'wagent','__init__.py'), "r", encoding='utf-8') as init_file:
        line = init_file.readline ().strip()
        package_version = line [len("__version__ = \""):-1]

setup(
    name='wagent',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=package_version,
    description='Windu message agent',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/codefoco/wagent',

    # Author details
    author=package_author,
    author_email='viniciusjarina@gmail.com',
    packages = find_packages(),
    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='sample setuptools development',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    #install_requires=['peppercorn'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'wagent': datafiles
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'


    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
