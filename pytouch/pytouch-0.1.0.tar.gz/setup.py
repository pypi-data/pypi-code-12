# coding: utf-8

from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='pytouch',
    version=version,

    description='easily make python file',
    keywords='pytouch,touch,createfile',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    author='hzcortex',
    author_email='iamwanghz@gmail.com.com',

    entry_points={
        'console_scripts': [
            'pytouch=pytouch.pytouch:main'
        ]
    },
)
