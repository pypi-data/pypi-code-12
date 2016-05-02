# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages


setup(
    name='bergholm-api-client',
    version='0.0.1',
    author=u'Mohammed Hammoud',
    author_email='mohammed@iktw.se',
    packages=find_packages(),
    url='https://github.com/iktw/bergholm-api-client',
    license='MIT licence, see LICENSE',
    description='Simple Client to fetch products from http://www.bergholm.com/',
    long_description=open('README.md').read(),
    zip_safe=False,
    include_package_data=True,
    install_requires=None
)
