#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Todooo.lib import useraction,checklist,datatrans,draw,operation,movement
import os
#from . import helpdoc


def your_todolist(userid):

	today=checklist.TODO('* * * * Today * * * *')
	
	future=checklist.TODO('* * * * Future * * * *')

	post=checklist.TODO('* * * * Gone * * * *')
	
	comp=checklist.TODO('* * * * Complete * * * *')
	switcher=0
	status={0:today,
			1:future,
			2:post,
			3:comp}
	current=today

	def init():

		try:

			datatrans.loadall(userid,today,future,post,comp)
		except FileNotFoundError:
			today.reset('Reset')
			future.reset('Reset')
		current.todolist[current.cursor[0]][2]=' ⬅ '
		

	def GoToDo():
		
		nonlocal switcher
		nonlocal current
		while True:
			#Draw the list
			os.system('clear')
			a=draw.Draw(today.todolist,today.name)
			b=draw.Draw(future.todolist,future.name)
			c=draw.Draw(post.todolist,post.name)
			d=draw.Draw(comp.todolist,comp.name)
			a.draw_TODO()
			b.draw_TODO()
			c.draw_TODO()
			d.draw_TODO()

			print('\033[0;30;47m')
			print('\033[0m')
			print("-"*40)
			#Here is a problem
			if switcher%4==0:
				print("Your Current position: Today")
			elif switcher%4==1:
				print("Your Current position: Future")
			elif switcher%4==2:
				print("Your Current position: Gone")
			elif switcher%4==3:
				print("Your Current position: Complete")
			
			print("* * * * * * * Description * * * * * * *\n")
			print('\033[95m')
			try:
				print("->",current.todolist[current.cursor[0]][3])
				
			except:
				print("Nothing here")
			print('\033[0m')
			print("- - - - - - - - - - - - - - - - - - - -")

			action = useraction.get_user_action()
			
			
			if action == 'Switch':
				try:
					current.todolist[current.cursor[0]][2]='   '
				except:
					pass
				switcher+=1
				current=status[switcher%4]
				if current.todolist:
					current.todolist[current.cursor[0]][2]=' ⬅ '
				continue
			
			if action in useraction.moves:
				while True:		
					
					if len(current.todolist) ==(current.cursor[0]+1) and action == 'Down':
						print("Uhoh..Out of Range..")						
						break
					elif current.cursor[0]==0 and action == 'Up':
						print("Uhoh..Out of Range..")					
						break
					else:
						movement.moves(action,current)
						break
				continue
			else:
				op=operation.Operation(current,post,comp,future,today)
				if op.execution(action,userid)==0:
					return False
				
				
	os.system('clear')
	#helpdoc.import_info()
	init()

	GoToDo()
	

