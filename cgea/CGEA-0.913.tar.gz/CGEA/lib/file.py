# set of utilities to interact with files

# @author: rm3086 (at) columbia (dot) edu

import csv, shutil, os, glob, cPickle, jsonpickle, json
from log import slogger

log = slogger ('CGEA')

# read an object (list, dictionary, set) from a serialized file
def read_obj (filename):
	try:
		data = cPickle.load (open(filename, 'rb'))
		return data
	except Exception as e:
		log.error(e)
		return None


# write an object (list, set, dictionary) to a serialized file
def write_obj (filename, data):
	try:
		cPickle.dump(data, open(filename, 'wb'))
		return True
	except Exception as e:
		log.error(e)
		return False
	
# read a text file
def read_file (filename):
	fid = open(filename, 'r')
	data = []
	for line in fid:			
		if len(line) > 0:
			line
			data.append (line.strip())		
	fid.close()
	return data

# read an dictionary from a json file
def read_JSON (filename, encoding = 'utf-8'):
	try:
		return json.load(open(filename, 'r'), encoding = encoding)
	except Exception as e:
		log.error(e)
		return None


# write a dictionary to a json file
def write_JSON (filename, data, encoding = 'utf-8'):
	try:
		json.dump(data, open(filename, 'w'), sort_keys = True, indent = 4, encoding = encoding)
		return True
	except Exception as e:
		log.error(e)
		return False

# read data from a csv file    
def read_csv (filename):
	try:
		reader = csv.reader (open(filename, "r"), escapechar='\\')
		data = []
		for r in reader:
			data.append(r)
		return data
	except Exception as e:
		log.error(e)
		return False

# read data from a csv file    
def read_csv_universal_newline (filename, delimiter = ","):
	try:
		reader = csv.reader (open(filename, "rU"), escapechar='\\', delimiter = delimiter)
		data = []
		for r in reader:
			data.append(r)
		return data
	except Exception as e:
		log.error(e)
		return False

# read a text file
def read_file (filename):
	try:
		fid = open(filename, 'r')
		data = []
		for line in fid:			
			if len(line) > 0:
				data.append (line.strip())		
		fid.close()
		return data
	except Exception as e:
		log.error(e)
		return False


# write data to a csv file
def write_csv (filename, data, quotechar='"', append = False, delimiter = ',', pivot = False):
	if quotechar is None: quoting=csv.QUOTE_NONE
	else: quoting=csv.QUOTE_ALL
	if append: writetype = 'a'
	else: writetype = 'wb'
	if pivot: data = zip(*data)
	try:
		doc = csv.writer (open(filename, writetype), delimiter=delimiter, quotechar=quotechar, quoting=quoting, escapechar = '\\')
		for d in data:
			doc.writerow (d)
		return True			
	except Exception as e:
		log.error(e)
		return False
	
# read a csv and output a list of dictionaries
def csvToDictionaryList(filename, delimiter = ','):
	try:
		reader = csv.DictReader (open(filename, "r"),delimiter = delimiter, escapechar='\\')
		data = []  
		for r in reader:
			data.append(r)
		return data
	except Exception as e:
		log.error(e)
		return False

# read a csv and output a dictionary with the keys as the specified column, and a list of dictionary rows for their result
def csvToDictionary(filename, key):
	try:
		reader = csv.DictReader (open(filename, "r"))
		data = {}
		for r in reader:
			keyvalue = r[key]
			if keyvalue in data:
				del r[key]
				data[keyvalue].append(r)
			else:
				del r[key]
				data[keyvalue] =[r]
		return data
	except Exception as e:
		log.error(e)
		return False

def dictionaryListToCSV(filename, data, fieldnames = None, encode = None, delimiter = ','):
#	try:
		if not fieldnames:
			fieldnames = sorted(data[0].keys())
		doc = csv.DictWriter (open(filename, 'wb'), fieldnames=fieldnames, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_ALL, extrasaction = 'ignore')
		doc.writeheader()
		for d in data:
			if encode:
				for key, value in d.items():
					try:
						d[key] = value.encode(encode)
					except AttributeError:
						try:
							d[key] = ';'.join(value).encode(encode)
						except Exception:
							d[key] = '' 
			doc.writerow (d)
		return True			
# 	except Exception as e:
# 		log.error(e)
# 		return False

def prettyPrint(localobject, prefix = ''):
	if len(prefix) > 40:
		print prefix+json.dumps(localobject, sort_keys=True,
	                  	 indent=4, separators=(',', ': '))
	else:
		print prefix
		print json.dumps(localobject, sort_keys=True,
	                  	 indent=4, separators=(',', ': '))