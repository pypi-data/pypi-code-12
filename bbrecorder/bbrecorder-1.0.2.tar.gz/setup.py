#!/bin/env python
# -*- coding: utf-8 -*-
# Author: Laurent Pointal <laurent.pointal@limsi.fr> <laurent.pointal@laposte.net>

from distutils.core import setup
import sys
import io

setup(
    name='bbrecorder',
    version='1.0.2',
    author='Laurent Pointal',
    author_email='laurent.pointal@limsi.fr',
    url='https://perso.limsi.fr/pointal/dev:bbrecorder',
    download_url='https://sourcesup.renater.fr/projects/bbrecorder/',
    description='Black box style logging handler to delay logs emitting to crisis situation.',
    py_modules=['bbrecorder'],
    keywords=['logging','record','black','box'],
    license='New BSD License',
    classifiers=[
                'Development Status :: 5 - Production/Stable',
                'Intended Audience :: Science/Research',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Programming Language :: Python :: 2',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.3',
                'License :: OSI Approved :: BSD License',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Topic :: System :: Logging',
             ],
    long_description=io.open("README.txt", encoding='utf-8').read(),
    )

