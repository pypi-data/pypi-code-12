import ast
import setuptools

with open('flask_frink/__init__.py') as f:
    for line in f:
        if line.startswith('__version__'):
            version = ast.parse(line).body[0].value.s
            break

assert version is not None

setuptools.setup(
    name="flask_frink",
    version=version,

    url="https://github.com/hactar-is/flask-frink",

    author="Hactar",
    author_email="systems@hactar.is",

    description="Add Flask-Security datastore functionality to Frink.",
    long_description="""Frink provides basic ORM-like functionality for RethinkDB on top of
    Schematics. This adds functionality for using Frink with Flask and Flask Security.""",

    packages=setuptools.find_packages(),

    install_requires=[
        'Flask',
        'schematics',
        'rethinkdb==2.3.0',
        'flask-security',
        'inflection',
        'frink>=0.0.7',
        'future'
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4'
    ],
)
