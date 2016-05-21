import os
import re
from setuptools import setup, find_packages


def readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
        return readme.read()


def version():
    pattern = re.compile(r'__version__ = \'([\d\.]+)\'')
    with open(os.path.join('django_autoshard', '__init__.py')) as f:
        data = f.read()
        return re.search(pattern, data).group(1)


setup(
    name='django-autoshard',
    version=version(),
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    description='A Django library that makes sharding easy.',
    long_description=readme(),
    url='https://github.com/cipriantarta/django-autoshard',
    author='Ciprian Tarta',
    author_email='me@cipriantarta.ro',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Framework :: Django",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
    ],
    keywords='django shard sharding',
    install_requires=[
        'django>=1.8',
        'six',
    ],
    test_suite='django_autoshard.tests',
)
