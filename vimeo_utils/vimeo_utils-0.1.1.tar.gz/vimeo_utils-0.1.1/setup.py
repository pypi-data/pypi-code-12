import os
from setuptools import setup

setup(
    name='vimeo_utils',
    version='0.1.1',
    packages=['vimeo_utils'],
    include_package_data=True,
    license='MIT License',
    description='Vimeo-related shortcuts for Django',
    url='https://github.com/life-in-messiah/django-vimeo-utils',
    download_url = 'https://github.com/life-in-messiah/django-vimeo-utils/tarball/0.1.1',
    author='Joshua Austin',
    author_email='joshthetechie@outlook.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
