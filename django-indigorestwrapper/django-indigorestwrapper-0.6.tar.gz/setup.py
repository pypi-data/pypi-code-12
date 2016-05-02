import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-indigorestwrapper',
    version='0.6',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',  
    description='This is a (completely unauthorized) REST wrapper for the Indigo home automation application, using Django and Django-rest-framework.',
    long_description=README,
    url='https://github.com/EdwardMoyse/django-indigorestwrapper',
    author='Edward Moyse',
    author_email='edward.moyse@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',  
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
