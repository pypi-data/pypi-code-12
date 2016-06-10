import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='fh-django-common',
    version='0.2.5',
    packages=['common'],
    include_package_data=True,
    description='A Django app to provide common functionality in Django projects',
    long_description=README,
    url='https://gitlab.com/futurehaus/django-common',
    tests_require=['Django'],
    test_suite='runtests.main',
)
