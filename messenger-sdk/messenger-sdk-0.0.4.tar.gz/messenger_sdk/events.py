from abc import ABCMeta, abstractmethod
from datetime import datetime


class Event:
    __metaclass__ = ABCMeta

    def __init__(self, event):
        self._event = event
        self._created_at = datetime.now()
        self._intent = None

    def get_recipient_id(self):
        return self._event.get('sender', {}).get('id')

    def set_intent(self, intent):
        self._intent = intent

    def get_intent(self):
        return self._intent

    def get_created_at(self):
        return self._created_at

    def is_valid(self):
        return self.get_payload() and self.get_recipient_id() and self.get_intent()

    @abstractmethod
    def get_payload(self):
        raise NotImplementedError()

    def as_dict(self):
        return {
            'userId': self.get_recipient_id(),
            'createdAt': self.get_created_at(),
            'type': self.__class__.__name__,
            'intent': self.get_intent(),
            'payload': self.get_payload()
        }


class PostbackEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def get_payload(self):
        return self._event.get('postback').get('payload')


class MessageEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def get_payload(self):
        return self._event.get('message').get('text')

    def get_attachments(self):
        return self._event.get('message').get('attachments')

    def is_valid(self):
        return super().is_valid() and not self._event.get('message').get('attachments')


class DeliveryEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def get_payload(self):
        pass


class ReadEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def get_payload(self):
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

