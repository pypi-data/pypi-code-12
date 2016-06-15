import asyncio
import json
from os import environ
from sys import stderr
import logging

import boto3


class QueueProcessor:
    """
    Base class which should be subclassed to create your own queue.

    Create a subclass of `QueueProcessor`, and instantiate it to run

    Example usage::

        from eurystheus import Q

        class ExampleQueue(Q):

            queue_name = 'queue-name'

            @Q.task('test_task')
            def test_task(self, *args):
                print ('running ' + ','.join(args))

        queue = ExampleQueue()
    """
    queue_name = None
    _tasks = dict()
    log = logging.getLogger('eurystheus')

    def _get_task(self, name):
        return self._tasks.get(name)

    def process(self, message):
        """Process a message and invoke the task requested using the specified parameters.

        :param message: Message in the format ``{'task': <task_name>, 'parameters': [<param_1>, <param_2>, ...]}``
        :type message: dict
        """
        task_name = message.get('task')
        task = self._get_task(task_name)
        if task is not None:
            try:
                task(self, *message.get('parameters', []))
            except Exception:
                self.log.exception('{{Queue {0}}} Error running task {0}'.format(self.queue_name, task_name))

    @asyncio.coroutine
    def poll(self):
        """
        Poll the SQS queue for messages. For each, process the task requested.
        """
        self.log.debug('{{Queue {0}}} Checking for messages'.format(self.queue_name))
        for message in self.queue.receive_messages():
            self.log.debug('{{Queue {0}}} Processing message: {1}'.format(self.queue_name, message.body))
            message_body = json.loads(message.body)
            self.process(message_body)
            self.log.debug('{{Queue {0}}} Completed processing message: {1}'.format(self.queue_name, message.body))
            message.delete()
        yield from asyncio.sleep(1)

    @asyncio.coroutine
    def loop_executer(self, loop):
        while loop.is_running():
            yield from asyncio.wait([self.poll()])

    def __init__(self, run=True):
        """ Constructor - connects to SQS and begins main event loop

        :param run: (optional) Disable starting the main loop if set to False.
        :type run: bool
        """
        if self.queue_name is None:
            self.queue_name = environ.get('QUEUE_NAME', None)
            if self.queue_name is None:
                print('QUEUE_NAME environment variable is not set.', file=stderr)
                exit(1)

        self.log.debug('{{Queue {0}}} Started polling queue.'.format(self.queue_name))
        # Get the service resource
        sqs = boto3.resource('sqs')
        # Get the queue. This returns an SQS.Queue instance
        self.queue = sqs.get_queue_by_name(QueueName=self.queue_name)
        self.loop = asyncio.get_event_loop()
        try:
            self.loop.create_task(self.loop_executer(self.loop))
            if run:
                self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.close()
            self.log.debug('{{Queue {0}}} Stopped polling queue.'.format(self.queue_name))

    @classmethod
    def task(cls, name):
        """Decorator to designate the available tasks in your worker.

        :param name: The name of the task, which can be invoked by messages
        :type name: str

        """
        def decorator(func):
            cls._tasks[name] = func
            return func
        return decorator
