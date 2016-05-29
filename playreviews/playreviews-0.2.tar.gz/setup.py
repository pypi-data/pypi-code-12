from setuptools import setup
import os

if os.environ.get('USER','') == 'vagrant':
    del os.link

setup(
    name = 'playreviews',
    packages = ['playreviews'],
    version = '0.2',
    description = 'Package to scrape google play store reviews',
    author = 'Sharat Chandra',
    author_email = 'sharat9211@gmail.com',
    url = 'https://github.com/sharat9211/playreviews',
    keywords = ['google play store reviews', 'reviews', 'play store'],
    classifiers = [],
    install_requires = [
        'requests',
        'beautifulsoup4',
    ]

)