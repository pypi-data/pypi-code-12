import os
from distutils.core import setup
from setuptools import find_packages


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()


setup(
    name='chuck-norris-python',
    version='0.2',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    license='MIT',
    long_description=long_description,
    install_requires=['requests'],
    url='https://github.com/Keda87/chuck-norris-python',
    author='Adiyat Mubarak',
    author_email='adiyatmubarak@gmail.com'
)
