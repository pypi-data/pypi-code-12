from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='rin-driver-vmware',

    version='0.1.4',

    description='A command line utilities to operate vCenter',
    long_description=long_description,

    url='',

    author='Hiroyasu OHYAMA',
    author_email='oyama-hiroyasu@dmm.com',

    license='MIT',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['rin-common'],

    data_files=[('etc', ['data/rin-vmware.yml.example'])],

    entry_points={
        'console_scripts': [
            'vmware_list_servers=rin_vmware.list_servers:main',
            'vmware_get_server=rin_vmware.get_server:main',
            'vmware_create_server=rin_vmware.create_instance:main',
        ],
    },
)
