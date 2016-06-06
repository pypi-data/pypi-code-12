#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Flask-Triangle
==============

**With great UX comes great security needs.** *Uncle Ben*

Flask-Triangle is utterly influenced by Flask-WTF_. It aims to provide you with
similar features : form input handling and validation. The main difference is
that Flask-Triangle is designed with AngularJS_ and XHR in mind.

Flask-Triangle comes preloaded with various features :

    * End-to-end data validation based on JSONschema_.
    * A collection of ready to use *Widgets* for both standard HTML inputs and
      toolkits (i.e. UI-Bootstrap_).
    * A set of *Modifiers* to adapt the default behaviour to your needs.
    * Various tools to integrate AngularJS in your Flask_ application.

For detailed informations, have a look at the documentation_.

.. _Flask: http://flask.pocoo.org/
.. _Flask-WTF: https://flask-wtf.readthedocs.org/en/latest/
.. _AngularJS: http://angularjs.org/
.. _UI-Bootstrap: http://angular-ui.github.io/bootstrap/
.. _JSONschema: http://json-schema.org/
.. _documentation: http://flask-triangle.readthedocs.org/
'''

from setuptools import setup, find_packages

setup(

    name='Flask-Triangle-joeflack4',
    version='0.5.6',
    author='Joe Flack',
    author_email='joeflack4@gmail.com',
    description=('Integration of AngularJS and Flask, originally created by Morgan Delahaye-Prat (mdp@m-del.fr).'),
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=['six', 'flask', 'jsonschema'],
    tests_require=['beautifulsoup4'],
    url='http://flask-triangle.readthedocs.org/',
	download_url = 'https://github.com/joeflack4/flask-triangle/tarball/v0.5.6',
	keywords = ['flask', 'angular', 'jinja2', 'angular js', 'flask triangle'],
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Web Environment',
        'Framework :: Flask'
    ]
)
