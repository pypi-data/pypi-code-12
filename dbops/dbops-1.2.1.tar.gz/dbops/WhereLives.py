
"""Perform a search for databases on hosts.

This module allows for command line or programtic checking of
specified hosts for a particular database, or the reverse.
-Ryan Birmingham
"""


from sqlalchemy import create_engine, inspect


class WhereLives(object):
    """An object to keep track of a search or searches.

    Args:
        searchkey (str): The database or host to search for.
        hostlist: A list, file, or file path containing a list of hosts.
        dbtype: The database server type. (e.g: 'my', 'pg', 'lt', 'ms')
            see dbmap for supported types and abbreviations.
        permissions: A dict, list, file, or file path containing username
            and password.
        reverse (bool): True to search on host for databases.
    """

    dbmap = {'my': 'mysql', 'pg': 'postgresql', 'or': 'oracle',
             'ms': 'mssql', 'lt': 'sqlite', 'rs': 'redshift'}

    def __init__(self, searchkey=None, hostlist=None,
                 permissions=None, dbtype="my", reverse=False):
        """initalize, trying to normalize input."""
        self.dbtype = self.dbmap[dbtype]
        if type(searchkey) is not str:
            raise TypeError('String expected for searchkey.')
        else:
            self.searchkey = searchkey
        # if hostlist looks like a list, then use it
        if type(hostlist) is list:
            self.hostlist = hostlist
        else:
            if type(hostlist) is not file:
                try:
                    hostlist = open(hostlist)
                except IOError:
                    raise IOError('Hostlist file interpreted as path,'
                                  'not found')
                except TypeError:
                    raise TypeError('hostlist input type not understood')
            self.hostlist = hostlist.read().splitlines()
        # let permissions None work
        if permissions is None:
            self.permissions = None
        else:
            if type(permissions) is dict:
                self.permissions = permissions
            elif type(permissions) is list:
                # convert to dict
                temp_per = {}
                try:
                    temp_per['username'] = permissions[1]
                    temp_per['password'] = permissions[2]
                except IndexError:
                    raise TypeError("permissions missing information")
                self.permissions = temp_per
            else:
                if type(permissions) is not file:
                    try:
                        permissions = open(permissions)
                    except IOError:
                        raise IOError('permissions interpreted as file path,'
                                      'not found')
                    except TypeError:
                        raise TypeError('permissions type not understood')
                permissions = permissions.read().splitlines()
                temp_per = {}
                try:
                    temp_per['username'] = permissions[1]
                    temp_per['password'] = permissions[2]
                except IndexError:
                    raise TypeError("permissions missing information")
                self.permissions = temp_per
        self.reverse = reverse

    def __repr__(self):
        """Return a string for python."""
        return "WhereLives object searching for " + self.searchkey

    def __str__(self):
        """Return a string for command line invoke."""
        a = "Wherelives searching for " + self.searchkey + "on "
        return a + str(self.hostlist)

    def get_schema(self):
        """Get all databases for listed hosts.

        Returns:
            list of lists, in the form [host, database]
        """
        res = []
        for host in self.hostlist:
            if self.permissions is not None:
                engine = create_engine(self.dbtype + '://' +
                                       self.permissions['username'] + ":" +
                                       self.permissions['password'] + "@" +
                                       host)
            else:
                engine = create_engine(self.dbtype + '://' +
                                       host)
            inspector = inspect(engine)
            one_res = [[host, x]
                       for x in inspector.get_schema_names()]
            res.append(one_res)
        return res

    def search(self):
        """Perform a search as specified in object type."""
        schema_list = self.get_schema()
        if self.reverse:
            result = [x for x in schema_list if
                      self.searchkey.lower() in x[0].lower()]
        else:
            result = [x for x in schema_list if
                      self.searchkey.lower() in x[1].lower()]
        return result

if __name__ == "__main__":
    import sys
    args = ['test', ['localhost'],
            {'username': 'root', 'password': 'toor'}, 'my', 'false']
    for x in range(0, len(sys.argv)-1):
        args[x] = sys.argv[x]
    searcher = WhereLives(args[0], args[1], args[2], args[3], args[4])
    print((searcher.__str__())+'\n')
    print(searcher.search())
