import logging

from tornado import gen

from messenger_sdk.events import *


class Processor:
    __metaclass__ = ABCMeta

    @gen.coroutine
    def handle(self, event: Event):
        if not isinstance(event, Event):
            raise TypeError(
                'Invalid event class. Expected {}, {} given'.format(Event.__name__, type(event).__name__))
        response = yield self.process_event(event)
        return response

    @gen.coroutine
    def process_event(self, event: Event):
        response = yield self.handle_event(event)
        return response

    @gen.coroutine
    def handle_event(self, event: Event):
        intent = event.intent()
        if not intent:
            raise ValueError('Missing event intent')
        function_to_call = self._get_function_to_call(intent)
        if function_to_call:
            logging.debug('Function: %s', function_to_call.__name__)
            response = yield function_to_call(event)
            return response

    @abstractmethod
    def _get_function_to_call(self, intent):
        raise NotImplementedError()
