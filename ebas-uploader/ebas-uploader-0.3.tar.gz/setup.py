import codecs

from os import path
from setuptools import setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    author="Maize Analytics",
    description="a command line utility to watch a folder and auto-upload files to an EBAS node",
    name="ebas-uploader",
    long_description=read("README.rst"),
    version="0.3",
    url="https://github.com/maizeanalyticsorg/ebas-uploader",
    license="MIT",
    py_modules=["ebas_uploader"],
    install_requires=[
        "click==5.1",
        "colorama==0.3.3",
        "opbeat==3.3.0",
        "requests==2.7.0",
        "watchdog==0.8.3"
    ],
    entry_points="""
        [console_scripts]
        ebas_uploader=ebas_uploader:main
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
