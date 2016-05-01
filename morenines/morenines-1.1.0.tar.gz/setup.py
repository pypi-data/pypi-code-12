import os
from codecs import open
from setuptools import setup, find_packages

this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, 'DESCRIPTION.rst'), encoding='utf8') as f:
    long_desc = f.read()

setup(
    name='morenines',
    version='1.1.0',
    url='https://github.com/mcgid/morenines',
    license='MIT',

    description='A simple content change detector',
    long_description=long_desc,

    keywords=[
        'backup',
        'hashing',
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: System",
        "Topic :: System :: Archiving",
        "Topic :: System :: Archiving :: Mirroring",
        "Topic :: Utilities",
    ],

    install_requires=[
        'click',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mn = morenines.application:main'
        ]
    },
)
