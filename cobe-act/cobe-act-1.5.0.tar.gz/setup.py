"""Distutils build script for the act package."""

from setuptools import setup


__version__ = '1.5.0'


setup(
    name='cobe-act',
    version=__version__,
    author='cobe.io',
    author_email='info@cobe.io',
    license='LGPLv3',
    url='http://bitbucket.org/cobeio/act',
    description='A collection of common tools for cobe.io.',
    packages=['act'],
    install_requires=[
        'setuptools',
        'apipkg',
        'msgpack-python',
        'Logbook',
        'pyzmq',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: Other/Proprietary License',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
