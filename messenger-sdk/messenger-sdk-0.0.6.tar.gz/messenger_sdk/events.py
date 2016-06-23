from abc import ABCMeta, abstractmethod
from datetime import datetime


class Event:
    __metaclass__ = ABCMeta

    def __init__(self, event):
        self._event = event
        self._created_at = datetime.now()
        self._intent = None
        self._storage = None

    @property
    def recipient_id(self):
        return self._event.get('sender', {}).get('id')

    @property
    def intent(self):
        return self._intent

    @intent.setter
    def intent(self, intent):
        self._intent = intent

    @property
    def created_at(self):
        return self._created_at

    def is_valid(self):
        return self.payload and self.recipient_id and self.intent

    @abstractmethod
    def payload(self):
        raise NotImplementedError()

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, storage: dict):
        self._storage = storage

    def as_dict(self):
        return {
            'userId': self.recipient_id,
            'createdAt': self.created_at,
            'type': self.__class__.__name__,
            'intent': self.intent,
            'payload': self.payload
        }


class PostbackEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    @property
    def payload(self):
        return self._event.get('postback').get('payload')


class MessageEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    @property
    def payload(self):
        return self._event.get('message').get('text')

    @property
    def attachments(self):
        return self._event.get('message').get('attachments')

    def is_valid(self):
        return super().is_valid() and not self._event.get('message').get('attachments')


class DeliveryEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def payload(self):
        pass


class ReadEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def payload(self):
        pass


class EventFactory:
    _events = {
        'message': MessageEvent,
        'postback': PostbackEvent,
        'delivery': DeliveryEvent,
        'read': ReadEvent
    }
    
    def create_event(self, event):
        for key in self._events.keys():
            if event.get(key):
                return self._events.get(key)(event)
        raise TypeError('Unsupported event.')

