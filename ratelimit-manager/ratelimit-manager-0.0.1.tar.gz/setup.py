# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ratelimit-manager',
    version='0.0.1',
    description='ratelimit manager',
    author='Tomotaka Ito',
    author_email='tomotaka.ito@gmail.com',
    url='https://github.com/tomotaka/ratelimit-manager',
    packages=find_packages(),
    license='MIT License',
    include_package_data=True,
    install_requires=['numpy'],
    tests_require=['nose'],
    test_suite='nose.collector'
)
