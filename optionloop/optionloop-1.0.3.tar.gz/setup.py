from setuptools import setup
#md to rst conversion
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(name='optionloop',
		version='1.0.3',
		description='Allows collapsing of nested for loops via '
		'dictionary iteration',
		url='https://github.com/arghdos/optionLoop',
		author='arghdos',
		author_email='arghdos@gmail.com',
		license='GPL',
		packages=['optionloop'],
		zip_safe=True,
		test_suite='nose.collector',
		long_description=read_md('README.md'),
		tests_require=['nose'])
