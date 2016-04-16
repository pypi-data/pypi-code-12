from setuptools import setup

setup(
	name='getTweets',	# The name of the PyPI-package.
	version='0.1111',		# Update the version number for new releases
	description='Gathers all the tweets from a specific feed',
	author='Zachary Wimer',
	author_email='zwimer@gmail.com',
	scripts=['getTweets.py']	# The name of the script, and also the command to be used to call it
)

