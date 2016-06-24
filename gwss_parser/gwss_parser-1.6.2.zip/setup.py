from setuptools import setup

setup(
	name='gwss_parser',
	version='1.6.2',
	description='Garena web stats system collector',
	url='http://github.com/storborg/funniest',
	author='Garena Online Ltd',
	author_email='tranmt@garena.com',
	license='MIT',
	packages=['gwss_parser'],
	package_data={'gwss_parser': ['common/*']},
	install_requires=[
		'redis', 'pyparsing', 'psutil'
	],
	scripts=['bin/gwss-parser.py'],
	zip_safe=False)
