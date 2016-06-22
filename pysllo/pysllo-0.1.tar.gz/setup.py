from distutils.core import setup

# hack for vagrant based environment
import os
del os.link

setup(
    name='pysllo',
    version='0.1',
    packages=['pysllo'],
    url='http://pysllo.readthedocs.io/',
    license='BSD',
    author='kivio',
    author_email='kivio@kivio.pl',
    description='Make your python logging more '
                'structured and easy to aggregate'
)
