from setuptools import setup, find_packages

requires=['rauth', 'six']

setup(name='contextio',
    version='v1.11.1',
    description='Library for accessing the Context.IO API (v2.0 and Lite) in Python',
    author='Tony Blank, Jesse Dhillon, Alex Tanton',
    author_email='tony@context.io, jesse@deva0.net',
    url='http://context.io',
    keywords=['contextIO', 'imap', 'oauth'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    download_url='https://github.com/contextio/Python-ContextIO/archive/v1.11.0.tar.gz',
)
