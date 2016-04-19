"""
Flask-Sendwithus
================

About
-----

Forwards-compatible Flask extension to interact with the `sendwithus <https://www.sendwithus.com/>`_ API.

Installation
------------

    pip install Flask-Sendwithus

Documentation
-------------

Uses the standard extension pattern. Example::

    >>> from flask import Flask
    >>> from flask_sendwithus import Sendwithus

    >>> app = Flask(__name__)
    >>> app.config['SENDWITHUS_API_KEY'] = 'YOUR-API-KEY'
    >>> sendwithus = Sendwithus()
    >>> sendwithus.init_app(app)
    >>> r = sendwithus.send(
        email_id='YOUR-EMAIL-ID',
        recipient={'address': 'us@sendwithus.com'})
    >>> print(r.status_code)
    200
    )

See `the official python client's documentation <https://github.com/sendwithus/sendwithus_python)>`_ for further info on what methods are available. All methods found on the `sendwithus.api` instance is proxied on the Flask-Sendwithus's instance.

"""
from setuptools import setup

setup(
    name='Flask-Sendwithus',
    version='1.0.1',
    author="Jacob Magnusson",
    author_email="m@jacobian.se",
    url='https://github.com/jmagnusson/Flask-Sendwithus',
    platforms='any',
    license="BSD",
    description="Forwards-compatible Flask extension to interact with the sendwithus API",
    long_description=__doc__,
    packages=['flask_sendwithus'],
    install_requires=['flask>=0.8', 'sendwithus'],
    extras_require=dict(
        test=[
            'coverage',
            'flake8',
            'isort',
            'pytest',
        ],
    ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
