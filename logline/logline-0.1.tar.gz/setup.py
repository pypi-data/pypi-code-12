from distutils.core import setup
setup(
	name = 'logline',
	packages = ['logline'], # this must be the same as the name above
	version = '0.1',
	description = 'A Python abstraction library for the LogLine API',
	long_description = "See README.md for the full description of LogLine",
	author = 'Finnian Anderson',
	author_email = 'finnian.anderson@gmail.com',
	url = 'https://github.com/developius/logline-python', # use the URL to the github repo
	download_url = 'https://github.com/developius/logline-python/tarball/0.1', # I'll explain this in a second
	keywords = ['logging', 'api','LogLine'], # arbitrary keywords
	classifiers = [],
	license = 'MIT',
	requires = [
		'json',
		'urllib',
		'urllib2'
	]
)