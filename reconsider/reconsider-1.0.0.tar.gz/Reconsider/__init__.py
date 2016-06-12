# coding=utf-8
""" Reconsider Package

Used to clone DBs and Tables from one RethinkDB instance to another
"""

__author__		= "Chris Nasr"
__copyright__	= "OuroborosCoding"
__license__		= "Apache"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "ouroboroscode@gmail.com"

# Import python core modules
import math
import re
import sys

# Import pip modules
import rethinkdb as r

# Compile index regex
_INDEX_REGEX	= re.compile(r'(?:\.getField\("([^"]+)"\)|r\.row\("([^"]+)"\))')

# Number of "=" in progress bar
_PROGRESS_TICKS	= 25

# Clone
def clone(source, destination, dbs = None, verbose = False):
	"""Clone

	Clone is used to clone one or many DBs/Tables from one host to another

	Args:
		source (dict): Data specifying the source instance
			A dictionary with the following possible elements: host, port, user,
			password, timeout, ssl (see rethinkdb python api)

		destination (dict): Date specifying the destination instance
			Works the same as source, but for the destination host

		dbs (list|dict): A list of DBs
			This is the list of Databases that will be cloned. If the value is a
			list, all tables in each DB with be cloned. If the value is a dict,
			it is assumed the keys are the names of the DBs, and the value (a
			list) is the tables that will be cloned from each DB

		verbose (bool): Optional verbose flag
			If true the function will print out details about what it's doing.
			Defaults to False

	Returns:
		bool: Returns true on success

	Raises:
		ValueError: If any arguments are incorrect a ValueError will be raised
	"""

	# If the source is not a valid dict
	if not isinstance(source, dict):
		raise ValueError('source must be a dict')

	# Open a connection to the source instance
	try:
		oSource	= r.connect(**source)

	# Catch possible error
	except r.errors.RqlDriverError:
		sys.stderr.write('Can not connect to source host: ' + str(source) + '\n')
		return False

	# If the destination is not a valid dict
	if not isinstance(destination, dict):
		raise ValueError('destination must be a dict')

	# Open a connection to the destination instance
	try:
		oDest	= r.connect(**destination)

	# Catch possible error
	except r.errors.RqlDriverError:
		sys.stderr.write('Can not connect to destination host: ' + str(destination) + '\n')
		return False

	# Get all the DBs on the source
	lSourceDBs	= r.db_list().run(oSource)

	# If no DBs were specified
	if not dbs:
		dbs	= lSourceDBs

	# If the DBs were sent as a list (no tables specified)
	if isinstance(dbs, (list,tuple)):
		dbs	= {s:None for s in dbs}

	# Go through each DB listed
	for sDB,lTables in dbs.iteritems():

		# If the DB doesn't exist in the source
		if sDB not in lSourceDBs:
			sys.stderr.write('No such DB "%s" on the source host\n' % sDB)
			continue

		# Check if the DB exists on the destination
		if r.db_list().contains(sDB).run(oDest):
			sys.stderr.write('DB "%s" already exists on the destination host\n"' % sDB)
			continue

		# If verbose mode is on
		if verbose:
			sys.stdout.write('Processing DB "%s"\n' % sDB)

		# Create the DB on the destination host
		r.db_create(sDB).run(oDest)

		# Get all the tables in the DB
		lSourceTables	= r.db(sDB).table_list().run(oSource)

		# If no tables were specified
		if not lTables:
			lTables	= lSourceTables

		# Go through each Table
		for sTable in lTables:

			# If the DB doesn't exist in the source
			if sTable not in lSourceTables:
				sys.stderr.write('No such Table "%s.%s" on the source host\n' % (sDB,sTable))
				continue

			# If verbose mode is on
			if verbose:

				# Output
				sys.stdout.write('  Processing Table "%s": [%s] 0%%' % (sTable, (' ' * _PROGRESS_TICKS)))

				# Get the number of documents in the table
				fTotal	= float(r.db(sDB).table(sTable).count().run(oSource))

				# Calculate the block size
				fBlock	= fTotal / _PROGRESS_TICKS

				# Init the count and the ticks
				iCount	= 0
				iTicks	= 0

			# Get the primary key of the table
			sKeyField	= r.db(sDB).table(sTable).info().run(oSource)['primary_key']

			# Create the Table
			r.db(sDB).table_create(sTable, primary_key=sKeyField).run(oDest)

			# Get the list of indexes
			lIndexes	= r.db(sDB).table(sTable).index_status().run(oSource)

			# Create each index
			for dIndex in lIndexes:

				# Pull out the name
				sName	= dIndex['index']

				# Pull out the fields
				oMatches	= _INDEX_REGEX.findall(dIndex['query'])

				# If there's only one field
				if len(oMatches) == 1:

					# Create a single field index
					r.db(sDB).table(sTable).index_create(oMatches[0][0]).run(oDest)

				# Else if the index is comprised of multiple fields
				else:

					# Pull out each field
					lFields	= []
					for tMatch in oMatches:
						lFields.append(r.row[tMatch[1]])

					# Create a multi-index field
					r.db(sDB).table(sTable).index_create(sName, lFields).run(oDest)

			# Copy the data one document at a time
			for dDoc in r.db(sDB).table(sTable).run(oSource):

				# Copy the document to the destination
				r.db(sDB).table(sTable).insert(dDoc).run(oDest)

				# If verbose mode is on
				if verbose:

					# Increment the count
					iCount	+= 1

					# Get the number of ticks
					iTemp	= int(round(float(iCount) / fBlock))

					# If the ticks are more than the previous
					if iTemp > iTicks:
						iTicks	= iTemp

						# Output
						sys.stdout.write('\r  Processing Table "%s": [%s%s] %d%%' % (
							sTable,
							('=' * iTicks),
							(' ' * (_PROGRESS_TICKS - iTicks)),
							(iTicks * 4)
						))
						sys.stdout.flush()

			# If verbose mode is on
			if verbose:

				# Output
				sys.stdout.write('\r  Processing Table "%s": [%s] 100%%\n' % (sTable, ('=' * _PROGRESS_TICKS)))
