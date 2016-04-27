from setuptools import find_packages, setup

__version__ = '1.0.0'

setup(
    name='findawspeers',
    version=__version__,
    packages=find_packages(),
    install_requires=['typing', 'aws-auth-helper', 'boto'],
    url='https://github.com/drewsonne/findawspeers',
    license='GPLv2',
    author='Drew J. Sonne',
    author_email='drew.sonne@gmail.com',
    description='Small utility to returns a list of this instances EC2 peers in an Auto scaling group',
    entry_points={
        'console_scripts': [
            'find-aws-peers=findawspeers.__main__:main'
        ]
    },
)
