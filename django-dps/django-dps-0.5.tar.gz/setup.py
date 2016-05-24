#!/usr/bin/env python

import os

from setuptools import setup, find_packages

# if there's a converted (rst) readme, use it, otherwise fall back to markdown
if os.path.exists('README.rst'):
    readme_path = 'README.rst'
else:
    readme_path = 'README.md'

# avoid importing the module
exec(open('dps/_version.py').read())

setup(
    name='django-dps',
    version=__version__,
    packages=find_packages(),
    license='BSD License',
    url="https://github.com/gregplaysguitar/django-dps/",

    maintainer="Greg Brown",
    maintainer_email="greg@gregbrown.co.nz",

    description='Django integrations for the DPS payment gateway',
    long_description=open(readme_path).read(),

    install_requires=[
        'Django>=1.7',
    ],

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
