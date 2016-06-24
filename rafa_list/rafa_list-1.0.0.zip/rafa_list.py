def rafa(o):
	if isinstance(o,list):
		for n in o:
			rafa(n)
	else:
		print (o)
