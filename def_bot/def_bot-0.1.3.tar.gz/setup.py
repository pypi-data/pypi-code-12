# coding: utf-8
"""The original @def_bot implementation
"""
import setuptools


setuptools.setup(
    name='def_bot',
    version='0.1.3',
    install_requires=['bender>=0.0.2', 'blinker', 'flask', 'gunicorn', 'raven', 'drae', 'click'],
    packages=setuptools.find_packages(),
    description = 'The original @def_bot implementation',
    author = 'José Sazo',
    author_email = 'jose.sazo@gmail.com',
    url = 'https://git.hso.rocks/hso/def',
    download_url = 'https://git.hso.rocks/hso/def/archive/0.1.3.tar.gz',
    include_package_data=True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points = {
        'console_scripts': [
            'def=def_bot.commands:cli'
        ],
    }
)
