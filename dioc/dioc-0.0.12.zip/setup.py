from setuptools import setup, find_packages

version = '0.0.12'
name = 'dioc'
short_description = '`dioc` is a package for DigitalOcean.'
long_description = """\
`dioc` is a package for DigitalOcean.
::
   $ cat << eof >> .bashrc
export DIOC_TOKEN=...
export DIOC_DEFAULT_SSHKEY=sshk
export DIOC_DEFAULT_SIZE=512mb
export DIOC_DEFAULT_REGION=sgp1
eval "$(_DIO_COMPLETE=source dio)"
eof

   $ dio create test '' user_data='"#!/bin/bash\\ndocker run -p 80:8080 tsutomu7/gotour"'
   $ dio scp sample test:/tmp
   $ dio ssh test 'ls -l /tmp'
   $ dio destroy test

   $ python3
   import dioc
   d = dioc.Droplet('test')
   c = dioc.ssh_client()
   c.exec_command('ls')
   d.destroy()

Requirements
------------
* Python 3
* paramiko
* python-digitalocean
* Click

Features
--------
* nothing

Setup
-----
::

   $ pip install dioc
   or
   $ easy_install dioc

History
-------
0.0.1 (2015-12-27)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Software Development",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    py_modules=['dioc'],
    keywords=['dioc',],
    packages=find_packages(),
    include_package_data=True,
    author='Saito Tsutomu',
    author_email='tsutomu@kke.co.jp',
    url='https://pypi.python.org/pypi/dioc',
    license='PSFL',
    install_requires=['paramiko', 'python-digitalocean', 'Click'],
    entry_points='''
        [console_scripts]
        dio=dioc:action
    ''',
)
