from setuptools import setup, find_packages
from version import VERSION
setup(
    name = 'OlymLibrary',
    version = VERSION,
    keywords = ('OlymLibrary', 'robot'),
    description = 'olymtech test',
    license = 'MIT License',

    author = 'zy',
    author_email = '84497503@qq.com',

    packages = find_packages(),
    platforms = 'any',
)