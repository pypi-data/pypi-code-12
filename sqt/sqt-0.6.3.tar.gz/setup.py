from setuptools import setup, Extension
from distutils.version import LooseVersion
from glob import glob
import os
import sys

# set __version__
exec(next(open('sqt/__init__.py')))

MIN_CYTHON_VERSION = '0.17'

if sys.version_info < (3, 3):
	sys.stdout.write("At least Python 3.3 is required.\n")
	sys.exit(1)


def out_of_date(extensions):
	"""
	Check whether any pyx source is newer than the corresponding generated
	C(++) source or whether any C(++) source is missing.
	"""
	for extension in extensions:
		for pyx in extension.sources:
			path, ext = os.path.splitext(pyx)
			if ext not in ('.pyx', '.py'):
				continue
			csource = path + ('.cpp' if extension.language == 'c++' else '.c')
			if not os.path.exists(csource) or (
				os.path.getmtime(pyx) > os.path.getmtime(csource)):
				return True
	return False


def no_cythonize(extensions, **_ignore):
	"""
	Change file extensions from .pyx to .c or .cpp.

	Copied from Cython documentation
	"""
	for extension in extensions:
		sources = []
		for sfile in extension.sources:
			path, ext = os.path.splitext(sfile)
			if ext in ('.pyx', '.py'):
				if extension.language == 'c++':
					ext = '.cpp'
				else:
					ext = '.c'
				sfile = path + ext
			sources.append(sfile)
		extension.sources[:] = sources
	return extensions


def cythonize_if_necessary(extensions):
	if '--cython' in sys.argv:
		sys.argv.remove('--cython')
	elif out_of_date(extensions):
		sys.stdout.write('At least one C source file is missing or out of date.\n')
	else:
		return no_cythonize(extensions)

	try:
		from Cython import __version__ as cyversion
	except ImportError:
		sys.stdout.write(
			"ERROR: Cython is not installed. Install at least Cython version " +
			str(MIN_CYTHON_VERSION) + " to continue.\n")
		sys.exit(1)
	if LooseVersion(cyversion) < LooseVersion(MIN_CYTHON_VERSION):
		sys.stdout.write(
			"ERROR: Your Cython is at version '" + str(cyversion) +
			"', but at least version " + str(MIN_CYTHON_VERSION) + " is required.\n")
		sys.exit(1)

	from Cython.Build import cythonize
	return cythonize(extensions)


extensions = [
	Extension('sqt._helpers', sources=['sqt/_helpers.pyx']),
]
extensions = cythonize_if_necessary(extensions)


setup(
	name = 'sqt',
	version = __version__,
	author = 'Marcel Martin',
	author_email = 'marcel.martin@scilifelab.se',
	url = 'https://bitbucket.org/marcelm/sqt',
	description = 'Command-line tools for the analysis of high-throughput sequencing data',
	license = 'MIT',
	packages = [ 'sqt', 'sqt.io', 'sqt.commands' ],
	entry_points = {'console_scripts': [
		'sqt = sqt.__main__:main',
		#'sqt-addadapt = sqt.commands.addadapt:main',
		#'sqt-bam2fastq = sqt.commands.bam2fastq:main',
		#'sqt-bamstats = sqt.commands.bamstats:main',
		#'sqt-checkfastqpe = sqt.commands.checkfastqpe:main',
		#'sqt-checkvcfref = sqt.commands.checkvcfref:main',
		#'sqt-compare-sequences = sqt.commands.compare_sequences:main',
		#'sqt-coverage = sqt.commands.coverage:main',
		#'sqt-fastaextract = sqt.commands.fastaextract:main',
		#'sqt-fastamutate = sqt.commands.fastamutate:main',
		#'sqt-fastastats = sqt.commands.fastastats:main',
		#'sqt-fastxmod = sqt.commands.fastxmod:main',
		#'sqt-fixbam64 = sqt.commands.fixbam64:main',
		#'sqt-globalalign = sqt.commands.globalalign:main',
		#'sqt-histogram = sqt.commands.histogram:main',
		#'sqt-qualityguess = sqt.commands.qualityguess:main',
		#'sqt-readcov = sqt.commands.readcov:main',
		#'sqt-samfixn = sqt.commands.samfixn:main',
		#'sqt-simreads = sqt.commands.simreads:main',
		#'sqt-translate = sqt.commands.translate:main',
	]},
	install_requires = [
		'pysam!=0.9.0',
		'cutadapt',
		'matplotlib',
		'seaborn',
	],
	ext_modules = extensions,
	test_suite = 'nose.collector',
	classifiers = [
		"Development Status :: 3 - Alpha",
		#Development Status :: 4 - Beta
		#Development Status :: 5 - Production/Stable
		"Environment :: Console",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Programming Language :: Python :: 3",
		"Topic :: Scientific/Engineering :: Bio-Informatics"
	]
)
