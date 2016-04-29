from yamlns import namespace as ns

def fetchNs(cursor):
	"""
		Wraps a database cursor so that instead of providing data
		as arrays, it provides objects with attributes named
		as the query column names.
	"""

	fields = [column.name for column in cursor.description]
	for row in cursor:
		yield ns(zip(fields, row))
	raise StopIteration

def nsList(cursor) :
	"""
		Given a database cursor, returns a list of objects with the fields
		as attributes for every returned row.
		Use fetchNs for a more optimal usage.
	"""
	return [e for e in fetchNs(cursor) ]

def csvTable(cursor) :
	"""
		Returns retrieved rows as a tab separated values csv with proper headers.
	"""
	fields = [column.name for column in cursor.description]
	return '\n'.join('\t'.join(str(x) for x in line) for line in ([fields] + cursor.fetchall()) )



