from setuptools import setup, find_packages

PACKAGE = "flask_zeus"
NAME = "flask-zeus"
DESCRIPTION = ""
AUTHOR = "nanlong"
AUTHOR_EMAIL = "fei.code@gmail.com"
URL = "https://github.com/nanlong/flask_zeus"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=find_packages(),
    platforms='python 3.5',
    install_requires=[
        'flask',
        'flask-login',
        'flask-wtf',
        'flask-sqlalchemy',
        'flask-restful',
        'wtforms-json',
    ]
)