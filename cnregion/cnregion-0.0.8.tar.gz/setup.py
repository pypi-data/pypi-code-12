# coding: utf-8


from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cnregion',

    version='0.0.8',

    description='China region utils',
    long_description=long_description,

    url='https://github.com/xiachufang/cnregion',

    # Author details
    author='cadl',
    author_email='cadl@xiachufang.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['simplejson'],
    keywords='china region',
    include_package_data=True
)
