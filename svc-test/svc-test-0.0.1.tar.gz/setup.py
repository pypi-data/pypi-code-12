#!/usr/bin/env python
# encoding: utf-8
# auth: ywt

from setuptools import setup, find_packages


setup(
    name='svc-test',
    version='0.0.1',
    keywords=('svc', 'test', 'egg'),
    description='svc test',
    license='MIT License',

    url='http://svc.sogou',
    author='ywt',
    author_email='yinwentao@sogou-inc.com',

    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=[],
)
