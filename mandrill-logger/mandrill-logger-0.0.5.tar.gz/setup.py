# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='mandrill-logger',
    version='0.0.5',
    author=u'Will & Skill',
    author_email='info@willandskill.se',
    packages=find_packages(),
    url='https://github.com/willandskill/mandrill_logger',
    license='MIT licence, see LICENCE.txt',
    description='Django logging for Mandrill',
    long_description=open('README.md').read(),
    zip_safe=False,
    include_package_data=True
)
