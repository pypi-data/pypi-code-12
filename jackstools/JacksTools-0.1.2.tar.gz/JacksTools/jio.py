'''
Small Module for managing basic file io

quick rundown:

	contains astropy.io.fits for quick access
	contains a quick csv/dat loader

'''
import ast
from astropy.io import fits
import numpy as np

def load(fname, delimiter = ',', escchar = '#', headed = False):

	with open(fname,'rb') as f: 
		headers = None
		skips = 0
		for line in f:
			if not line.startswith(escchar):
				if headed and headers is None: 
					headers = line.strip().split(delimiter)
					skips += 1
					continue
				formats = []
				for item in line.strip().split(delimiter):
					try:
						fm = np.dtype(type(ast.literal_eval(item.strip('+'))))
					except ValueError:
						fm = np.dtype(type(item))
					except SyntaxError:
						fm  = np.dtype(type(item))
					formats.append(fm)
				break
			elif line[1] != escchar:
				headers = line[1:].strip().split(delimiter)
		f.seek(0)
		for i in xrange(skips):
			f.readline()
		
		if headers is None:
			headers = map(str,range(len(formats)))
		return np.array([tuple(line.strip().split(delimiter)) for line in f if not line.startswith('#')], dtype = zip(headers, formats))

