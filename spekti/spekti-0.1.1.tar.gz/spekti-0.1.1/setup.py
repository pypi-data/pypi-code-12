from setuptools import setup
 # -*- coding: utf-8 -*-

setup(
    name = 'spekti',
    version = '0.1.1',
    description = 'Execute command on file or folder change',
    author = 'Gérald Lelong',
    author_email = 'lelong.gerald@gmail.com',
    url = 'https://github.com/lelongg/watcher',
    scripts = [
        'spekti',
    ],
    install_requires = [
        'watchdog',
        'argparse',
    ],
)
