# coding: utf-8

"""Telegram bot framework

"""
import setuptools


setuptools.setup(
    name='bender',
    version='0.0.3',
    install_requires=['requests', 'redis', 'future'],
    packages=setuptools.find_packages(),
    description = 'Telegram bot framework',
    author = 'José Sazo',
    author_email = 'jose.sazo@gmail.com',
    url = 'https://git.hso.rocks/hso/bender',
    download_url = 'https://git.hso.rocks/hso/bender/archive/0.0.3.tar.gz',
    keywords = ['text', 'api', 'bot'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ])
