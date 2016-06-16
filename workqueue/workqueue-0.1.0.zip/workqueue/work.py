import json
import pika
from inspect import isfunction, isbuiltin

"""
This module provides the necessary tools for executing asynchronous tasks in Master/Slave fashion. It exposes three
 classes:
 - Config: Configuration object passed to both the master (TaskPublisher) and the slaves (Worker) that will establish
 a dialogue.
 - TaskPublisher: Master class. It sends tasks to the workers.
 - Worker: Slave class. It registers the tasks it can perform and then executes it every time receives a message telling
 it to do so.
"""


class TaskPublisher:
    """
    Master class. It sends tasks to the workers.
    """

    def __init__(self, config):
        """
        TaskPublisher constructor.
        :param config: Configuration parameters for this TaskPublisher. For effective communication, it should contain the
        exact same information passed to the respective Worker(s).
        :return: New TaskPublisher instance.
        """
        assert isinstance(config, Config), 'config must be instance of Config class.'
        self._config = config

    def publish_task(self, task_name, data):
        """
        Publishes a new task to a worker.
        :param task_name: Name of the task to be executed.
        :param data: Information needed to complete the task
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._config.host))
        channel = connection.channel()

        # We don't want our queue to expire, hence the durable set to True.
        channel.queue_declare(queue=self._config.queue_name, durable=True)

        message = {'task': task_name, 'data': data}

        channel.basic_publish(exchange=self._config._exchange,
                              routing_key=self._config.queue_name,
                              body=json.dumps(message),
                              # make message persistent
                              properties=pika.BasicProperties(delivery_mode=2, )
                              )

        connection.close()


class Worker:
    """
    Slave class. It registers the tasks it can perform and then executes it every time receives a message telling
     it to do so.
    """

    def __init__(self, config):
        """
        Worker constructor.
        :param config: Configuration parameters for this Worker. For effective communication, it should contain the
        exact same information passed to the respective TaskPublisher.
        :return: New Worker instance.
        """
        assert isinstance(config, Config), 'config must be instance of Config class.'
        self._config = config
        self._function_registry = {}

    def register(self, tag, f):
        """
        Register a new task with its respective handler. This handler must be a function that
        takes a dict as input and returns nothing.
        :param tag: Task name.
        :param f: Handler for the task.
        :return:
        """
        assert isinstance(tag, str), 'tag must be a string'
        assert isfunction(f) or isbuiltin(f), 'f must be a function that takes a dict and returns nothing.'

        self._function_registry[tag] = f

    def run(self):
        """
        Starts the execution of the worker.
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._config.host))
        channel = connection.channel()

        channel.queue_declare(queue=self._config.queue_name,
                              durable=True)  # We don't want our queue to expire.
        handlers = self._function_registry

        def _callback(ch, method, properties, body):
            message = json.loads(body.decode('utf-8'))

            assert 'task' in message and 'data' in message, """Invalid message. It must be of the form:
             {
                "task": <name of the task to be executed>,
                "data": <input data for the task>
             }
            """

            tag = message['task']  # Used to look up the proper task handler.
            data = message['data']  # Data (as a dict) used by the handler.

            # Tell the handler to do its stuff.
            assert tag in handlers, 'Not found %s task in the registry.' % tag

            f = handlers[tag]
            f(data)

            ch.basic_ack(delivery_tag=method.delivery_tag)  # Let the sender know we're done.

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(_callback, queue=self._config.queue_name)

        channel.start_consuming()


class Config:
    """
    Abstraction of the configuration parameters need both by the Worker and TaskPublisher classes.
    """

    def __init__(self, host='localhost', queue_name='task_queue'):
        """
        Config constructor.
        :param host: hostname where the Worker will be listening or where the TaskPublisher will be publishing. (Default: localhost)
        :param queue_name: Name of the queue from the Worker will pull its work or, in case of the TaskPublisher, where
        it will submit tasks. (Default: task_queue)
        :return: New Config instance.
        """
        assert isinstance(host, str), 'host must be a valid string.'
        assert isinstance(queue_name, str), 'queue_name must be a valid string'

        self.host = host
        self.queue_name = queue_name
        self._exchange = ''  # You shouldn't change this
