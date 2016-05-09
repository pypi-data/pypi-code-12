import os
from setuptools import setup, find_packages

version = '0.3.0'

setup(
    name='pyactiverecord',
    version=version,
    description="pyactiverecord is python active record like mysql wrapper.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='db, mysql, active record, ORM',
    author="Hiroyuki Nikaido",
    author_email="hiroyuki.nikaido@gmail.com",
    url='https://github.com/nkdn/pyactiverecord',
    license='MIT',
    packages=find_packages(exclude=['examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    long_description=open("README.txt", "r").read(),
    install_requires=['mysql-connector-python']
)
