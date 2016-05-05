#!/usr/bin/env python

import codecs
from setuptools import setup, find_packages

install_requires = [
    'django-nose',
    'sbo-selenium>=0.4.0',
]

version = '1.6.1'  # Update docs/CHANGELOG.rst if you increment the version

with codecs.open('README.rst', 'r', 'utf-8') as f:
    long_description = f.read()

setup(
    name="django-nose-qunit",
    version=version,
    author="Jeremy Bowman",
    author_email="jbowman@safaribooksonline.com",
    description="Integrate QUnit JavaScript tests into a Django test suite via nose",
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Testing',
    ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    url='https://github.com/safarijv/django-qunit-ci',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'nose.plugins.0.10': [
            'django-qunit = django_nose_qunit.nose_plugin:QUnitPlugin',
            'django-qunit-index = django_nose_qunit.nose_plugin:QUnitIndexPlugin'
        ]
    },
)
