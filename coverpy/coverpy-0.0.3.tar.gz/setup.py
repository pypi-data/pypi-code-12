from setuptools import setup, find_packages

try:
    from pypandoc import convert
    markdown = lambda file: convert(file, 'rst', 'md')
except ImportError:
    print("Can't find pypandoc. This is fine; but try to install it to have nicely formatted docs in PyPI.")
    markdown = lambda file: open(file, 'r').read()

setup(
	# PyPI specific meta
	name='coverpy',
	version='0.0.3',
	license='MIT License',
	author="fallenshell",
	author_email='dev@mxio.us',
	description="A wrapper for iTunes Search API",
	long_description=markdown('README.md'),
	keywords='itunes search api wrapper simple clear cover album art music',
	# Package routines
	packages=find_packages(exclude=['scripts', 'tests']),
	install_requires=['requests'],
)
