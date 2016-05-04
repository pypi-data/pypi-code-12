# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'requests>=2.9.1',
    'lxml>=3.6.0'
]
VERSION = '0.0.5'

setup(
    name='smskit',
    version=VERSION,
    description='Abstack sms utils component.',
    author='abstack',
    author_email='mzj@abstack.com',
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='http://www.abstack.com/',
    keywords='smskit is a sms utils!'
)
