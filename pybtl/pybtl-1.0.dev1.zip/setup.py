import os
from setuptools import setup, find_packages


def read(fname):
        """ Return content of specified file """
        return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='pybtl',
    description=('Library for serializing python objects as tightly packed '
                 'bit arrays'),
    keywords='binary serialization deserialization bits',
    version='1.0.dev1',
    author='Outernet Inc',
    author_email='apps@outernet.is',
    license='BSD',
    url='https://github.com/Outernet-Project/pybtl',
    long_description=read('README.rst'),
    packages=find_packages(),
    install_requires=[
        'bitarray',
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)
