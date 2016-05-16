#!/usr/bin/env python3
import os
from setuptools import setup, find_packages


def get_readme():
    return open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    author="Julio Gonzalez Altamirano",
    author_email='devjga@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
    ],
    description="Easily post tweets from an image library.",
    entry_points={
        'console_scripts': [
            'goldfinchsong=goldfinchsong.cli:run',
        ],
    },
    install_requires=['click',  'tinydb', 'tweepy'],
    keywords="twitter api images",
    license="MIT",
    long_description=get_readme(),
    name='goldfinchsong',
    packages=find_packages(include=['goldfinchsong', 'goldfinchsong.*'],
                           exclude=['tests', 'tests.*']),
    platforms=['Any'],
    url='https://github.com/jga/goldfinchsong',
    version='0.1.4',
)
