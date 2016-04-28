''' This module allows you to interact with Pulse queues.'''
import json

from mozillapulse.config import PulseConfiguration
from mozillapulse.consumers import GenericConsumer

class PulseReplayConsumer(GenericConsumer):
    def __init__(self, exchanges, **kwargs):
        super(PulseReplayConsumer, self).__init__(
            PulseConfiguration(**kwargs), exchanges, **kwargs)


def _read_config_file(filepath):
    with open(filepath) as data_file:
        return json.load(data_file)


def create_consumer(user, password, config_file_path, handle_message, *args, **kwargs):
    '''Create a pulse consumer. Call listen() to start listening.'''
    queue_config = _read_config_file(filepath=config_file_path)
    return PulseReplayConsumer(
        # A list with the exchanges of each element under 'sources'
        exchanges=map(lambda x: queue_config['sources'][x]['exchange'], queue_config['sources'].keys()),
        callback=handle_message,
        **{
            'applabel': queue_config['applabel'],
            'durable': queue_config['durable'], # If the queue exists and is durable it should match
            'password': password,
            'topic': map(lambda x: queue_config['sources'][x]['topic'], queue_config['sources'].keys()),
            'user': user
        }
    )
    return consumer
