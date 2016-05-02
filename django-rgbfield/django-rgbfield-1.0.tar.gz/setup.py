#!/usr/bin/env python
from setuptools import find_packages, setup

import rgbfield

setup(
    name='django-rgbfield',
    version=rgbfield.__version__,
    description='An extension to the Django web framework that provides database and form color fields to accept RGB '
                'encoded color in HEX and store it as 4 bytes int',
    long_description=open('README.md').read(),
    url='https://github.com/MisterFix/django-rgbfield',
    author='Alexander Likhachev',
    author_email='likhachev96@gmail.com',
    install_requires=[
        'Django>=1.8',
        'six',
    ],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    license='MIT License',
    keywords=['django rgb color field'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)