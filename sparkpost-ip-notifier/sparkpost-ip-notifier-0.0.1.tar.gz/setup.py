# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages


INSTALL_REQUIREMENTS = [
    'requests>=2.9.1',
    'sparkpost>=1.2.0'
]

setup(
    name='sparkpost-ip-notifier',
    version='0.0.1',
    author=u'Mohammed Hammoud',
    author_email='mohammed@iktw.se',
    packages=find_packages(),
    url='https://github.com/iktw/sparkpost-ip-notifier',
    license='MIT licence, see LICENSE',
    description='Package to notify you by email when your External IP has changed.',
    long_description=open('README.md').read(),
    zip_safe=False,
    include_package_data=True,
    install_requires=INSTALL_REQUIREMENTS
)
