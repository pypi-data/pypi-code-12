import MySQLdb
import sys
import re
from sqlite3 import OperationalError
from sqlite3 import ProgrammingError
import csv
import os
import string

"""
This class will first parse the NCBI gene data and build a table called "symbol_synonym" in database
Then build a final_symbol_synonym table for mapping gene to GOterm association

Before update database, user must complete the following steps: 
a. download the newest database dump: http://archive.geneontology.org/latest-lite/
b. add .sql to current database dump file, for example: change "go_20151003-assocdb-data" to "go_20151003-assocdb-data.sql"
c. log into database on server and type the following command:
	DROP DATABASE IF EXISTS assocdb
	CREATE DATABASE IF EXISTS assocdb
	quit
d. type the following command: 
        mysql -h localhost -u username -p assocdb <dbdump
   for example: 
        mysql -h localhost -u username -p assocdb <go_20151003-assocdb-data.sql
e. download newest NCBI homo gene file: http://www.ncbi.nlm.nih.gov/gene/
click Download/FTP on left column, directory is Data —> GENE_INFO —> Mammalia —> Homo_sapiens.gene_info.gz, after download it, change file type to .txt

Then Create an instance for updating database and call function to update.
Parameters:
a. homo_gene_directory is the directory that of the previous downloaded NCBI homo gene txt file. 

Example of updating database: 
mydb = updateDB.UpdateDB(host, username, password, "assocdb”, homo_gene_directory)
mydb.update()

"""
class UpdateDB:

	## construct a database connector
	# @param host  
	# @param user 
	# @param password
	# @param NCBI_filepath directory of NCBI file
	# @param NCBI_csv directory for storing the parsed NCBI file
	# @param updateDB_sqlfile directory of updataDB_sqlfile 
	def __init__(self, host, user, password, dbname, NCBI_filepath):
		"""
		This class is a database connector
		@param host  
		@param user 
		@param password
		@param NCBI_filepath directory of NCBI file
		@param updateDB_sqlfile directory of updataDB_sqlfile 
		"""
		self.db = MySQLdb.connect(host, user, password, dbname)
		self.NCBI_filepath = NCBI_filepath
		self.parsedNCBI_filepath = self.determine_path() + "/extra_file" 
		self.updateDB_sqlfile = self.determine_path() + "/extra_file/updateDB.sql"

	## reading and execuating sqlfiles
	# @param sql_file directory of sqlfile
	def exec_sql_file(self, sql_file):
		"""
		reading and executing sqlfiles
		@param sql_file directory of sqlfile
		"""
		cursor = self.db.cursor()
		print "\n[INFO] Executing SQL script file: '%s'" % (sql_file)
		statement = ""
		for line in open(sql_file):
			if re.match(r'--', line):  # ignore sql comment lines
				continue
			if not re.search(r'[^-;]+;', line):  # keep appending lines that don't end in ';'
				statement = statement + line
			else:  # when you get a line ending in ';' then exec statement and reset for next statement
				statement = statement + line
				#print "\n\n[DEBUG] Executing SQL statement:\n%s" % (statement)
				try:
					cursor.execute(statement)
				except (OperationalError, ProgrammingError) as e:
					print "\n[WARN] MySQLError during execute statement \n\tArgs: '%s'" % (str(e.args))
				statement = ""


	## read NCBI gene data and extract only homo sapiens gene symbol and synonym
	# @param ncbi_file: directory of ncbi_file
	# @return parsed ncbi gene data
	def parseNCBI(self):
		"""
		read NCBI gene data and extract only homo sapiens gene symbol and synonym
		@return parsed ncbi gene data
		"""
		inputfile=open(self.NCBI_filepath, "r")
		reader=csv.reader(inputfile)
		try:
			os.remove(self.parsedNCBI_filepath + '/NCBI_homo_genes.csv')
		except OSError:
			pass  
		with open(self.parsedNCBI_filepath + '/NCBI_homo_genes.csv', 'wb') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',')
			for line in reader:
				currentline = line[0].split("\t")
				NCBIid = currentline[1]
				symbol = currentline[2] 
				synonmys= currentline[4]
				if synonmys!="-" :
					synonmylist=synonmys.split("|")
					for i in range(0,len(synonmylist)):
						row = ["null", NCBIid, symbol, synonmylist[i]]
						writer.writerow(row)
		# print "NCBI_offical_symbol.csv is generated"
		inputfile.close()

	## dump parsed NCBI gene symbol into assocdb as a table named symbol_synonym
	def updateNCBI(self):
		"""
		dump parsed NCBI gene symbol into assocdb as a table named symbol_synonym
		"""
		self.parseNCBI()
		cursor = self.db.cursor()
		cursor.execute("DROP TABLE IF EXISTS symbol_synonym")
		cursor.execute("CREATE TABLE symbol_synonym (id int(11) AUTO_INCREMENT, NCBIid int (11), symbol varchar(15), synonym varchar(15), PRIMARY KEY (id))")
		csv_data = csv.reader(open(self.parsedNCBI_filepath + '/NCBI_homo_genes.csv','r'))
		for row in csv_data:
			symbol = self.escapeSingleQuote(row[2])
			synonym = self.escapeSingleQuote(row[3])
			query = "INSERT INTO symbol_synonym (id, NCBIid, symbol, synonym) VALUES (%s, %s, '%s', '%s')"%(row[0], row[1], symbol, synonym)
			cursor.execute(query)
		#close the connection to the database.
		self.db.commit()
		cursor.close()
		# print "NCBI symbol_synonym table is updated"

	## escape single quote in sql
	def escapeSingleQuote(self, word):
		"""
		escape single quote in sql
		"""
		return string.replace(word,"'","''")
	
	## read the updateDataBase.sql script and execute it
	# updateDataBase.sql is creating a final_symbol_synonym table, which is mapping symbols and synonyms to GO terms for later use
	def update(self):
		"""
		read the updateDataBase.sql script and execute it
		updateDataBase.sql is creating a final_symbol_synonym table, which is mapping symbols and synonyms to GO terms for later use
		"""
		self.updateNCBI()
		cursor = self.db.cursor()
		self.exec_sql_file(self.updateDB_sqlfile)
		print "final_symbol_synonym table is updated"
	
	def determine_path(self):
		try:
			root = __file__
			if os.path.islink (root):
				root = os.path.realpath (root)
			return os.path.dirname (os.path.abspath (root))
		except:
			print "I'm sorry, but something is wrong."
			print "There is no __file__ variable. Please contact the author."
			sys.exit ()
