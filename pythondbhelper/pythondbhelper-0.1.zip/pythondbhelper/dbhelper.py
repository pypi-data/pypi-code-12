'''
Created on Jun 3, 2016

@author: Waqas Ali
'''
import pymysql

class dbhelper:
    def __init__(self, host, port, user, password, dbname):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__dbname = dbname
        
    def __openConnection(self):
        connection = pymysql.Connect(host=self.__host, port=self.__port, user=self.__user, passwd=self.__password, db=self.__dbname)
        return connection

    def __closeConnection(self, connection):
        if connection:
            connection.close()

    '''
    return single row
    '''
    def fetchOne(self, query):
        val = str(query).lstrip().lower()
        if val.startswith('insert') or val.startswith('update') or val.startswith('delete'):
            raise ValueError('invalid query.')
        conn = self.__openConnection()
        cur = conn.cursor() #pymysql.cursors.DictCursor
        cur.execute(query) 
        dt = cur.fetchone()
        self.__closeConnection(conn)
        return dt

    '''
    return multiple rows
    '''
    def fetchAll(self, query):
        val = str(query).lstrip().lower()
        if val.startswith('insert') or val.startswith('update') or val.startswith('delete'):
            raise ValueError('invalid query.')
        conn = self.__openConnection()
        cur = conn.cursor() #pymysql.cursors.DictCursor
        cur.execute(query) 
        dt = cur.fetchall()
        self.__closeConnection(conn)
        return dt

    '''
    insert new record
    '''
    def insertRecord(self, query):
        return self.__executeQuery(query)

    '''
    update record
    '''
    def updateRecord(self, query):
        return self.__executeQuery(query)

    '''
    delete record
    '''
    def deleteRecord(self, query):
        return self.__executeQuery(query)

    def __executeQuery(self, query):
        if str(query).lstrip().lower().startswith('select'):
            raise ValueError('invalid query.')
        conn = self.__openConnection()
        cur = conn.cursor() #pymysql.cursors.DictCursor
        cur.execute(query) 
        conn.commit()
        self.__closeConnection(conn)
        return 'Query executed successfully'
    
    '''
    about helper class.
    '''
    def aboutMe(self):
        print('Python db helper class.')
