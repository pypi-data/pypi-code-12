from setuptools import setup

setup(
    name = 'uconfig',
    description = 'simple configuration file parser',
    version = '0.1.1',
    author = 'David Ewelt',
    author_email = 'uranoxyd@gmail.com',
    url = 'https://bitbucket.org/uranoxyd/uconfig',
    license = 'BSD',
    py_modules = ['uconfig'],
    zip_safe = False,

    classifiers = [
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    keywords = 'configuration parser'
)