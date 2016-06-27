''' This module allows you to interact with Pulse queues.'''
import ast
import json
import logging

from mock import Mock

from mozillapulse.config import PulseConfiguration
from mozillapulse.consumers import GenericConsumer

LOG = logging.getLogger(__name__)


class PulseReplayConsumer(GenericConsumer):
    def __init__(self, exchanges, **kwargs):
        super(PulseReplayConsumer, self).__init__(
            PulseConfiguration(**kwargs), exchanges, **kwargs)


def _read_json_file(filepath):
    with open(filepath) as data_file:
        return json.load(data_file)


def _read_file(filepath):
    with open(filepath) as data_file:
        return data_file.read()


def create_consumer(user, password, config_file_path, process_message, *args, **kwargs):
    '''Create a pulse consumer. Call listen() to start listening.'''
    queue_config = _read_json_file(filepath=config_file_path)

    exchanges = map(lambda x: queue_config['sources'][x]['exchange'], queue_config['sources'].keys())
    topics = map(lambda x: queue_config['sources'][x]['topic'], queue_config['sources'].keys())

    for i in range(0, len(exchanges)):
        LOG.info('Listening to (%s, %s)' % (exchanges[i], topics[i]))

    pulse_args = {
        # If the queue exists and is durable it should match
        'durable': queue_config['durable'] in ('true', 'True'),
        'password': password,
        'topic': topics,
        'user': user
    }

    if queue_config.get('applabel') is not None:
        pulse_args['applabel'] = queue_config['applabel']

    return PulseReplayConsumer(
        # A list with the exchanges of each element under 'sources'
        exchanges=exchanges,
        callback=process_message,
        **pulse_args
    )
    return consumer


def replay_messages(filepath, process_message, *args, **kwargs):
    ''' Take pulse messages from a file and process each with process_message.

    :param filepath: File containing dumped pulse messages
    :type filepath: str
    :param process_message: Function to process each pulse message with
    :type process_message: function
    :param *args: Arguments to be passed to process_message()
    :type *args: tuple
    :param **kwargs: Keyword argument to be passed to process_message()
    :type **kwargs: dict

    :returns: Nothing
    :rtype: None

    '''
    message = Mock()

    file_contents = _read_file(filepath)
    for line in file_contents.splitlines():
        # Using ast.literal_eval to turn pulse message strings into dicts
        process_message(ast.literal_eval(line), message, *args, **kwargs)
