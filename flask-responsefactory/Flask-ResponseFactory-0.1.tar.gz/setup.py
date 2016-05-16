"""
Flask-ResponseFactory
-------------

Create Flask response objects in a declarative way.
"""
from setuptools import setup


setup(
    name='Flask-ResponseFactory',
    version='0.1',
    url='https://github.com/joelcolucci/flask-responsefactory',
    license='MIT',
    author='Joel Colucci',
    author_email='joelcolucci@gmail.com',
    description='Create Flask response objects in a declarative way',
    long_description=__doc__,
    packages=['flask_responsefactory'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
