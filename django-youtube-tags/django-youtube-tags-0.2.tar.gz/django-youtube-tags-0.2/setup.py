import os
from setuptools import setup

setup(
    name='django-youtube-tags',
    version='0.2',
    packages=['django-youtube-tags'],
    include_package_data=True,
    license='MIT License',
    description='Custom Django template tags to simplify embedding Youtube videos and thumbnails',
    url='https://github.com/life-in-messiah/django-youtube-tags',
    download_url = 'https://github.com/life-in-messiah/django-youtube-tags/tarball/0.2',
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
