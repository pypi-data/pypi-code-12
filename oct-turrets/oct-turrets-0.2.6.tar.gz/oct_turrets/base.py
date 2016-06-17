from __future__ import unicode_literals

import six
import zmq
import uuid
from threading import Thread


class BaseTurret(object):
    """The base turret class

    :param hq_address str: the ip address of the HQ runing OCT
    :param hq_pub_port int: the port of the publish socket in the HQ
    :param hq_rc_port int: the port of the result collector in the HQ
    """

    READY = 'ready'
    RUNNING = 'Running'
    ABORTED = 'Aborted'
    INIT = 'Initialized'
    KILLED = 'Killed'

    def __init__(self, config, script_module, unique_id=None):

        self.config = config
        self.cannons = []
        self.script_module = script_module
        self.start_time = None
        self.run_loop = True
        self.start_loop = True
        self.already_responded = False
        self.uuid = unique_id or six.text_type(uuid.uuid4())
        self.commands = {}
        self.status = self.INIT

        self.setup_sockets()

        self.init_commands()

    def init_commands(self):
        """Initialize the commands dictionnary. This dict will be used when master send a command to interpret them
        """
        pass

    def setup_sockets(self):
        """Init and connect all the turrets
        """
        self.context = zmq.Context()

        self.poller = zmq.Poller()
        self.local_result = self.context.socket(zmq.PULL)
        self.local_result.bind("inproc://turret")

        self.master_publisher = self.context.socket(zmq.SUB)
        self.master_publisher.connect("tcp://{}:{}".format(self.config['hq_address'], self.config['hq_publisher']))
        self.master_publisher.setsockopt_string(zmq.SUBSCRIBE, '')
        self.master_publisher.setsockopt_string(zmq.SUBSCRIBE, self.uuid)

        self.result_collector = self.context.socket(zmq.PUSH)
        self.result_collector.connect("tcp://{}:{}".format(self.config['hq_address'], self.config['hq_rc']))

        self.poller.register(self.local_result, zmq.POLLIN)
        self.poller.register(self.master_publisher, zmq.POLLIN)

    def close_sockets(self):
        """Close all the sockets
        """
        self.local_result.close()
        self.master_publisher.close()
        self.result_collector.close()
        self.context.destroy()

    def build_status_message(self):
        data = {
            'turret': self.config['name'],
            'status': self.status,
            'uuid': self.uuid,
            'rampup': self.config['rampup'],
            'script': self.config['script'],
            'cannons': self.config['cannons']
        }
        return data

    def find_command(self, payload):
        """Execute the given command by searching it in the self.commands property.

        :param payload str: the dict containing the message from the master
        :return: True if the command exists, false if the payload does not contain a command or the command is not found
        :rtype: bool
        """
        if 'command' in payload:
            command = self.commands.get(payload['command'])
            return command
        print("The message does not contain a command")
        return None

    def start(self):
        """Start the turret and wait for the master to call the run method
        """
        raise NotImplementedError("Start method must be implemented")

    def send_result(self, result):
        """Send result to the result collector

        :param result dict: the result to send to the master
        :return: None
        """
        raise NotImplementedError("send_result error must be implemented")

    def run(self):
        """Main loop for the turret
        """
        raise NotImplementedError("run method must be implemented")


class BaseCannon(Thread):
    """The base cannon class, inherit from thread

    :param start_time int: the start_time of the test
    :param run_time int: the total run time for the script in second
    :param script_module: the module containing the test
    """

    def __init__(self, start_time, script_module, turret_uuid, context, config):
        super(BaseCannon, self).__init__()
        self.start_time = start_time
        self.script_module = script_module
        self.run_loop = True
        self.config = config

        self.result_socket = context.socket(zmq.PUSH)
        self.result_socket.connect("tcp://{}:{}".format(self.config['hq_address'], self.config['hq_rc']))

    def run(self):
        """The main run method for the cannon
        """
        raise NotImplementedError("run method must be implemented")


class BaseTransaction(object):
    """The base transaction class for writing tests
    """

    def __init__(self, config):
        self.config = config
        self.custom_timers = {}

    def setup(self):
        """This method will be call before the run method, use it to setup all needed datas.
        The setup time will not be included in the scriptrun_time
        """
        pass

    def run(self):
        """This is the main function that will be executed for the tests
        """
        pass

    def tear_down(self):
        """This method will be call once the run method has ended. Since the transaction instance will never be
        destroyed before the end of the test, use this method to clean and reset all variables, etc.
        The tear down time will not be included in the scriptrun_time
        """
        pass
