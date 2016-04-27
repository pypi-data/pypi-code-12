#from setuptools import setup
from distutils.core import setup
setup(name='thLib',
    version='0.11.9',
    description='Collection of Python utilities for signal analysis',
    long_description=open('README.txt').read(),
    license = 'http://opensource.org/licenses/BSD-2-Clause',
    author='Thomas Haslwanter',
    author_email='thomas.haslwanter@fh-linz.at',
    url='http://work.thaslwanter.at',
    package_dir={'': '.'},
    packages=['thLib'],
)
