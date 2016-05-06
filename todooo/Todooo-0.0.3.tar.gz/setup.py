#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
	name='Todooo',
	version='0.0.3',
	author='Chenghao Qian',
	author_email='qch.jacob.jm@gmail.com',
	packages=['Todooo','Todooo.lib'],
	scripts=['Todooo/TODO'],
	package_data={'Todooo':['data/*.dat','data/usr/*/*.dat']},
	url='https://github.com/ChenghaoQ/Todo',
	license='COPYING.WTFPL',
	description='A simple todolist with cursor.'
)
