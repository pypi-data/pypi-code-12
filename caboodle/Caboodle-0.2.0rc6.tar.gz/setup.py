from setuptools import setup

def format(input, start = 0):
	result = ''
	indent = False
	count = 0

	with open(input, 'r') as file:
		for line in file:
			if count > start:
				if line[:1] == '\t' and not indent:
					indent = True
					result += '::\n\n'

				if line[:1].isalnum() and indent:
					indent = False

				result += line.replace('> ', '\t')
			count += 1

	return result

blurb = ('Caboodle is a Python module for web browsing or web scraping developed to '
	'provide an all-in-one (kit and caboodle) utility for anything the web has '
	'to offer.\n')
ld = blurb + format('README.md', 3)
print(ld, end='\n\n')

setup(
	name = 'Caboodle',
	version = '0.2.0-RC6',
	author = 'Justin Willis',
	author_email = 'sirJustin.Willis@gmail.com',
	packages = ['caboodle',],
	url = 'https://bitbucket.org/bkvaluemeal/caboodle',
	license = 'ISC License',
	description = 'A Python module for web browsing or web scraping',
	long_description = ld,
	install_requires = [
		'Selenium >= 2.46.0',
		'Pillow >= 3.0.0',
		'scikit-image >= 0.11.3',
		'scipy >= 0.16.1'
	],
)
