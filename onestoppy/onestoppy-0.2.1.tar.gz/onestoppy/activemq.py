import sqlalchemy, consul
from stompy.simple import Client

db = {}

class Connection:
    stomp = None
    env = None
    c = consul.Consul(host='consul.service.onestop')

    def __init__(self, env):
        self.env = env

        index, data = self.c.kv.get('global/config/%s/common/ActiveMQ/stomp/host' % self.env)
        stomp_host = data['Value']

        index, data = self.c.kv.get('global/config/%s/common/ActiveMQ/stomp/port' % self.env)
        stomp_port = int(data['Value'])

	self.stomp = Client(host=stomp_host, port=stomp_port)
	self.stomp.connect()

        #engine = sqlalchemy.create_engine(connection_string)
        #engine.connect()

        #self.engine = engine
        #self.execute = engine.execute
        #self.text = sqlalchemy.text

