
from datetime import date

class Dumdba(object):
	""" 
	Esta pequela biblioteca oferece suporte a conexao com banco de dados Mysql sem necessitar de uma framework
	"""
	
	def __init__(self, host, user, passwd, db, dbms = 'MYSQL'):
		"""
		Construtor - efetua a conexao com o banco de dados
		Parametros:
			host:	(str) endereco do banco de dados
			user: 	(str) usuario do banco de dados
			passw: 	(str) senha do usuario do banco de dados
			db: 	(str) base de dados que sera efetuada as transacoes
			[dbms:	(str) definicao do sgbd usado
		"""

		self.__host   = host
		self.__user   = user
		self.__passwd = passwd
		self.__db     = db

		if dbms == 'MYSQL':
			import MySQLdb as Dbms
			self.__con = Dbms.connect(host= host, user= user, passwd = passwd, db= db)

		self.__cur = self.__con.cursor(Dbms.cursors.DictCursor)

	def __del__(self):
		"""Destrutor - fecha a conexao com o banco de dados"""
		self.__cur.close()
		self.__con.close()

	def __commit(self):
		self.__con.commit()

	def rowcount(self):
		"""
		Retorna o numero de linhas presente no cursor.
		"""
		return self.__cur.rowcount

	def __execute(self, query, data = {},commit = False):

		if data:
			self.__cur.execute(query,data)
		else:
			self.__cur.execute(query)

		if self.rowcount() > 0:
			if commit:
				self.__commit()
			return True
		return False

	def __fetch(self, query, data = {}, one_row = True, commit = False):
		if self.__execute(query,data = data, commit = commit):
			if one_row:
				return self.__cur.fetchone()
			else:
				return list(self.__cur.fetchall())
		else:
			return False



	def __select_row(self, table_name, columns = [], where = '', group = '', order = '',
					 limit = 0, one_row = True, ret_numrows = False, commit = False):
		
		if columns:
			colunas = []
			for val in columns:
				if isinstance(val,tuple):
					colunas.append(str(val[0]) + ' AS ' + str(val[1]))
				else:
					colunas.append(str(val))
			query = 'SELECT ' + ','.join(colunas) + ' FROM '
		else:
			query = 'SELECT * FROM '

		query += str(table_name)

		if where:
			query += ' WHERE ' + str(where)
		if group:
			query += ' GROUP BY ' + str(group)
		if order:
			query += ' ORDER BY ' + str(order)
		if one_row:
			query += ' LIMIT 1'	
		elif limit:
			query += ' LIMIT ' + str(limit)

		fetch = self.__fetch(query, one_row = one_row, commit = commit)

		if ret_numrows:
			return self.rowcount()
		return fetch

	def __insert_row(self, table_name, data, default_data = {}, commit = False):
		query = 'INSERT INTO ' + str(table_name) + ' ('

		colunas = []
		values  = []

		for index in data:
			colunas.append(str(index))
			if data[index] == None:
				values.append('NULL')
			elif isinstance(data[index], list):
				values.append(str(data[index][0]))
			elif isinstance(data[index],int) or isinstance(data[index],float) or isinstance(data[index],long):
				values.append(str(data[index]))
			else:
				values.append('\''+str(data[index])+'\'')

		if default_data:
			for index in default_data:
				if not str(index) in colunas:
					colunas.append(str(index))
					if default_data[index] == None:
						values.append('NULL')
					elif isinstance(default_data[index],list):
						values.append(str(default_data[index][0]))
					elif isinstance(default_data[index],int) or isinstance(default_data[index],float) or isinstance(default_data[index],long):
						values.append(str(default_data[index]))
					else:
						values.append('\''+str(default_data[index])+'\'')

		query += ','.join(colunas) + ') VALUES (' + ','.join(values) + ')'

		return self.__execute(query,commit = commit)

	def __update_row(self, table_name, data, where = '', default_data = {}, commit = False):
		query = 'UPDATE ' + str(table_name) + ' SET '

		colunas = []
		values  = []

		for index in data:
			colunas.append(str(index))
			if data[index] == None:
				values.append('NULL')
			elif isinstance(data[index], list):
				values.append(str(data[index][0]))
			elif isinstance(data[index],int) or isinstance(data[index],float) or isinstance(data[index],long):
				values.append(str(data[index]))
			else:
				values.append('\''+str(data[index])+'\'')

		if default_data:
			for index in default_data:
				if not str(index) in colunas:
					colunas.append(str(index))
					if default_data[index] == None:
						values.append('NULL')
					elif isinstance(default_data[index],list):
						values.append(str(default_data[index][0]))
					elif isinstance(default_data[index],int) or isinstance(default_data[index],float) or isinstance(default_data[index],long):
						values.append(str(default_data[index]))
					else:
						values.append('\''+str(default_data[index])+'\'')

		compon  = [colunas[i]+'='+values[i] for i in range(len(colunas))]

		query += ','.join(compon)
		if where:
			query += ' WHERE ' + str(where)

		return self.__execute(query, commit = commit)


	def __delete_row(self,table_name, where = '', group = '', order = '', limit = 0, ret_numrows = False, commit = False):
		query = 'DELETE FROM ' + str(table_name)

		if where:
			query += ' WHERE ' + str(where)
		if group:
			query += ' GROUP BY ' + str(group)
		if order:
			query += ' ORDER BY ' + str(order)
		if limit:
			query += ' LIMIT ' + str(limit)

		ret_exec = self.__execute(query, commit = commit)
		if ret_numrows:
			return self.rowcount()
		return ret_exec


	#PUBLIC METHODS----------------------------------------------------------------------------------------------------
	def sqlexe(self,query,data={},commit = True):
		return self.__execute(query,data,commit)

	def query(self, query, data = {}, one_row = False, commit = True):
		return self.__fetch(query,data,one_row, commit = commit)

	def select(self, table_name, columns = [], where = '', group = '', order = '',
					 limit = 0, one_row = False, ret_numrows = False, commit = False):
		return self.__select_row(table_name,columns,where,group,order,limit,one_row,ret_numrows,commit)

	def insert(self, table_name, data, default_data = {}, commit = True):
		return self.__insert_row(table_name,data,default_data,commit)

	def update(self, table_name, data, where = '', default_data = {}, commit = True):
		return self.__update_row(table_name,data,where,default_data,commit)

	def delete(self,table_name, where = '', group = '', order = '', limit = 0, ret_numrows = False, commit = True):
		return self.__delete_row(table_name,where,group,order,limit,ret_numrows,commit)

