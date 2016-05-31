'''this is a xxx'''
def lol2(tlist,indent=False,level=0):
	for name1 in tlist:
		if isinstance(name1,list):
			lol2(name1,indent,level+1)
		else:
			if indent:
				for tab in range(level):
					print('\t',end='')
			print(name1)
