import codecs
from os import path
from setuptools import setup, find_packages


def read(filepath):
    filepath = path.join(path.dirname(__file__), filepath)
    return codecs.open(filepath, 'r', 'utf-8').read()

description = read('README.rst') + read('AUTHORS.rst') + read('CHANGELOG.rst')

setup(
    name='django-setuptest-jenkins',
    version='0.0.3',
    description='Simple test suite enabling Django app testing with jenkins reports via $ python setup.py test',
    long_description=description,
    author='Dariusz Rzepka',
    author_email='rzepkadarek@gmail.com',
    license='BSD',
    url='https://github.com/darkowic/django-setuptest-jenkins',
    keywords=['django', 'test', 'jenkins', 'app'],
    packages=find_packages(),
    install_requires=[
        'django-jenkins>=0.18.0',
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)