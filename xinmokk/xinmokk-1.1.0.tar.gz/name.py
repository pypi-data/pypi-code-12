'''this is a xxx'''
def lol(tlist):
	for name1 in tlist:
		if isinstance(name1,list):
			lol(name1)
		else:
			print(name1)
