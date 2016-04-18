#!/usr/bin/env python
"""
sentry-hal
==============

An extension for Sentry which integrates with a JSON based XMPP chat bot.

:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages


tests_require = [
    'nose>=1.1.2',
]

install_requires = [
    'sentry>=8.3.2',
]

setup(
    name='sentry-hal',
    version='0.2.0',
    author='Smarkets Limited',
    author_email='ops@smarkets.com',
    url='http://www.github.com/smarkets/sentry-hal',
    description='A Sentry extension which integrates with a JSON based XMPP chat bot',
    long_description=__doc__,
    license='BSD',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    entry_points={
       'sentry.plugins': [
            'sentry_hal = sentry_hal.plugin:HALMessage'
        ],
    },
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
