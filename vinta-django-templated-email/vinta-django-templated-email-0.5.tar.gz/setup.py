#!/usr/bin/env python

from setuptools import setup
import sys
import os

DESCRIPTION = "A Django oriented templated / transaction email abstraction"

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

# python setup.py register

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    # print("You probably want to also tag the version now:")
    # print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    # print("  git push --tags")
    sys.exit()


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Framework :: Django',
]

setup(
    name='vinta-django-templated-email',
    version='0.5',
    packages=['templated_email', 'templated_email.backends'],
    author='Bradley Whittington',
    author_email='radbrad182@gmail.com',
    url='https://github.com/vintasoftware/django-templated-email',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'six',
    ],
)
