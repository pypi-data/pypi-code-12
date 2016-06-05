#!/usr/bin/env python3
__VERSION__ = '0.2.2'

from setuptools import setup, find_packages


def long_desc():
    with open('README.rst') as file:
        return file.read()


setup(
    name='ch_solutions',
    version=__VERSION__,
    long_description=long_desc(),
    classifiers=[
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
    keywords='CloudHigh ch_solutions tools shortcuts',
    url='https://gitlab.com/cloudhigh/ch_solutions',
    author='Buck Brady',
    author_email='bbrady@cloudhigh.solutions',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'PyMySQL',
        'requests',
    ],
    # test_suite='nose.collector',
    # tests_require=[
    #     'nose',
    #     'nose-cover3',
    # ],
    # entry_points = [],
    # include_package_data = True,
)
