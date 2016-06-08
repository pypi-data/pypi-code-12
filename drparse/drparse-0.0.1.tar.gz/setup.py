# -*- coding: utf-8 -*-

import os
import codecs
import uuid

from setuptools import setup
from pip.req import parse_requirements

def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()

setup(
    name='drparse',
    author='Tim van der Hulst',
    author_email='tim.vdh@gmail.com',
    version='0.0.1',
    url='https://github.com/hampsterx/drparse',
    install_requires=[str(ir.req) for ir in parse_requirements('requirements.txt', session=uuid.uuid4())],
    py_modules=['drparse'],
    license=read('LICENSE'),
    description='Parse dates out of a textual string',
    long_description=read('README.md'),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ]
)