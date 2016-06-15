from setuptools import setup, find_packages

name='remisc'
with open('README.rst', 'r') as f:
    ld = f.read()
    
setup(
	name=name,
	version='0.0.2',
	packages=find_packages(),
	install_requires=[],
	package_data={
		'': ['*.html','*.rst']
	},
	author='Brian Kirkpatrick',
	author_email='code@tythos.net',
	description='REST-ful microservice framework for scientific computing',
	long_description=ld,
	license='MIT',
	keywords='rest server scientific computing microservice',
	url='https://github.com/Tythos/' + name,
	test_suite=name+'.test.suite',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Scientific/Engineering :: Information Analysis',
		'Programming Language :: Python :: 2',
	],
)
