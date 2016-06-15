import json
from os import environ
from sys import stderr
import logging

import boto3


class QueueClient:
    """
    Class used to submit tasks to the queue for processing.

    Example usage::

        from sthenelus import Q

        Q.submit('task_name', 'parameter1', 'parameter2')
    """
    queue_name = None
    log = logging.getLogger('sthenelus')

    def submit(self, task_name, *parameters):
        """Submit a task for processing.

        :param task_name: Name of the task to submit for processing
        :type message: dict
        :param parameters: Parameters to pass to the task
        """
        payload = {
            'task': task_name,
            'parameters': parameters
        }
        response = self.queue.send_message(MessageBody=json.dumps(payload))
        if response.get('MessageId') is None:
            self.log.exception('{{Queue {0}}} Error submitting task {0}'.format(self.queue_name, task_name))

    def __init__(self):
        """ Constructor - connects to SQS and submits jobs
        """
        if self.queue_name is None:
            self.queue_name = environ.get('QUEUE_NAME', None)
            if self.queue_name is None:
                print('QUEUE_NAME environment variable is not set.', file=stderr)
                exit(1)

        self.log.debug('{{Queue {0}}} Client started.'.format(self.queue_name))
        # Get the service resource
        sqs = boto3.resource('sqs')
        # Get the queue. This returns an SQS.Queue instance
        self.queue = sqs.get_queue_by_name(QueueName=self.queue_name)
        self.log.debug('{{Queue {0}}} Ready to accept tasks.'.format(self.queue_name))

