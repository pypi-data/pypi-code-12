import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

version = __import__('django_toolset').__version__

setup(
    name='django-toolset',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A set of helper functions and utilities for a Django application',
    download_url = 'https://github.com/codezeus/django-toolset/tarball/0.1.3',
    long_description=README,
    url='https://github.com/codezeus/django-toolset',
    author='Dan Sackett',
    author_email='danesackett@gmail.com',
    tests_require=['Django', 'pytest', 'coverage', 'mock'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
)
