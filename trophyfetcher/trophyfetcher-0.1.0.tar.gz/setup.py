# coding: utf-8

from setuptools import setup, find_packages

setup(
    name='trophyfetcher',
    version='0.1.0',
    url='https://github.com/robertomlsoares/trophyfetcher',

    author='Roberto Soares',
    author_email='robertomlsoares@gmail.com',

    description='A package used to fetch public information about trophies from PSN.',
    long_description=open('README.rst').read(),
    license='MIT',

    platforms=['Platform Independent'],
    install_requires=['selenium >= 2.53.2'],
    packages=find_packages(),
    package_data={
        '': ['*.txt', '*.rst']
    },

    keywords=['selenium', 'psn', 'trophy', 'fetcher', 'crawler'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
