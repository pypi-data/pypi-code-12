#!/usr/bin/env python
try:
    import os
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
    name='maillift-python',
    version='1.0.1',
    author='Marcus Saad',
    author_email='mv.nsaad@gmail.com',
    description="Wrapper around MailLift API",
    url='https://github.com/marcussaad/mailift-python',
    license='GPL V3',
    install_requires=[
        "requests==2.8.1"
    ],
    packages=['maillift'],
    download_url='https://github.com/marcussaad/mailift-python/tarball/1.0.1',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords=['api', 'maillift', 'letters', 'devtools', 'Development'],
)
