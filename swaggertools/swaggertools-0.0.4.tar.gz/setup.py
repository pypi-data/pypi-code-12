#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer

setup(
    name='swaggertools',
    version=versioneer.get_version(),
    description='Merge many files swagger specification into one file.',
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    license='MIT',
    url='http://swagger.errorist.io/tools',
    install_requires=[
        'dominate',
        'pyyaml'
    ],
    packages=find_packages(),
    keywords=[
        'api',
        'json',
        'yaml',
        'utilitaries',
        'validation',
        'swagger'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: OpenStack',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    entry_points={
        'console_scripts': [
            'swagger-tools = swaggertools.cli:main',
        ]
    },
    cmdclass=versioneer.get_cmdclass()
)
