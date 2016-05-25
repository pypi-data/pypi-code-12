# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
import codecs

version = '0.1.1'

setup(
    name='py3o.types',
    version=version,
    description="Data type helpers for Py3o",
    long_description=codecs.open(
        "README.rst", mode='r', encoding="utf-8"
    ).read(),
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='LibreOffice OpenOffice templating PDF',
    author='Jérémie Gavrel',
    author_email='jeremie.gavrel@xcg-consulting.fr',
    url='http://bitbucket.org/faide/py3o.types',
    license='MIT License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['py3o'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'six >= 1.4',
        'lxml',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
