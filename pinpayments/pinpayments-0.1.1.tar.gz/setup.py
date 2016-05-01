"""A Python interface to the PinPayments API.

See:
https://pin.net.au/docs/api
https://github.com/MattHealy/pinpayments-python
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pinpayments',
    version='0.1.1',
    description='A Python interface to the Pin Payments API.',
    long_description=long_description,
    url='https://github.com/MattHealy/pinpayments-python',
    author='Matt Healy',
    author_email='healmatt@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='pinpayments pin payments',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests>=2.9.1'],
)
