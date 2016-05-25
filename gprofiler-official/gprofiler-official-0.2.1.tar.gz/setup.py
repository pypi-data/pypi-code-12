from distutils.core import setup

import os
import os.path
import subprocess
import sys

def get_version():
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	return subprocess.check_output(
		[sys.executable, "gprofiler.py", "--version"],
		stderr=subprocess.STDOUT
	).strip()

setup(
	name = 'gprofiler-official',
	py_modules = ['gprofiler.gprofiler', 'gprofiler.paramtransform'],
	scripts = ['gprofiler.py'],
	version = get_version(),
	description = 'Functional enrichment analysis and more via the g:Profiler toolkit',
	author = 'Tambet Arak',
	author_email = 'biit.support@lists.ut.ee',
	url = 'http://biit.cs.ut.ee/gprofiler',
	keywords = ['biology', 'bioinformatics', 'enrichment', 'gprofiler'],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: BSD License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Topic :: Scientific/Engineering :: Bio-Informatics'
	],
	long_description = """\

gprofiler-official
==================

The official Python interface to the g:Profiler `[1] <http://biit.cs.ut.ee/gprofiler>`_ toolkit for enrichment
analysis of functional (GO and other) terms, conversion between identifier
namespaces and mapping orhologous genes in related organisms. This library
provides both a command-line tool and a Python module. It is designed to be
lightweight and not require any 3rd party packages. 

Installation on Linux using pip
-------------------------------

The pip tool `[4] <https://pip.pypa.io/en/stable/>`_ is the recommended method of installing Python packages.

Optionally create a virtual environment `[2] <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_::

$ virtualenv2 myenv
$ source myenv/bin/activate

Install the software with pip, see `[3] <https://python-packaging-user-guide.readthedocs.org/en/latest/installing/>`_ for instructions::

$ pip install gprofiler-official

Make sure that the installed gprofiler.py script is on your $PATH. When using
a virtual environment as shown above, this should happen automatically.

Run an example query::

$ gprofiler.py -o scerevisiae "swi4 swi6"

For detailed usage instructions, see::

$ gprofiler.py --help

To use the module in your codebase::

	from gprofiler import GProfiler
	gp = GProfiler("MyToolName/0.1")
	result = gp.gprofile("sox2")

For details, see the API documentation `[6] <http://biit.cs.ut.ee/gprofiler_beta/doc/python/>`_.

Installation on Linux using the tarball
---------------------------------------

You may simply download the tarball from gprofiler-official PyPI page `[5] <https://pypi.python.org/pypi/gprofiler-official>`_,
extract it and use the gprofiler.py script without installation. For detailed
usage instructions, see::

$ gprofiler.py --help

Installation on other platforms
-------------------------------

Please see `[3] <https://python-packaging-user-guide.readthedocs.org/en/latest/installing/>`_ for package installation instructions on various platforms.

* [1] http://biit.cs.ut.ee/gprofiler
* [2] http://docs.python-guide.org/en/latest/dev/virtualenvs/
* [3] https://python-packaging-user-guide.readthedocs.org/en/latest/installing/
* [4] https://pip.pypa.io/en/stable/
* [5] https://pypi.python.org/pypi/gprofiler-official
* [6] http://biit.cs.ut.ee/gprofiler_beta/doc/python/

	"""
)
