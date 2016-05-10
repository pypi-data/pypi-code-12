			if switcher%4==0:
				try:
					future.todolist[future.cursor[0]][2]='   '
				except:
					pass
				current=today
				print("Your Current position: Today")
			elif switcher%4==1:
				try:

					today.todolist[today.cursor[0]][2]='   '
				except:
					pass
				current=future
				print("Your Current position: Future")
			elif switcher%4==2:
				
				try:
					post.todolist[post.cursor[0]][2]='   '
				except:
					pass

				current=post
				print("Your Current position: Gone")
			elif switcher%4==3:
				
				try:
					comp.todolist[post.cursor[0]][2]='   '
				except:
					pass
