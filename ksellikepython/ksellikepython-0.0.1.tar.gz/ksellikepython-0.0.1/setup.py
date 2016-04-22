# coding:utf-8

import sys
from setuptools import setup, find_packages

bin_scripts = ['bin/ksel']

setup(
    name = 'ksellikepython',
    version = '0.0.1',
    description = 'Command Line Tool for ksellesk.',
    long_description = open('README.md', 'rb').read().decode('utf-8'),
    keywords = 'ksel',
    author = 'Daniel Zheng',
    author_email = '296376717@qq.com',
    url = 'http://egghurts.com',
    scripts = bin_scripts,
    packages = find_packages('.'),
    package_dir = {'ksellikepython': 'qingstor'},
    include_package_data = True,
)
