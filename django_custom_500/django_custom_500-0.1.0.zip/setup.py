# coding=utf-8

import io

from setuptools import setup

setup(
    name='django_custom_500',
    version='0.1.0',
    description='Create custom 500.html for Django with optional Sentry support.',
    long_description=io.open('README.rst').read(),
    url='https://github.com/illagrenan/django-custom-500',
    license='MIT',
    author='Vasek Dohnal',
    author_email='vaclav.dohnal@gmail.com',
    packages=['django_custom_500'],
    install_requires=['django'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=[]
)
