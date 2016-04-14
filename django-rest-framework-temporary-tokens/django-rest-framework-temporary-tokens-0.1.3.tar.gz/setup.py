import os
import sys

from distutils.core import setup

import rest_framework_temporary_tokens

version = rest_framework_temporary_tokens.__version__

setup(
    name='django-rest-framework-temporary-tokens',
    version=version,
    description="""
Works with Django REST Framework and allows you to create authentication
tokens that expire within a given number of minutes and optionally
refresh the time to expiration on each successful authentication.
""",
    url='https://bitbucket.org/kbktech/django-rest-framework-temporary-tokens',
    download_url='https://bitbucket.org/kbktech/django-rest-framework-temporary-tokens/get/0.1.3.tar.bz2',
    author='Matthew Sewell',
    author_email='msewell@kbktech.com',
    license='MIT',
    packages=['rest_framework_temporary_tokens', 'rest_framework_temporary_tokens.migrations'],
    install_requires=[
        'djangorestframework>=3.2.3'
    ],
    keywords=[  'django', 'rest', 'framework', 'restframework', 'token',
                'expire', 'expiration', 'temporary', 'authtoken' ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
