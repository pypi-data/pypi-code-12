from abc import abstractmethod


class BaseTemplate:
    @abstractmethod
    def __dict__(self):
        raise NotImplementedError()


class PlainTextMessage(BaseTemplate):
    def __init__(self, recipient_id, text):
        self.recipient_id = recipient_id
        self.text = text

    def __dict__(self):
        return {
            'recipient': {
                'id': self.recipient_id
            },
            'message': {
                'text': self.text
            }
        }


class ButtonMessage(BaseTemplate):
    def __init__(self, recipient_id, text, buttons):
        self.recipient_id = recipient_id
        self.text = text
        self.buttons = buttons

    def __dict__(self):
        return {
            'recipient': {
                'id': self.recipient_id
            },
            'message': {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'button',
                        'text': self.text,
                        'buttons': [button.__dict__() for button in self.buttons]
                    }
                }
            }
        }


class Button:
    def __init__(self, title, type='postback', url=None, payload=None):
        self._title = title
        self._url = None
        self._payload = None

        if type in ['postback', 'web_url']:
            self._type = type
        else:
            raise ValueError("Type must be postback or web_url.")

        if type == 'web_url':
            if url is not None:
                self._url = url
            else:
                raise ValueError("Url is required with web_url type.")

        if type == 'postback':
            if payload is not None:
                self._payload = payload
            else:
                raise ValueError("Payload is required with postback type.")

    @property
    def title(self):
        return self._title

    @property
    def type(self):
        return self._type

    @property
    def url(self):
        return self._url

    @property
    def payload(self):
        return self._payload

    def __dict__(self):
        item = {
            'type': self.type,
            'title': self.title
        }
        if self.url:
            item['url'] = self.url,
        if self.payload:
            item['payload'] = self.payload

        return item


class GenericMessage(BaseTemplate):
    def __init__(self, recipient_id, elements):
        self.recipient_id = recipient_id
        if len(elements) > 10:
            raise ValueError("Max number of elements is 10.")
        self.elements = elements

    def __dict__(self):
        return {
            'recipient': {
                'id': self.recipient_id
            },
            'message': {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'generic',
                        'elements': [e.__dict__() for e in self.elements]
                    }
                }
            }
        }


class Element:
    def __init__(self, title, item_url=None, image_url=None, subtitle=None, buttons=None):
        self._title = title
        self._item_url = None
        self._image_url = None
        self._subtitle = None
        self._buttons = None

        if subtitle:
            self._subtitle = subtitle
        if item_url:
            self._item_url = item_url
        if image_url:
            self._image_url = image_url
        if buttons:
            if len(buttons) > 3:
                raise ValueError("Max number of buttons is 3.")
            self._buttons = buttons

    def __dict__(self):
        item = {
            'title': self.title,
            'subtitle': self.subtitle,
            'image_url': self.image_url,
            'item_url': self.item_url
        }
        if self.buttons:
            item['buttons'] = [b.__dict__() for b in self.buttons]

        return item

    @property
    def title(self):
        return self._title

    @property
    def item_url(self):
        return self._item_url

    @property
    def image_url(self):
        return self._image_url

    @property
    def subtitle(self):
        return self._subtitle

    @property
    def buttons(self):
        return self._buttons
