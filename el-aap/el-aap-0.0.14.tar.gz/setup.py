from setuptools import setup, find_packages

setup(
    name='el-aap',
    version='0.0.14',
    description='Elasticsearch Authentication and Authorization Proxy',
    long_description="""
Elasticsearch Authentication and Authorization reverse proxy
implementation in Python 3.

Copyright (c) 2016, Stephan Schultchen.

License: MIT (see LICENSE for details)
    """,
    packages=find_packages(),
    scripts=[
        'contrib/el_aap',
        'contrib/el_aap_api',
        'contrib/el_aap_cli'
    ],
    url='https://github.com/schlitzered/pyredis',
    license='MIT',
    author='schlitzer',
    author_email='stephan.schultchen@gmail.com',
    test_suite='test',
    platforms='posix',
    classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3'
    ],
    install_requires=[
        'bottle',
        'cachetools',
        'jinja2',
        'jsonschema',
        'passlib',
        'pep3143daemon',
        'pymongo',
        'requests',
        'waitress',
        'wsgi-request-logger',
        'wsgi-request-id',
    ],
    keywords=[
        'elasticsearch'
    ]
)
