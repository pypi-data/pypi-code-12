#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

requirements = [
    'pysam',
    'biopython',
]

setup(
    name='sam2fasta',
    version='0.1.0',
    description="Simple script to convert sam file to fasta format.",
    author="Michal Hozza",
    author_email='mhozza@gmail.com',
    url='https://github.com/mhozza/sam2fasta',
    packages=[
        'sam2fasta',
    ],
    package_dir={'sam2fasta':
                 'sam2fasta'},
    entry_points={
        'console_scripts': ['sam2fasta=sam2fasta.sam2fasta:run'],
    },
    install_requires=requirements,
    license="ISCL",
    zip_safe=True,
    keywords='sam2fasta',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
)
