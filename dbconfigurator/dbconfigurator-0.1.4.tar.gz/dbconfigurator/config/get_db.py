import dataset
import json
import os
script_dir = os.path.dirname(os.path.abspath(__file__))



def register_config():
    connection = {}
    try:
        input = raw_input
    except NameError:
        pass
    
    connection['profile_name'] = input('Profile Name? ')
    connection['dbms'] = input('DBMS? ')
    connection['user'] = input('username? ')
    connection['password'] = input('Password? ')
    connection['module'] = input('DB Driver Name? (python package)')
    connection['host'] = input('Host? ')

    connection['port']= input('Port? ')
    connection['charset'] = input('Charset? ')
        
    with open(str(script_dir) + '/config_{profile_name}.json'.format(profile_name=connection['profile_name']), 'w') as f:
        json.dump(f, connection)



class Configurator:
    def __init__(self, profile_name = 'default', script_dir=script_dir, dbname=''):
        self.jsonpath = str(script_dir) + '/config_default.json'
        self.dbname = dbname
        
        with open(self.jsonpath) as config:
            self.CONFIG = json.load(config)
            self.dbms = CONFIG['dbms']
            self.user = CONFIG['user']
            self.module = CONFIG['module']
            self.password = CONFIG['password']
            self.host = CONFIG['host']
            self.port = CONFIG['port']
            self.charset = CONFIG['charset']

            if self.dbname != '':
                self.dbname = '/' + self.dbname
            self.url ='{dbms}+{module}://{user}:{password}@{host}:{port}/{dbname}?charset=self.utf8'.format(dbms=self.dbms,module=self.module, user=self.user, password=self.password, host=self.host, port=self.port, dbname=self.dbname)
    
    
    
    def get_db(self):
        return dataset.connect(self.url)

    def get_engine(self):
        db = self.get_db()
        return db.engine
