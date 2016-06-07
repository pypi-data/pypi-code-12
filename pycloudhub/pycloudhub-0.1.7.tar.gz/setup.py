"""
CloudHub API Wrapper
====================

An initial attempt at an implementation of the MuleSoft CloudHub API in Python.

See `Official API Documentation <http://www.mulesoft.org/documentation/display/current/API>`_.
"""
from setuptools import setup, find_packages

setup(
    name='pycloudhub',
    version='0.1.7',
    description='A CloudHub API wrapper written in python',
    long_description=__doc__,
    url='https://bitbucket.org/pgolec/pycloudhub',
    author='Patrick Golec',
    author_email='pgolec+pypi@gmail.com',
    license='BSD',

    classifiers=[
        # Project maturity
        'Development Status :: 3 - Alpha',

        # Environment
        'Environment :: Console',
        'Environment :: Other Environment',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Python version
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='cloud cloudhub mule mulesoft',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['requests', 'bigpy>=0.1.1'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'httpretty'],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'cloudhub=cloudhub.cli:main',
        ],
    },
)
