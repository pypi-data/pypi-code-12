#! /usr/bin/env python
from setuptools import setup, find_packages
from io import open
import versioneer

setup(
    name='amqp_client_cli',
    packages=find_packages(),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='A command line interface for interacting with '
                'amqp exchanges',
    author='Dillon Dixon',
    author_email='dillondixon@gmail.com',
    url='https://github.com/ownaginatious/amqp-client-cli',
    license='MIT',
    keywords=['amqp', 'cli', 'client', 'rabbitmq', 'amq'],
    classifiers=['Environment :: Console'],
    install_requires=[line.strip()
                      for line in open("requirements.txt", "r",
                                       encoding="utf-8").readlines()],
    entry_points={
        "console_scripts": [
            "amqpcli = amqp_client_cli.main:main",
        ],
    },
)
