# coding=utf-8

import os
from setuptools import setup


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-fs-leonid',
    version='0.1.0',
    packages=['leonid'],
    include_package_data=True,
    install_requires=[],
    author='Yuri Lya',
    author_email='yuri.lya@fogstream.ru',
    url='https://bitbucket.org/fogstream/django-fs-leonid',
    license='The MIT License (MIT)',
    description='The Django-related reusable app provides the ability to create and store in a database files such as robots.txt, sitemap.xml and so on.',
    long_description=README,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
