'''this is a xxx'''
def lol2(tlist,level=0):
	for name1 in tlist:
		if isinstance(name1,list):
			lol2(name1,level+1)
		else:
			for tab in range(level):
				print('\t',end='')
			print(name1)
