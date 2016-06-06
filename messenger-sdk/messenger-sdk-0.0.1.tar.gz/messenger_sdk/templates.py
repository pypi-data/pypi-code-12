from abc import abstractmethod


class BaseTemplate:
    @abstractmethod
    def get_template(self):
        raise NotImplementedError()


class PlainTextMessage(BaseTemplate):
    def __init__(self, recipient_id, text):
        self.recipient_id = recipient_id
        self.text = text

    def get_template(self):
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

    def get_template(self):
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
                        'buttons': [button.as_dict() for button in self.buttons]
                    }
                }
            }
        }


class Button:
    title = None
    type = None
    url = None
    payload = None

    def __init__(self, title, type='postback', url=None, payload=None):
        self.title = title
        if type in ['postback', 'web_url']:
            self.type = type
        else:
            raise ValueError("type must be postback or web_url")
        if type == 'web_url':
            if url is not None:
                self.url = url
            else:
                raise ValueError("url is required with web_url type")
        if type == 'postback':
            if payload is not None:
                self.payload = payload
            else:
                raise ValueError("payload is required with postback type")

    def as_dict(self):
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
            raise ValueError("max number of elements is 10")
        self.elements = elements

    def get_template(self):
        return {
            'recipient': {
                'id': self.recipient_id
            },
            'message': {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'generic',
                        'elements': [e.as_dict() for e in self.elements]
                    }
                }
            }
        }


class Element:
    title = None
    item_url = None
    image_url = None
    subtitle = None
    buttons = None

    def __init__(self, title, item_url=None, image_url=None, subtitle=None, buttons=None):
        self.title = title
        if subtitle:
            self.subtitle = subtitle
        if item_url:
            self.item_url = item_url
        if image_url:
            self.image_url = image_url
        if buttons:
            if len(buttons) > 3:
                raise ValueError("max number of buttons is 3")
            self.buttons = buttons

    def as_dict(self):
        item = {
            'title': self.title,
            'subtitle': self.subtitle,
            'image_url': self.image_url,
            'item_url': self.item_url
        }
        if self.buttons:
            item['buttons'] = [b.as_dict() for b in self.buttons]

        return item
