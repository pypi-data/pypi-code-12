from setuptools import setup, find_packages
from codecs import open
from os import path
import messaging_client.metadata as metadata

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
long_description = ""

try:
    from pypandoc import convert
    if path.exists(path.join(here, 'README.md')):
        long_description = convert('README.md', 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")

setup(
    name=metadata.NAME,
    version=metadata.VERSION,
    description=metadata.DESCRIPTION,
    long_description=long_description,
    url=metadata.URL,
    author=metadata.AUTHOR,
    author_email=metadata.AUTHOR_EMAIL,
    license=metadata.LICENSE,
    keywords=metadata.KEYWORDS,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    setup_requires=['nose>=1.0', 'coverage>=4.0.3', 'pypandoc>=1.1.3'],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        'console_scripts': [
            'messaging-client=messaging_client.__main__:main',
        ],
    },
)
