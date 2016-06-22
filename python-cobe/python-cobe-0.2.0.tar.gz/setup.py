"""Setup script for the Cobe Python library."""

import pathlib

import setuptools


PROJECT = pathlib.Path(__file__).resolve().parent


setuptools.setup(
    name='python-cobe',
    version='0.2.0',
    packages=['cobe'],
    author='Abilisoft Ltd.',
    author_email='info@cobe.io',
    url='https://cobe.io/',
    description=('A library to enable streaming of custom '
                 'entities to Cobe.io from within any Python applications'),
    long_description=(PROJECT / 'README.rst').open().read(),
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Monitoring',
    ],
    install_requires=[
        'pyzmq >=14.7, <15.0',
        'msgpack-python >=0.4.5, <0.5',
        'voluptuous >=0.8.7, <0.9',
    ],
)
