from setuptools import setup

def readme():
	with open('README.md') as f:
		return f.read()

setup(name='Ingresse',
	version='0.1',
	description='Ingresse Python SDK for great usage',
	long_description=readme(),
	url='https://www.ingresse.com/',
	author='Ingresse',
	author_email='devel@ingresse.com',

	packages=['ingresse'],

	install_requires=[
		'requests >= 0.14.1',
	],

	classifiers=[
		"Programming Language :: Python",
		"Development Status :: 1 - Planning",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Topic :: Software Development :: Libraries :: Python Modules"
	],
)