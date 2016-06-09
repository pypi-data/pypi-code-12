# -*- coding: utf-8 -*-
from setuptools import setup

try:
    long_description = open('README.rst', 'rt').read()
except Exception:
    long_description = ""

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="cfblog",
    description="Awesome CMS for Django",
    long_description=long_description,

    version="0.2.6",
    author='Vinay Karanam, Ashish Nayan',
    author_email="vinayinvicible@gmail.com, nayanashish@gmail.com",

    url='https://github.com/Coverfox/cfblog/',
    license='BSD',

    install_requires=requirements,
    packages=['cfblog', 'cfblog.migrations'],
    include_package_data=True,

    zip_safe=True,
)
