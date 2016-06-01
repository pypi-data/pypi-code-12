import time
import multiprocessing as mlt

import re
import MySQLdb
import sqlite3 as sqlite

from generaltools import log_tools
from generaltools.server_tools import GeneralServer


class BaseDB(object):
    """ Wrapper class around MySQLdb"""
    def __init__(self, database=None, user=None, host=None, password=None,
                 lock=False, sqlite_filename=None,
                 database_type="mysql", **kwargs):
        self.check_lock = lock or mlt.Lock()
        self.database = database
        self.user = user
        self.host = host
        self.password = password
        self.database_type = database_type
        if self.database_type == "mysql":
            self.conn = MySQLdb.connect(host=self.host, user=self.user,
                                        passwd=self.password, db=self.database)
            self.auto_increment = "NOT NULL AUTO_INCREMENT"
            self.integer = "INT"
        if self.database_type == "sqlite":
            self.conn = sqlite.connect(database)
            self.auto_increment = "AUTOINCREMENT"
            self.integer = "INTEGER"
        self.cursor = self.conn.cursor()

    def execute(self, sql):
        success=False
        i=0
        while not success:
            try:
                self.cursor.execute(sql)
                success=True
            except OperationalError as e:
                i +=1
                self.log.error("failed to execute will try again {0}" \
                               "\nFollowing error {1}".format(i, str(e)))
                time.sleep(1)
        return self.cursor

    def execute(self, sql):
        """Run and SQL command"""
        self.log.debug(sql)
        self.cursor.execute(sql)
        return self.cursor

    def commit(self):
        """Commit changes to the database"""
        self.conn.commit()

    def close_connection(self):
        """Close the database connection"""
        self.conn.close()


