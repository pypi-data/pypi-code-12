# N.B. to push a new version to PyPi, update the version number
# in rfhub/version.py and then run 'python setup.py sdist upload'
from setuptools import setup

execfile('PageObjectLibrary/version.py')

long_description = \
'''PageObjectLibrary is a lightweight library which supports using
the page object pattern with robot framework and Selenium2Library.
This library does not replace Selenium2Library. Rather, it
provides a framework around which to use Selenium2Library and the
lower-level bindings to selenium via robot framework keywords.
'''

setup(
    name             = 'robotframework-pageobjectlibrary',
    version          = "0.1.2",
#    version          = __version__,
    author           = 'Bryan Oakley',
    author_email     = 'bryan.oakley@gmail.com',
    url              = 'https://github.com/boakley/robotframework-pageobjectlibrary/',
    keywords         = 'robotframework',
    license          = 'Apache License 2.0',
    description      = 'Robotframework library that implements the Page Object pattern',
    long_description = long_description,
    zip_safe         = True,
    include_package_data = True,
    install_requires = ['robotframework', 'robotframework-selenium2library', 'selenium', 'six'],
    classifiers      = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Framework :: Robot Framework",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Intended Audience :: Developers",
        ],
    packages         =[
        'PageObjectLibrary',
    ],
    scripts          =[], 
)
