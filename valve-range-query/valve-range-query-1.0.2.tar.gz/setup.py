"""
Python library for Query of Valve Servers over a range of IPs

"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='valve-range-query',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.2',

    description='Python library for Query of Valve Servers over a range of IPs',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/anshulshah96/valve-range-query',

    # Author details
    author='Anshul Shah',
    author_email='anshulshah96@gmail.com',

    packages = ['valve-range-query'],


    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
    ],

    keywords='valve query servers counter strike',

)