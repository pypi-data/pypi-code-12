from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as readMeFile:
    long_description = readMeFile.read()

setup(
    name='communitysift',
    version='0.0.0',
    description='Community Sift is a SaaS based, dynamic and real time Chat Filtering Tool',
    long_description=long_description,
    author='CommunitySift',
    author_email=' demo@communitysift.com',
    url='https://communitysift.com/',
  #  license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
     #   'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    packages=find_packages(),
    install_requires=[
        'requests',
        'ConfigParser'
    ],
    zip_safe=False,
)