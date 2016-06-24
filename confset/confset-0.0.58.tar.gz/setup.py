#!/usr/bin/python
# Copyright (c) 2012-2015 Dwight Hubbard. All rights reserved.
# Licensed under the Apache License, Version 2.0.
# See the included License.txt file for details.

"""
Package configuration for confset module and utility
"""
import json
import os
from setuptools import setup


METADATA_FILENAME = 'confset/package_metadata.json'


def readme():
    with open('README.rst') as f:
        return f.read()


class Git(object):
    version_list = ['0', '7', '0']

    def __init__(self, version=None):
        if version:
            self.version_list = version.split('.')

    @property
    def version(self):
        """
        Generate a Unique version value from the git information
        :return:
        """
        git_rev = len(os.popen('git rev-list HEAD').readlines())
        if git_rev != 0:
            self.version_list[-1] = '%d' % git_rev
        version = '.'.join(self.version_list)
        return version

    @property
    def branch(self):
        """
        Get the current git branch
        :return:
        """
        return os.popen('git rev-parse --abbrev-ref HEAD').read().strip()

    @property
    def hash(self):
        """
        Return the git hash for the current build
        :return:
        """
        return os.popen('git rev-parse HEAD').read().strip()

    @property
    def origin(self):
        """
        Return the fetch url for the git origin
        :return:
        """
        for item in os.popen('git remote -v'):
            split_item = item.strip().split()
            if split_item[0] == 'origin' and split_item[-1] == '(push)':
                return split_item[1]


def get_and_update_metadata(version=None):
    """
    Get the package metadata or generate it if missing
    :return: The current package metadata
    """
    global METADATA_FILENAME
    global REDIS_SERVER_METADATA

    if not version:
        version = '.0.0.0'
    if not os.path.exists('.git') and os.path.exists(METADATA_FILENAME):
        with open(METADATA_FILENAME) as fh:
            metadata = json.load(fh)
    else:
        git = Git(version=version)
        metadata = {
            'git_version': git.version,
            'git_origin': git.origin,
            'git_branch': git.branch,
            'git_hash': git.hash,
            'version': git.version,
            'ci_build_number': os.environ.get('TRAVIS_BUILD_NUMBER', ''),
            'ci_tag': os.environ.get('TRAVIS_TAG', '')
        }
        with open(METADATA_FILENAME, 'w') as fh:
            json.dump(metadata, fh, indent=4)
    return metadata


if __name__ == "__main__":
    metadata = get_and_update_metadata('0.0.35')

    setup(
        name="confset",
        author="Dwight Hubbard",
        author_email="d@d-h.us",
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Information Technology',
            'Operating System :: POSIX',
            'Operating System :: POSIX :: Linux',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: BSD :: FreeBSD',
            'Operating System :: POSIX :: SunOS/Solaris',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        description="A simple script to change or update package configurations",
        license="Apache 2.0",
        long_description=open('README.rst').read(),
        packages=["confset"],
        package_data={
            'confset': ['package_metadata.json']
        },
        requires=['configobj'],
        scripts=['bin/confset'],
        url="http://github.com/dwighthubbard/confset",
        version=metadata['version'],
    )
