#!/usr/bin/env python3

import ast
import os
from pathlib import Path
import sys
from setuptools import setup


class MetadataFinder(ast.NodeVisitor):
    def __init__(self):
        self.version = None
        self.summary = None
        self.author = None
        self.email = None
        self.uri = None
        self.licence = None

    def visit_Assign(self, node):
        if node.targets[0].id == '__version__':
            self.version = node.value.s
        elif node.targets[0].id == '__summary__':
            self.summary = node.value.s
        elif node.targets[0].id == '__author__':
            self.author = node.value.s
        elif node.targets[0].id == '__email__':
            self.email = node.value.s
        elif node.targets[0].id == '__uri__':
            self.uri = node.value.s
        elif node.targets[0].id == '__license__':
            self.license = node.value.s

with Path('python_xirsys', '__init__.py').open() as open_file:
    finder = MetadataFinder()
    finder.visit(ast.parse(open_file.read()))

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (finder.version, finder.version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
changes = open('CHANGES.rst').read().replace('.. :changelog:', '')

INSTALL_REQUIRES = [
    'requests~=2.10',
]

setup(
    name='python-xirsys',
    version=finder.version,
    description=finder.summary,
    long_description=readme + '\n\n' + changes,
    author=finder.author,
    author_email=finder.email,
    url=finder.uri,
    packages=[
        'python_xirsys',
    ],
    package_dir={'python_xirsys': 'python_xirsys'},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    license=finder.license,
    zip_safe=False,
    keywords='xirsys',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
