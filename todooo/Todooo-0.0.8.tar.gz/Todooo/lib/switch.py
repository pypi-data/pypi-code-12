#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def switch(switcher,current,today,future,post,complete):
	if switcher%4==0:
		try:
			current.todolist[current.cursor[0]][2]='   '
		except:
			pass
		current=today
		if current.todolist:
			current.todolist[current.cursor[0]][2]=' ⬅ '
		print("Your Current position: Today")
	elif switcher%4==1:
		try:

			current.todolist[current.cursor[0]][2]='   '
		except:
			pass
		current=future
		if current.todolist:
			current.todolist[current.cursor[0]][2]=' ⬅ '
		print("Your Current position: Future")
	elif switcher%4==2:
		try:
			current.todolist[current.cursor[0]][2]='   '
		except:
			pass

		current=post
		if current.todolist:
			current.todolist[current.cursor[0]][2]=' ⬅ '
		print("Your Current position: Gone")
	elif switcher%4==3:
		
		try:
			current.todolist[current.cursor[0]][2]='   '
		except:
			pass

		current=comp
		if current.todolist:
			current.todolist[future.cursor[0]][2]=' ⬅ '
		print("Your Current position: Complete")
	
