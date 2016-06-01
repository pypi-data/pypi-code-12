import sqlalchemy, consul

db = {}

class Database:
    env = None
    c = consul.Consul(host='consul.service.onestop')

    def __init__(self, env):
        self.env = env

        index, data = self.c.kv.get('global/config/%s/common/DBConnections/MSIC/sqlalchemy' % self.env)
        connection_string = data['Value']
        engine = sqlalchemy.create_engine(connection_string)
        engine.connect()

        self.engine = engine
        self.execute = engine.execute
        self.text = sqlalchemy.text

