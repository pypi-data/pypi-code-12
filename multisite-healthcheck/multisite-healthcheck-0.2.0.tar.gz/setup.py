import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='multisite-healthcheck',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='Django app to check the status of sites in a multi-website django environment.',
    long_description=README,
    url='https://github.com/DanielKirov/multisite-healthcheck',
    author='Daniel Kirov',
    author_email='daniel.kirov@pancentric.com',
    install_requires=[
        'django>=1.4.0',
        'requests>=2.3.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
