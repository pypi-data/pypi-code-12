from setuptools import setup, find_packages

setup(
	name= 'thrift3babeltrace',
	packages = find_packages(),
	include_package_data=True,
	version = '0.2.2',
	description = 'Apache Thrift with modifications for compatibility for Python 3',
	author = 'Victor Araujo',
	author_email = 've.ar91@gmail.com',
	url = 'https://github.com/vears91/thrift3-binary-protocol',
	download_url = 'https://github.com/vears91/thrift3-binary-protocol/tarball/0.2.1',
	keywords = ['thrift', 'python3', 'binary protocol', 'thrift3', 'babeltrace'],
	classifiers = []
)
