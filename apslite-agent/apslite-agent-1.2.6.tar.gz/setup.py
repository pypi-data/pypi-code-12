#!/usr/bin/env python

import os
import time
from os.path import abspath, dirname, join

from apslite_agent.constants import PACKAGE_NAME

from setuptools import find_packages, setup

PACKAGE_VERSION = '1.2'
PACKAGE_AUTHOR = 'APS Lite team'


def version():
    path_version = join(dirname(abspath(__file__)), 'version.txt')

    def version_file(mode='r'):
        return open(path_version, mode)

    if os.path.exists(path_version):
        with version_file() as verfile:
            return verfile.readline().strip()

    if os.getenv('TRAVIS'):
        build_version = os.getenv('TRAVIS_BUILD_NUMBER')
    elif os.getenv('JENKINS_HOME'):
        build_version = 'jenkins{}'.format(os.getenv('BUILD_NUMBER'))
    else:
        build_version = 'dev{}'.format(int(time.time()))

    with version_file('w') as verfile:
        verfile.write('{0}.{1}'.format(PACKAGE_VERSION, build_version))

    with version_file() as verfile:
        return verfile.readline().strip()


def parse_requirements(requirements):
    with open(requirements) as f:
        return [l.strip('\n') for l in f if l.strip('\n') and not l.startswith('#')]


reqs = parse_requirements(join(dirname(__file__), 'requirements.txt'))

setup(
    name=PACKAGE_NAME,
    version=version(),
    author=PACKAGE_AUTHOR,
    author_email='aps@odin.com',
    url='http://aps.odin.com',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=reqs,
    entry_points={
        'console_scripts': ['apslite-agent = apslite_agent.main:main']
    },
)
