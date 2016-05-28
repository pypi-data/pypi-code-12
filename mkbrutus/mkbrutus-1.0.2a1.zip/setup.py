# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='mkbrutus',
    version='1.0.2a1',
    scripts=['mkbrutus.py'],
    description='Password bruteforcer for MikroTik devices',
    url='https://github.com/mkbrutusproject/mkbrutus',
    author='Ramiro Caire',
    author_email='ramiro.caire@gmail.com',
    license='AGPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='mkbrutus Mikrotik RouterOS',
    install_requires=[
        'docopt==0.6.2',
        'PyPrind==2.9.3',
        'RouterOS-api==0.13'
    ]
)
