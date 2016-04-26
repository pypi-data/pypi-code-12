# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2014 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Fabric Library for MySQL
"""

from __future__ import unicode_literals

from fabric.api import sudo, hide, get


def user_exists(name, host='localhost'):
    """
    Determine if a given MySQL user exists.
    """
    user = sql("SELECT User FROM user WHERE User = '{0}' and Host = '{1}'".format(name, host), database='mysql')
    return user == name


def create_user(name, host='localhost', password=None, checkfirst=True):
    """
    Create a MySQL user account.
    """
    if not checkfirst or not user_exists(name, host):
        sql("CREATE USER '{0}'@'{1}';".format(name, host))
    if password:
        with hide('running'):
            sql("SET PASSWORD FOR '{0}'@'{1}' = PASSWORD('{2}');".format(
                name, host, password))


def drop_user(name, host='localhost'):
    """
    Drop a MySQL user account.
    """
    sql("drop user '{0}'@'{1}'".format(name, host))
    

def db_exists(name):
    """
    Determine if a given MySQL database exists.
    """
    db = sql("SELECT SCHEMA_NAME FROM SCHEMATA WHERE SCHEMA_NAME = '{0}'".format(name), database='information_schema')
    return db == name


def table_exists(name, database):
    """
    Determine if a given table exists within the given MySQL database.
    """
    table = sql("SELECT TABLE_NAME FROM TABLES WHERE TABLE_SCHEMA = '{0}' AND TABLE_NAME = '{1}'".format(database, name), database='information_schema')
    return table == name


def create_db(name, checkfirst=True, user=None):
    """
    Create a MySQL database.
    """
    if not checkfirst or not db_exists(name):
        sudo('mysqladmin create {0}'.format(name))
        if user:
            grant_access(name, user)


def drop_db(name, checkfirst=True):
    """
    Drop a MySQL database.
    """
    if not checkfirst or db_exists(name):
        sudo('mysqladmin drop --force {0}'.format(name))


def grant_access(dbname, username):
    """
    Grant full access to the given database for the given user.  Note that the
    username should be given in MySQL's native format, e.g. 'myuser@localhost'.
    """
    sql('grant all on `{0}`.* to {1}'.format(dbname, username))


def sql(sql, database=''):
    """
    Execute some SQL.
    """
    sql = '"{0}"'.format(sql) if sql.find("'") >= 0 else "'{0}'".format(sql)
    return sudo('mysql --execute={0} --batch --skip-column-names {1}'.format(sql, database))


def download_db(name, destination=None):
    """
    Download a database from the "current" server.
    """
    if destination is None:
        destination = './{0}.sql.gz'.format(name)
    sudo('mysqldump --result-file={0}.sql {0}'.format(name))
    sudo('gzip --force {0}.sql'.format(name))
    get('{0}.sql.gz'.format(name), destination)
    sudo('rm {0}.sql.gz'.format(name))
