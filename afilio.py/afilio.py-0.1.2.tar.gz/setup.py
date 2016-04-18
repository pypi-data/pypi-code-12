#!/usr/bin/env python

from setuptools import setup

setup(name='afilio.py',
            version='0.1.2',
            description='Afilio API Client & Bindings',
            keywords="afilio.py is an afilio api client & bindings for accessing Sales & Leads API",
            author='Andre Pastore',
            author_email='andrepgs@gmail.com',
            url='https://github.com/apast/afilio.py',
            download_url='https://github.com/apast/afilio.py/tarball/0.1',
            packages=['afilioapi'],
            package_dir= {'': 'src/main/py/'}
           )
