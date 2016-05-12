# coding:utf-8

import sys
from setuptools import setup, find_packages

setup(
    name = 'testqsctl',
    version = '1.3',
    description = 'Advanced command line tool for QingStor.',
    long_description = open('README.md', 'rb').read().decode('utf-8'),
    keywords = 'qingcloud qingstor qsctl',
    author = 'Daniel Zheng',
    author_email = 'daniel@yunify.com',
    url = 'https://docs.qingcloud.com',
    scripts = ['bin/qsctl', 'bin/qsctl.cmd'],
    packages = find_packages('.'),
    package_dir = {'qsctl': 'qingstor',},
    namespace_packages = ['qingstor',],
    include_package_data = True,
    install_requires = [
        'argparse >= 1.1',
        'PyYAML >= 3.1',
        'qingcloud-sdk >= 1.0.2',
    ]
)
