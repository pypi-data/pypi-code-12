from setuptools import setup

setup(
    name             = 'dml',
    version          = '0.0.10.0',
    packages         = ['dml',],
    install_requires = ['json','pymongo',],
    license          = 'MIT License',
	url              = 'http://datamechanics.org',
	author           = 'A. Lapets',
	author_email     = 'a@lapets.io',
    description      = 'Common functionalities for building Data Mechanics platform components.',
    long_description = open('README').read(),
)
