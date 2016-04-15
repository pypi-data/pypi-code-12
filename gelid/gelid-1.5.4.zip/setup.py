# -*- coding: utf-8 -*-
# Created by lvjiyong on 15/3/16
from os.path import dirname, join
from setuptools import setup, find_packages

with open(join(dirname(__file__), 'VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

setup(
    name="gelid",
    version=version,
    description=u"gelid专注中文网页内容抽取",
    author="lvjiyong",
    url="https://github.com/lvjiyong/python-gelid",
    license="Apache2.0",
    long_description=open('README.md').read(),
    maintainer='lvjiyong',
    platforms=["any"],
    maintainer_email='lvjiyong@gmail.com',
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'six',
        'lxml',
        'enum34',
        'readability-lxml',
        'jieba',
        'chardet',
        'gelid-http',
        'BeautifulSoup'
    ],
)