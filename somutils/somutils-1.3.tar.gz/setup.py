#!/usr/bin/python3
#-*- coding: utf8 -*-

from setuptools import setup

readme = open("README.rst").read()

setup(
    name = "somutils",
    version = "1.3",
    description = "Tools we use at Somenergia and can be useful",
    author = "César López Ramírez",
    author_email = "cesar.lopez@somenergia.coop",
    url = 'https://github.com/Som-Energia/somenergia-utils',
    long_description = readme,
    license = 'GNU General Public License v3 or later (GPLv3+)',
    py_modules = [
        "sheetfetcher",
        "dbutils",
        ],
    scripts=[
        'venv',
        'activate_wrapper.sh',
        'sql2csv.py',
        ],
    install_requires=[
        'yamlns',
        'psycopg2',
        'consolemsg',
        'gspread',
        'oauth2client>=2.0',
        'PyOpenSSL',
        ],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
)

