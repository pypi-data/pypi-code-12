#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__author__ = 'Fabrice Corraire'

main_namespace = {}
with open('cryptoshop/_settings.py') as version_file:
    exec(version_file.read(), main_namespace)
version = main_namespace['__version__']

setup(
    name='cryptoshop',
    version=version,
    keywords=['aes', 'encrypt', 'decrypt', 'encryption', 'decryption', 'serpent', 'argon', 'secure', 'crypto',
              'cryptography', 'twofish', 'gcm', 'argon2', 'botan'],
    packages=find_packages(),
    author="Fabrice Corraire",
    author_email="antidote1911@gmail.com",
    description="Encrypt and decrypt file or string in GCM mode with AES, Serpent or Twofish as secure as possible.",
    long_description=open('README.rst').read(),
    install_requires=['tqdm', 'argon2_cffi'],
    include_package_data=True,
    url='https://github.com/Antidote1911/cryptoshop',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development'
    ],

)
