#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name = 'yaop',
      version = '0.1.1',
      description = 'Yet Another Option Parser (full fledged)',
	  long_description = '''A simple and light library that handle both command line parsing and config file reading.

The only thing you have to do, is to describe (throught a YAML resource /
config file) all options and parameters your main function expects.

This way, you only describe what to do, and not how to do it.

Every is done under the hood ; a simple call to the library handle :

  - application banner and help screen printing
  - command line parsing
  - building of dictionnary that hold configuration (flags, options and parameters values)
  - parsing optional config file that will override default values
  - etc.

Please read file README for getting started.

Other instructions are available in the documentation : both user and reference manuals.

Please be warned, that the library is in pre-alpha stage (for a short time),
until full documentation will be written : so package don't contains all source files yet.''',
      url = 'https://github.com/Aygos/yaop',
      author = 'Aygos (C.B.)',
      author_email='cyrilb02@sfr.fr',
      license = 'Creative Commons - BY-NC-ND',
	  keywords = 'yaop command line optparse config file YAML resource banner help script application console shell',
      classifiers=[
		'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 1 - Alpha',
		'Environment :: Console',
		'Framework :: Pytest',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Natural Language :: French',
		'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
		'Topic :: Software Development :: Interpreters',
		'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: Linguistic',
		'Topic :: System :: Shells',
		'Topic :: Text Processing',
      ],
      # packages = ['yaop'],
      # packages = find_packages('.'),
      packages = find_packages('.', exclude = ['yaop']),
      install_requires=[
          'pyyaml',
      ],
	  include_package_data = True,
      zip_safe = False,
	  setup_requires = ['pytest-runner'],
	  tests_require = ['pytest'],
	  )
