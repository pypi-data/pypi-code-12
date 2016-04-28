#!/usr/bin/env python
from setuptools import find_packages, setup

import versioneer


setup(
    name='JMS-Utils',
    version=versioneer.get_version(),
    description='Various utility functions',
    author='Johny Mo Swag',
    author_email='johnymoswag@gmail.com',
    url='https://github.com/JohnyMoSwag/jms-utils',
    download_url=('https://github.com/JohnyMoSwag/jms'
                  '-utils/archive/master.zip'),
    license='MIT',
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        'chardet',
        'six',
        ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'],
    )