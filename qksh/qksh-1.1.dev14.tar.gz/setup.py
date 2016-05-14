#!/usr/bin/env python

# example: https://github.com/pypa/sampleproject
from setuptools import setup

setup(
    name='qksh',
    version='1.1.dev14',
    description='A CLI utility working with F5 iHealth GUI'
                'for uploading and downloading files/commands etc.',
    url='https://github.com/ccorzlol/handy_qkview',
    license='MIT',
    author='Qiang He',
    author_email='abc89d@gmail.com',
    packages=['qksh'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Information Technology',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'args>=0.1.0',
        'clint>=0.5.1',
        'logging>=0.4.9.6',
        'lockfile>=0.12.2',
        'requests>=2.9.1',
        'requests-toolbelt>=0.6.0',
        'wheel>=0.29.0',
        'python-daemon>=2.1.1',
        'setproctitle>=1.1.10'
    ],
    keywords='qkview ihealth',
    entry_points={
        'console_scripts': [
            'qksh = qksh.qksh:main'
        ]
    },
)
