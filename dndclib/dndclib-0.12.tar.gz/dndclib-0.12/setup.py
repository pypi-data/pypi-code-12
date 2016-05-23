#from distutils.core import setup, Extension
from setuptools import setup, Extension, Command

long_description = 'DNDC Core Functions Libarary'

extension_mod = Extension('dndclib', sources = ['./DNDC_MODULE/DNDC_MODULE.cpp'])

classifiers = [
   "Development Status :: 1 - Planning",
   "Programming Language :: C++",
   "Topic :: Software Development",
]

setup (name = 'dndclib',
       version = '0.12',
       description = 'C++ Library of DNDC package',
	    # metadata for upload to PyPI
		author = "Feng",
		author_email = "dewscloud@gmail.com",
		license = "GPL",
		keywords = "DNDC Core Libarary",
        long_description=long_description,
        classifiers=classifiers,
		url = "http://www.dewscloud.com",   # project home page, if any
		# could also include long_description, download_url, classifiers, etc.

       ext_modules = [extension_mod])
