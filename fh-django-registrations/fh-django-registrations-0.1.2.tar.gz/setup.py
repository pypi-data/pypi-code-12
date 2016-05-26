import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='fh-django-registrations',
    version='0.1.2',
    packages=['registrations'],
    include_package_data=True,
    description='A Django app to provide account verification to activate and allow registering via email or SMS.',
    long_description=README,
    url='http://www.futurehaus.com/',
    install_requires=['base32-crockford', 'twilio']
)
