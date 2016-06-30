import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    README = ''
    CHANGES = ''


setup(
    name='SiftPartner',
    description='Python bindings for Sift Science\'s Partnerships API',
    version='0.0.3', # Must be kept up to date with siftpartner/version.py VERSION
    url='https://siftscience.com',

    author='Sift Science',
    author_email='support@siftscience.com',
    long_description=README + '\n\n' + CHANGES,

    packages=['siftpartner'],
    install_requires=[
        "requests >= 0.14.1",
        "mock >= 1.0.1",
    ],

    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