class GenDB(BaseDB):
    """ Providing basic procedures to work with databases"""
    def __init__(self, database=None, user=None,
                       host=None, password=None, database_type="mysql"):
        BaseDB.__init__(self, database=database, user=user,
                       host=host, password=password, 
                       database_type=database_type)
        self.tables = None

    def drop_table(self, table_name):
        """Drop table with table_name"""
        self.execute('SET FOREIGN_KEY_CHECKS = 0;')
        sql = "DROP table if exists {}".format(table_name)
        try:
            self.execute(sql)
        except MySQLdb.ProgrammingError:
            self.log.error("can not drop table does it exists")
        self.execute('SET FOREIGN_KEY_CHECKS = 1;')
        self.commit()

    def update_table_list(self):
        """get a list of existing tables"""
        if self.database_type == "mysql":
            sql = "SHOW TABLES"
        if self.database_type == "sqlite":
            sql = "SELECT name FROM sqlite_master WHERE type='table'"
            
        self.execute(sql)
        self.tables = self.cursor.fetchall()
        self.tables = [table[0] for table in self.tables]

    def check_if_table_exists(self, table_name):
        """Check if table with table_name exists"""
        self.update_table_list()
        if table_name in self.tables:
            return True
        else:
            return False

    def add_column_to_table(self, table_name, column_name, column_type):
        """Add a column to the table"""
        sql = "ALTER TABLE {} ADD COLUMN {} {} "\
              "DEFAULT NULL".format(table_name, column_name, column_type)
        self.execute(sql)
        self.commit()

    def get_column_names(self, table_name):
        """Read the names of the columns of a table"""
        if self.database_type == "mysql":
            sql = "describe {}".format(table_name)
            self.execute(sql)
            names = [str(name[0]) for name in self.cursor.fetchall()]
        if self.database_type == "sqlite":
            sql = " SELECT sql FROM sqlite_master WHERE name = '{}';".format(table_name)
            self.execute(sql)
            result = self.cursor.fetchall()[0][0]
            tmp = result.split(",")
            result = []
            for entry in tmp:
                if "CREATE" in entry:
                    entry = entry.split("(")[-1]
                result += [entry]
            names = [str(name.split()[0]) for name in result if str(name.split()[0]) != "FOREIGN"]
            names = [name.replace("`", "") for name in names]
        return names

    def add_table(self, table_name, columns):
        """Add a new table to the database if it does not exist

        Parameters
        ----------
        table_name : str
            The name of the table
        columns : dict
            Dictionary with the names of the colums as keys and the type as
            lookup values.

        """
        sql = "CREATE TABLE if not exists {0} "\
              "(id {1} PRIMARY KEY {2} ".format(table_name, self.integer, self.auto_increment)
        for column in columns.keys():
            if "FOREIGN" in columns[column]:
                columns[column] = columns[column].split(",")[0]
            else:
                sql += ", {} {}".format(column, columns[column])
        for column in columns.keys():
            if not "FOREIGN" in columns[column]:
                pass
            else:
                key = columns[column].split(",")[1]
                sql += ", {}".format(key)
        sql += ")"
        self.execute(sql)
        self.commit()
        
    def get_column_value_where(self,table_name,column_name,column_value,return_column=None):
        """ return column value where where criteria is true
        
        @param table_name table name to query
        @param column_name Column for where selection
        @param column_value value to check in where selection
        @param return_column Return value of this column, default is None and then the where column is returned
        
        example: get_column_value_where("path_table","path","/tmp/test","id")
        creates following sql
        """
        if return_column==None:
            return_column = column_name
        sql="select {3} from `{0}` where {1}='{2}'".format(table_name,column_name,column_value,return_column)
        self.execute(sql)
        result = self.cursor.fetchall()
        if result==None:
            self.log.error("value {2} not found in table {0} column {1}".format(table_name,column,value))
            sys.exit()        
        return result
    
    def get_column_value_multi_where(self,table_name,where_criteria=[],return_column=None):
        """ return column value where where criteria is true
        
        @param table_name table name to query
        @param where_criteria is an array of 3 element tuple, containing a column_name,operator and column_value
        @param column_value value to check in where selection
        @param return_column Return value of this column, default is None and then the where column is returned
        
        example: get_column_value_multi_where("path_table",[("path","="/tmp/test"),("id","="1")],"id")
        creates following sql
        """
        if return_column == None:
            return_column = "*"
        if len(where_criteria) == 0:
            self.log.info("no where criteria given, not doing anything")
            return        
        sql="select {1} from `{0}` where".format(table_name,return_column)
        for num,criteria in enumerate(where_criteria):
            column_name,operator,column_value = criteria
            sql+=" {0} {1} '{2}'".format(column_name,operator,column_value)
            print num, len(where_criteria)
            if num != len(where_criteria)-1:
               sql+=' and '        
        self.execute(sql)
        result = self.cursor.fetchall()
        if result==None:
            self.log.error("value {2} not found in table {0} column {1}".format(table_name,column,value))
            sys.exit()        
        return result
    
    def get_foreign_keys(self,table):
        """ return dictionary of foreign keys in table
        @param table        
        """
        sql="SHOW CREATE TABLE {0}".format(table)
        self.execute(sql)
        table_name,create_subscans_table_mysql = self.cursor.fetchone()
        #
        foreign_keys = {}
        for code in create_subscans_table_mysql.split("\n"):
             if "FOREIGN" in code:
                match = re.findall('`(\w+)`',code)
                foreign_keys[match[1]]="{0}.{1}".format(match[2],match[3])
        return foreign_keys

class MySQLConnection(GenDB):
    def __init__(self, database=None, user=None, host=None,
                 password=None):
        GenDB.__init__(self)
        self.database = database
        self.user = user
        self.host = host
        self.password = password
        self.conn = MySQLdb.connect(host=self.host, user=self.user,
                                    passwd=self.password, db=self.database)
        self.cursor = self.conn.cursor()
        self.type_ = "MySQL"

class SQLLiteConnection(GenDB):
    def __init__(self, file_name=None):
        GenDB.__init__(self)
        self.conn = sqlite.connect(file_name)
        self.cursor = self.conn.cursor()
        self.type_ = "SQLLite"
