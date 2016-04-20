from setuptools import setup
setup(name='optionloop',
		version='1.0',
		description='Allows collapsing of nested for loops via '
		'dictionary iteration',
		url='https://github.com/arghdos/optionLoop',
		author='arghdos',
		author_email='arghdos@gmail.com',
		license='GPL',
		packages=['optionloop'],
		zip_safe=True,
		test_suite='nose.collector',
		tests_require=['nose'])