class Table(object):

	def __init__(self,dumdba, table_name = ''):
		self.__dumdba = dumdba
		self.__table_name = table_name
		self.__result = False

	def __add__(self,data):
		self.__set_result(self.get_dumdba().insert(self.get_table_name(),data))
		return self

	def __sub__(self,where):
		self.__set_result(self.get_dumdba().delete(self.get_table_name(),where = where))
		return self

	def __mod__(self,where):
		res = self.get_dumdba().select(self.get_table_name(),where = where)
		self.__set_result(bool(res))		
		return res

	def get_dumdba(self):
		return self.__dumdba

	def set_dumdba(self,dumdba):
		self.__dumdba = dumdba

	def get_table_name(self):
		return self.__table_name

	def set_table_name(self,table_name):
		self.__table_name = table_name

	def result(self):
		return self.__result

	def __set_result(self,boolean):
		self.__result = boolean

	def select(self, columns = [], where = '', group = '', order = '',
					 limit = 0, one_row = False, ret_numrows = False, commit = False):
		self.get_dumdba().select(self.get_table_name(),columns,where,group,order,limit,one_row,ret_numrows,commit)

	def insert(self, data, default_data = {}, commit = True):
		self.get_dumdba().insert(self.get_table_name(),data,default_data,commit)

	def update(self, data, where = '', default_data = {}, commit = True):
		self.get_dumdba().update(self.get_table_name(),data,where,default_data,commit)

	def delete(self, where = '', group = '', order = '', limit = 0, ret_numrows = False, commit = True):
		self.get_dumdba().delete(self.get_table_name(),where,group,order,limit,ret_numrows,commit)