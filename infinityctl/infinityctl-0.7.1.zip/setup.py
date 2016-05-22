#!/usr/bin/env python

from setuptools import setup

setup(
    name='infinityctl',
    version='0.7.1',
    packages=['infinityctl'],
    url='https://bitbucket.org/Unicode4all/infinityctl',
    license='BSD-3-Clause',
    author='Unicode4all Foundation',
    author_email='anthon@unicode4all.org',
    description='Infinity Station 13 server management tool',
    long_description='A Space Station 13 server management tool'
                     ' primarily intended to use with russian SS13 server Infinity',
    platforms='POSIX',
    install_requires=[
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'infinityctl = infinityctl.__main__:main'
        ]
    },
    data_files=[
        ('/etc/infinityctl', ['infinityctl/cfg/config.yml'])
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
        'Natural Language :: Russian'
    ]
)
