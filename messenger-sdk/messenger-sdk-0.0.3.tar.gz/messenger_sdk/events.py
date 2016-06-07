from abc import ABCMeta, abstractmethod
from datetime import datetime


class Event:
    __metaclass__ = ABCMeta

    _intent = None
    _channel_id = None

    def __init__(self, event):
        self._event = event

    def get_recipient_id(self):
        return self._event.get('sender', {}).get('id')

    def set_intent(self, intent):
        self._intent = intent

    def get_intent(self):
        return self._intent

    def set_channel_id(self, channel_id):
        self._channel_id = channel_id

    def get_channel_id(self):
        return self._channel_id

    def is_valid(self):
        return self.get_payload() and self.get_recipient_id() and self.get_intent()

    @abstractmethod
    def get_payload(self):
        raise NotImplementedError()

    def as_dict(self):
        return {
            'user_id': self.get_recipient_id(),
            'created_at': datetime.utcnow(),
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


class EventFactory:
    TYPE_DELIVERY = 'delivery'
    TYPE_MESSAGE = 'message'
    TYPE_POSTBACK = 'postback'

    @staticmethod
    def create_event(event):
        if event.get('message'):
            return MessageEvent(event)
        if event.get('postback'):
            return PostbackEvent(event)
        if event.get('delivery'):
            return DeliveryEvent(event)
