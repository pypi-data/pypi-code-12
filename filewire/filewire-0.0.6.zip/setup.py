#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='filewire',
    version='0.0.6',
    description='Easily send and receive files in LAN',
    author='zxey',
    author_email='zxey.bones@gmail.com',
    url='https://pypi.python.org/pypi/filewire',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Natural Language :: English',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Topic :: Communications',
        'Topic :: Internet'
    ],
    keywords='lan share send receive file',
    entry_points={
        'console_scripts': [
            'filewire=filewire.filewire:main',
        ]
    }
)
