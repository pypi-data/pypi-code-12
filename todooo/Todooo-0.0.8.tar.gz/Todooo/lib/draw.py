#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Draw(object):
	def __init__(self,todolist,name):
		self.todolist=todolist
		self.name=name
	def draw_TODO(self):
		colorchange(self.name)
		print("* * * * %s * * * * *"%self.name)
		print("-"*40)
		for each in self.todolist:
			try:
				print('{:<3}{:<35}{:<}'.format(each[0],each[1],each[2]))
			except IndexError:
				pass
	def draw_string(string):
		print(string+'\n')


def colorchange(name):
	if 'Today' in name:
			print('\033[32m')
	if 'Future' in name:
			print('\033[33m')
	if 'Gone' in name:
			print('\033[31m')
	if 'Complete' in name:
			print('\033[34m')



