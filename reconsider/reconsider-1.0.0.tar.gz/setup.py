from setuptools import setup

setup(
	name='reconsider',
	version='1.0.0',
	url='https://github.com/ouroboroscoding/reconsider',
	description='Reconsider is a module used to move DBs/Tables from one RethinkDB instance to another.',
	keywords=['rethinkdb','data','database','db','nosql'],
	author='Chris Nasr - OuroborosCoding',
	author_email='ouroboroscode@gmail.com',
	license='Apache-2.0',
	packages=['Reconsider'],
	install_requires=['rethinkdb'],
	zip_safe=True
)
