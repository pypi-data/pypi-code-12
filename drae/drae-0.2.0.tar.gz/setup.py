# coding: utf-8

"""Query the DRAE

"""
import setuptools


setuptools.setup(
    name='drae',
    version='0.2.0',
    install_requires=['lxml', 'BeautifulSoup4', 'requests', 'future'],
    packages=setuptools.find_packages(),
    description = 'Query the DRAE',
    author = 'José Sazo',
    author_email = 'jose.sazo@gmail.com',
    url = 'https://git.hso.rocks/hso/drae',
    download_url = 'https://git.hso.rocks/hso/drae/archive/0.2.0.tar.gz',
    keywords = ['text', 'dictionary', 'api', 'scraping'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ])
