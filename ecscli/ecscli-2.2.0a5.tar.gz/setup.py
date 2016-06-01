from setuptools import find_packages
from distutils.core import setup
setup(
    name = 'ecscli',
    packages=find_packages(),
    version = '2.2.0.alpha5',
    description = 'a test install of the ECS ecscli',
    author = 'joe conery',
    author_email = 'joseph.conery@emc.com',
    classifiers = [],
    install_requires=[
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'ecscli = ecscli.ecscli:runCmd',
        ]
    }
)
