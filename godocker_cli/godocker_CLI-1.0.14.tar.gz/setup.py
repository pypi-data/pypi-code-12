#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import godockercli
import bin

setup(

    # name of the lib
    name='godocker_CLI',

    # version
    version='1.0.14',

    packages=find_packages(),

    author="Cyril MONJEAUD",

    description="CLI for godocker",

    long_description=open('README.md').read(),

    include_package_data=True,

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications",
    ],

    entry_points = {
        'console_scripts': [
            'godjob = bin.godjob:run',
            'godbatch = bin.godbatch:run',
            'godlogin = bin.godlogin:login',
            'goduser = bin.goduser:run',
            'godfile = bin.godfile:run',
            'godimage = bin.godimage:run',
            'godssh = bin.godssh:run',
            'godproject = bin.godproject:run',
        ],
    },
    install_requires = [
        'pyCLI>=2.0.3',
        'terminaltables>=1.0.2',
        'click',
        'requests>=2.7.0',
	    #'configparser',
    ],


    license="CECILL",

)
