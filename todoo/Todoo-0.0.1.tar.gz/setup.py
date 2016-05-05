from distutils.core import setup

setup(
	name='Todoo',
	version='0.0.1',
	author='Chenghao Qian',
	author_email='qch.jacob.jm@gmail.com',
	packages=['todoo'],
	package_data={'todoo':['data/*.dat','data/usr/*/*.dat']},
	license='COPYING.WTFPL',
	description='A simple todolist.'
)
