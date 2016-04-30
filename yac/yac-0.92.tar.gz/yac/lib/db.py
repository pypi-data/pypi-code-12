#!/usr/bin/env python

import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

# describes how to connect to a DB
# used for inputs to most functions below
class DB():

    def __init__(self, 
                 db_name,
                 db_user,
                 db_pwd,
                 db_host,
                 db_port,
                 db_engine):

        self.configs = {}

        self.configs['db_name'] = db_name
        self.configs['db_user'] = db_user
        self.configs['db_pwd']  = db_pwd
        self.configs['db_host'] = db_host
        self.configs['db_port'] = db_port        
        self.configs['engine'] = db_engine

# get the driver corresponding to the os we are running on
def get_db_driver(this_os = os.name):

    # drivers that seem to work best include:
    # windows:  pyodbc
    # macos:    pymssql

    if this_os == 'posix':
        # for posix-compliant os like macos
        driver = 'pymssql'
    else:
        # for windows this one seems to work best
        driver = 'pyodbc'

    return driver

# get connection string for connecting to an ms-sql RDBMS 
# db is an instance of the DB class
def get_connection_string(db):
    connection = ""
    driver = get_db_driver()
    if db.configs['engine']=='mssql':
        connection = "mssql+%s"%driver
    elif db.configs['engine']=='postgres':
        connection = 'postgresql'

    return "%s://%s:%s@%s/%s" % (connection, 
                                        db.configs['db_user'], 
                                        db.configs['db_pwd'], 
                                        db.configs['db_host'], 
                                        db.configs['db_name'])

# connect to database
# db is an instance of the DB class
def connect_to_db(db):
    return create_engine(get_connection_string(db))
    
# get an executable table (a table that alchemy commands can be run against)
# db is an instance of the DB class
def get_table(table_name, db):

    engine = connect_to_db(db)
    connection = engine.connect()
    metadata = MetaData(engine)

    # build table
    return Table(table_name, metadata, autoload=True)

def get_session(db):

    engine = connect_to_db(db)

    # create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # create a Session
    session = Session()    