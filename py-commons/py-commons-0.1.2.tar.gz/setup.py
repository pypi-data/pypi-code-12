import os
from setuptools import setup
from commons.testing import PyTest

try:
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        required = f.read().splitlines()
except IOError:
    required = []

setup(
    name='py-commons',
    version='0.1.2',
    packages=['commons'],
    package_dir={'commons': 'commons'},
    url='',
    license='',
    install_requires=required,
    cmdclass={'test': PyTest},
    author='Data Science',
    author_email='DataScience@pulsepoint.com',
    description='A set of useful utils for data analysis'
)
