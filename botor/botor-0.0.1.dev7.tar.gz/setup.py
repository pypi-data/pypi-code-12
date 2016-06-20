"""
Botor
=====

A thin wrapper around boto3

:copyright: (c) 2016 by Netflix, see AUTHORS for more
:license: Apache, see LICENSE for more details.
"""
import sys
import os.path

from setuptools import setup, find_packages

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

# When executing the setup.py, we need to be able to import ourselves.  This
# means that we need to add the src/ directory to the sys.path

sys.path.insert(0, ROOT)

about = {}
with open(os.path.join(ROOT, "botor", "__about__.py")) as f:
    exec(f.read(), about)

install_requires = [
    'boto3>=1.2.3',
    'boto>=2.39.0',
    'joblib>=0.9.4'
]

tests_require = []

docs_require = []

dev_require = []

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__email__"],
    url=about["__uri__"],
    description=about["__summary__"],
    long_description=open(os.path.join(ROOT, 'README.md')).read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
        'docs': docs_require,
        'dev': dev_require
    }
)