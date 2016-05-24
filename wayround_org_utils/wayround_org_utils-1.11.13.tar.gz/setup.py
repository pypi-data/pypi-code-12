#!/usr/bin/python3

import subprocess
import os.path

from setuptools import setup
from setuptools import Extension


py_compil_args = None
py_link_args = None

p = subprocess.Popen(
    ['pkg-config', '--cflags', 'python3'], stdout=subprocess.PIPE)
p.wait()
py_compile_args = str(p.communicate()[0], encoding='utf-8').split()

p = subprocess.Popen(
    ['pkg-config', '--libs', 'python3'], stdout=subprocess.PIPE)
p.wait()
py_link_args = str(p.communicate()[0], encoding='utf-8').split()




setup(
    name='wayround_org_utils',
    version='1.11.13',
    description='Various service modules',
    long_description="""\
This package contains various useful modules functions and classes.

""",

    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_org_utils',
    install_requires=[
        'wayround_org_mail',
        'regex'
        ],
    packages=[
        'wayround_org.utils',
        'wayround_org.utils.format'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        ],
    ext_modules=[
        Extension(
            "wayround_org.utils.format.elf_bin",
            ["wayround_org/utils/format/elf_bin.c"],
            extra_compile_args=py_compile_args,
            extra_link_args=py_link_args,
            ),
        ] ,
    package_data={
        'wayround_org.utils': [
            'config.sub',
            os.path.join('format', '*.c'),
            os.path.join('format', '*.h')
            ]
        }
    )
