
def countLines(filename, buf_size=1048576):
	'''
	fast counting to the lines of a given filename
	through only reading out a limited buffer
	'''
	f = open(filename)
	try:
		lines = 1
		read_f = f.read # loop optimization
		buf = read_f(buf_size)
		# Empty file
		if not buf:
			return 0
		while buf:
			lines += buf.count('\n')
			buf = read_f(buf_size)
		return lines
	finally:
		f.close()


if __name__ == '__main__':
	import __main__
	f = __main__.__file__
	print("file %s has %s lines" %(f, countLines(f)) )