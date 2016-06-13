# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

from aboutconfig import __version__

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    with open(os.path.join(BASE_DIR, 'README.md')) as fp:
        long_description = fp.read()

setup(
    name='django-aboutconfig',
    version='.'.join(str(s) for s in __version__),
    url='https://bitbucket.org/impala/django-aboutconfig',
    license='GPLv3+',
    description='A firefox-like about:config implementation for one-off settings in Django apps.',
    long_description=long_description,
    keywords=['django', 'library', 'configuration'],
    author='Kirill Stepanov',
    author_email='mail@kirillstepanov.me',
    packages=find_packages(),
    data_files=[('', ['LICENSE.txt', 'README.md'])],
    download_url='https://bitbucket.org/impala/django-aboutconfig/get/0.1.0.tar.gz',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'Django>=1.8',
        'six'
    ],
    include_package_data=True,
    zip_safe=False,
)
