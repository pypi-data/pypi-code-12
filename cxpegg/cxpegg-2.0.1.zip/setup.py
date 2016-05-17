try:
    from setuptools import setup
except:
    from distutils.core import setup


NAME = "cxpegg" 
PACKAGES = ["cxpegg",]
DESCRIPTION = "this is a test package for packing python liberaries tutorial."
LONG_DESCRIPTION =  'asdfasdf'  #read("README.rst")
KEYWORDS = "test python package"
AUTHOR = "MitchellChu"
AUTHOR_EMAIL = "youremail@email.com"
URL = "http://blog.useasp.net/"
VERSION = "2.0.1"
LICENSE = "MIT"

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    include_package_data=True,
    zip_safe=True,
)