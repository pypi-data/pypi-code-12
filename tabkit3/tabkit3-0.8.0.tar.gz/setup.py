#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="tabkit3",
    version="0.8.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            'tcat = tabkit.scripts:cat',
            'tcut = tabkit.scripts:cut',
            'tsrt = tabkit.scripts:sort',
            'tjoin = tabkit.scripts:join',
            'tmap_awk = tabkit.scripts:map',
            'tgrp_awk = tabkit.scripts:group',
            'tpretty = tabkit.scripts:pretty'
        ]
    },
    author="Dmitriy Zhiltsov",
    author_email="dzhiltsov@me.com",
    description="Coreutils-like kit for headed tab-separated files processing",
    license="PSF",
    url="https://github.com/zaabjuda/tabkit3",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
