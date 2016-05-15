#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='ufs-tools',
    version='0.5.0',
    description="Some functions can be used during python development",
    long_description=readme + '\n\n' + history,
    author="Wang Richard",
    author_email='richardwangwang@gmail.com',
    url='https://github.com/weijia/ufs-tools',
    packages=[
        'ufs_tools',
        'ufs_tools.short_decorator'
    ],
    package_dir={'ufs_tools': 'ufs_tools',
                 'ufs_tools.short_decorator':
                     'ufs_tools/short_decorator'
                 },
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='ufs_tools',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
