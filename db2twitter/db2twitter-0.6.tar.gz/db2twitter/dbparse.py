# -*- coding: utf-8 -*-
# Copyright © 2015-2016 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/

# DbParse class
'''DbParse class'''

# standard libraries imports
import sys

# 3rd party libraries imports
from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base

# app libraries imports
from db2twitter.wasposted import WasPosted

class DbParse(object):
    '''DbParse class'''
    def __init__(self, cfgvalues, sqlitesession):
        '''Constructor of the DbParse class'''
        self.sqlitesession = sqlitesession
        self.mainid = ''
        self.firstrun = True
        # Create and engine and get the metadata
        Base = declarative_base()
        engine = create_engine('{}://{}:{}@{}/{}'.format(cfgvalues['dbconnector'],
            cfgvalues['dbuser'],
            cfgvalues['dbpass'],
            cfgvalues['dbhost'], 
            cfgvalues['database']))
        meta = MetaData()
        meta.reflect(bind=engine)
        
        tableobjects = []
        tableschemas = {}
        # load schemas of tables
        for table in cfgvalues['rows']:
            tableschemas[table] = Table(table, meta, autoload=True, autoload_with=engine)

        #Create a session to use the tables    
        session = create_session(bind=engine)

        # find how many new tweets to send
        sqliteobj = self.sqlitesession.query(WasPosted.lastinsertid).order_by(WasPosted.lastinsertid.desc()).first()
        if sqliteobj:
            sqlitemaxid = sqliteobj.lastinsertid

        dbtables = [i for i in cfgvalues['dbtables'].split(',') if i !='']

        if not cfgvalues['ids']:
            tableobj = session.query(tableschemas[dbtables[0]]).order_by(tableschemas[dbtables[0]].columns.id.desc()).first()
            self.lastinsertid = getattr(tableobj, 'id')
        else:
            tabrequest = '{}'.format(cfgvalues['ids'][dbtables[0]])
            tableobj = session.query(tableschemas[dbtables[0]]).order_by(getattr(tableschemas[dbtables[0]].columns, tabrequest).desc()).first()
            self.lastinsertid = getattr(tableobj, cfgvalues['ids'][dbtables[0]])

        self.tweets = []
        self.allfields = []

        if sqliteobj:
            self.firstrun = False
            for table in cfgvalues['rows']:
                # if the table does not have a user-specified row 'id'
                if not cfgvalues['ids']:
                    if cfgvalues['sqlfilter']:
                        filterrequest = '{}'.format(cfgvalues['sqlfilter'][table])
                        tableobj = session.query(tableschemas[table]).filter(tableschemas[table].columns.id > sqlitemaxid, text(filterrequest))
                    else:
                        tableobj = session.query(tableschemas[table]).filter(tableschemas[table].columns.id > sqlitemaxid)
                else:
                    tabrequest = '{}'.format(cfgvalues['ids'][table])
                    if cfgvalues['sqlfilter']:
                        filterrequest = '{}'.format(cfgvalues['sqlfilter'][table])
                        tableobj = session.query(tableschemas[table]).filter(getattr(tableschemas[table].columns, tabrequest) > sqlitemaxid, text(filterrequest))
                    else:
                        tableobj = session.query(tableschemas[table]).filter(getattr(tableschemas[table].columns, tabrequest) > sqlitemaxid)

                # ignore the None query result
                if tableobj:
                    for tweetindb in tableobj:
                        if table in cfgvalues['images']:
                            # split the different fields we need, last field is the image path
                            self.tweets.append({'withimage': True, 'data': [getattr(tweetindb, i) for i in cfgvalues['rows'][table]]})
                        else:
                            self.tweets.append({'withimage': False, 'data': [getattr(tweetindb, i) for i in cfgvalues['rows'][table]]})

        else:
            self.firstrun = True
            for table in cfgvalues['rows']:
                # if the table does not have a user-specified row 'id'
                if not cfgvalues['ids']:
                    if cfgvalues['sqlfilter']:
                        filterrequest = '{}'.format(cfgvalues['sqlfilter'][table])
                        tableobj = session.query(tableschemas[table]).filter(tableschemas[table].columns.id <= self.lastinsertid, text(filterrequest))
                    else:
                        tableobj = session.query(tableschemas[table]).filter(tableschemas[table].columns.id <= self.lastinsertid)
                else:
                    tabrequest = '{}'.format(cfgvalues['ids'][table])
                    if cfgvalues['sqlfilter']:
                        filterrequest = '{}'.format(cfgvalues['sqlfilter'])
                        tableobj = session.query(tableschemas[table]).filter(getattr(tableschemas[table].columns, tabrequest) <= self.lastinsertid, text(filterrequest))
                    else:
                        tableobj = session.query(tableschemas[table]).filter(getattr(tableschemas[table].columns, tabrequest) <= self.lastinsertid)

                # ignore the None query result
                if tableobj:
                    for tweetdb in tableobj:
                        if table in cfgvalues['images']:
                            # split the different fields we need, last field is the image path
                            self.tweets.append({'withimage': True, 'data': [getattr(tweetdb, i) for i in cfgvalues['rows'][table]]})
                        else:
                            # split the different fields we need
                            self.tweets.append({'withimage': False, 'data': [getattr(tweetdb, i) for i in cfgvalues['rows'][table]]})

        # lets quit now if nothing new to tweet
        if not self.tweets:
            sys.exit(0)

    @property
    def dbvalues(self):
        '''Database parsed values'''
        return (self.tweets, self.lastinsertid, self.firstrun)
