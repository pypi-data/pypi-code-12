import sqlalchemy, consul, traceback, sys

from stompest.config import StompConfig
from stompest.protocol import StompSpec
from stompest.sync import Stomp


db = {}

class Connection:
    client = None
    env = None
    c = consul.Consul(host='consul.service.onestop')

    def __init__(self, env, username=None, password=None, clientid=None):
        self.env = env

        index, data = self.c.kv.get('global/config/%s/common/ActiveMQ/stomp/host' % self.env)
        stomp_host = data['Value']

        index, data = self.c.kv.get('global/config/%s/common/ActiveMQ/stomp/port' % self.env)
        stomp_port = int(data['Value'])

	stomp_config = StompConfig('tcp://%s:%d' % (stomp_host, stomp_port))
	self.client = Stomp(stomp_config)

    def connect(self):
	self.client.connect()

    def disconnect(self):
	self.client.disconnect()

    def push(self, message, destination):
    	self.client.send(destination, message)

    def pop(self, destination):
	self.client.subscribe(destination, {StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
	frame = self.client.receiveFrame()
	return frame

    def ack(self, frame):
	self.client.ack(frame)

