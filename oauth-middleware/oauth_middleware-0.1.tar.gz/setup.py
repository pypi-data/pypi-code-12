from __future__ import division, unicode_literals, print_function, absolute_import

import textwrap

from setuptools import setup, find_packages

setup(
    name='oauth_middleware',
    version=0.1,  # TODO: Do not forget to update in __init__
    description="Simple flask_oauthlib based middleware for WSGI app to preform oauth",
    author="Last G",
    author_email='sergei.azovskov@zalando.de',
    url='https://github.com/last-g/oauth_middleware',
    packages=find_packages(),
    requires=[
        'flask',
        'flask_oauthlib',
        'werkzeug',
        'six'
    ],
    classifiers=textwrap.dedent("""
        Development Status :: 3 - Alpha
        Intended Audience :: Developers
        License :: OSI Approved :: MIT License
        Operating System :: OS Independent
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: 3.4
        Programming Language :: Python :: 3.5
        Topic :: Software Development :: Libraries :: Python Modules
        Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware
    """).strip().splitlines(),

)