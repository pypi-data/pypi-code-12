import os
from setuptools import setup, find_packages


NAME = 'bitpack'
VERSION = '0.1'


def read(fname):
        """ Return content of specified file """
        return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name=NAME,
    description='Python data-binary serialization / deserialization library.',
    keywords='bitpack serialization deserialization',
    version=VERSION,
    author='Outernet Inc',
    author_email='apps@outernet.is',
    license='GPLv3',
    url='https://github.com/Outernet-Project/bitpack',
    long_description=read('README.rst'),
    packages=find_packages(),
    install_requires=[
        'bitarray',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)
