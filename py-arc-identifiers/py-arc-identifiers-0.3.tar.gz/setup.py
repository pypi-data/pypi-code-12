from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='py-arc-identifiers',
    version='0.3',
    description='generate Arc UUIDs in python',
    url='https://github.com/WPMedia/py-arc-identifiers',
    download_url='https://github.com/WPMedia/py-arc-identifiers/tarball/0.3',
    author='patharer',
    author_email='rohan.pathare@washpost.com',
    license='MIT',
    packages=['ArcUUID', 'test'],
)
