#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# Use blanc_pages.VERSION for version numbers
version_tuple = __import__('blancseo').VERSION
version = '.'.join([str(v) for v in version_tuple])

setup(
    name='blanc-seo',
    version=version,
    description='Blanc SEO for Django',
    long_description=open('README.rst').read(),
    url='http://www.blanctools.com/',
    maintainer='Alex Tomkins',
    maintainer_email='alex@blanc.ltd.uk',
    platforms=['any'],
    packages=[
        'blancseo',
        'blancseo.seo',
        'blancseo.seo.templatetags',
    ],
    package_data={'blancseo': [
        'seo/templates/seo/*.html',
    ]},
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    license='BSD-2',
)
