#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages  
version = '0.6.5'

setup(  
        name='asc2wp',
        version=version,
        description="File base post to Wordpress with Asciidoc format",
        classifiers=[
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 2 :: Only",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
            "Topic :: Internet :: WWW/HTTP :: Site Management",
            "Topic :: Text Processing :: Markup",
            "License :: OSI Approved :: MIT License",
            ],
        keywords='wordpress, asciidoc, asciidoctor, markup, api',
        author='Shuichi Minamie',
        author_email='s.minamie@gmail.com',
        url='',
        license='MIT',
        packages=find_packages(),
        zip_safe=True,
        install_requires=["python-wordpress-xmlrpc", "pyyaml"],
        entry_points="""  
            [console_scripts]
            asc2wp = asc2wp:main
        """,
    )