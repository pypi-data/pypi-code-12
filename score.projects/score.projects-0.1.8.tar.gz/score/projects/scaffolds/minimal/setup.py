import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

setup(
    name='__PACKAGE_NAME__',
    version='0.0.1',
    long_description=README,
    author='strg.at',
    author_email='score@strg.at',
    url='http://score-framework.org',
    keywords='score framework projects loader',
    packages=['__PACKAGE_NAME__'],
    zip_safe=False,
    license='LGPL',
    install_requires=[
        'score.init',
    ],
)
