# -*- coding: utf-8 -*-
"""setup.py."""
from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    'requests>=2.9.1',
    'lxml>=3.6.0'
]
VERSION = '0.0.8'

setup(
    name='smskit',
    version=VERSION,
    description='Abstack sms utils component.',
    author='abstack',
    author_email='mzj@abstack.com',
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='http://www.abstack.com/',
    keywords='smskit is a sms utils!'
)
