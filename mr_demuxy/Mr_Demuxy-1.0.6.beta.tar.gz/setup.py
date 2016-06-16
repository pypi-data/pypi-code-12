'''
#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
'''

import os

from setuptools import setup
from setuptools import find_packages



def file_path_joiner(file_dir):
    files_list = os.listdir(file_dir)
    corrected_file_path = []
    for cur_file in files_list:
        cur_fp = os.path.join(file_dir, cur_file)
        corrected_file_path.append(cur_fp)
    return corrected_file_path

script_files = file_path_joiner('bin')

#from distutils.core import setup

setup(
    name = 'Mr_Demuxy',
    version = '1.0.6.beta',
    description = 'demultiplexs combinatorially tagged reads',

    author = 'Daniel E. Lefever',
    author_email = 'lefeverde@gmail.com',
    
    packages = find_packages(),
    scripts = script_files,

    #package_dir = {
    #'Mr_Demuxy': 'lib',
    #},
    #entry_points={
    #    'console_scripts': [
    #        'pe_dem = mr_demuxy.pe_demuxer_dist.main_loop',
    #    ]
    #},
    package_data = {
    'Mr_Demuxy': ['example_data/example*'],
    'Mr_Demuxy': ['example_data/*.txt']
    },
    #py_modules = ['alias_maker'],
    #data_files = [
    #('Mr_Demuxy', ['MANIFEST.in']),
    #('', ['LICENSE/biopython_license.txt'])],
    

    
    
    license = 'MIT',
    platforms = 'any',
    classifiers = [
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        ]
    
    
    )