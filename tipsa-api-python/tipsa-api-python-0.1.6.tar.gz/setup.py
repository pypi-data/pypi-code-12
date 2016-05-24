# coding=utf-8
"""
Tipsa API setup
"""
__copyright__ = 'Copyright 2015, Abalt'

from setuptools import setup, find_packages

# Dynamically calculate the version based on tipsa.VERSION.
VERSION = __import__('tipsa').get_version()


setup(
    name='tipsa-api-python',
    version=VERSION,
    url='https://bitbucket.org/abalt/tipsa-api-python',
    author='Abalt',
    author_email='admin@abalt.org',
    description=(
        "Create packages to send using TIPSA API."),
    long_description=open('README.rst').read(),
    keywords="TIPSA, Shipping",
    license=open('LICENSE').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests',
                      'xmltodict'],
    download_url='https://bitbucket.org/abalt/tipsa-api-python/get/0.1.6.zip',
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Other/Nonlisted Topic'],
)
