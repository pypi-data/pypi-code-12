import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "bookshops",
    version = "0.1",
    packages = find_packages(),
    scripts = ['*.py', 'settings.py', 'README.md'],

    install_requires = [
        "termcolor", # colored print
        "clize",     # build cli args from the method (kw)args
        "six",
        "future",
    ],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        # 'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "vindarel",
    author_email = "ehvince@mailz.org",
    description = "Get book information (isbn or search) from real bookstores.",
    long_description = read('README.md'),
    license = "GNU GPLv3",
    keywords = "bookshop bookstore library book isbn ean webscraping",
    url = "https://gitlab.com/vindarel/bookshops",

    entry_points = {
        "console_scripts": [
            "livres = frFR.librairiedeparis.librairiedeparisScraper:main",
            "libros = esES.casadellibro.casadellibroScraper:main",
        ],
    },

    tests_require = {

    },

    classifiers = [
        "Environment :: Console",
        "License :: Public Domain",
        "Topic :: Utilities",
    ],

)
