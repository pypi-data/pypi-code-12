import requests
import json

from pyramid.events import subscriber

from unicore.webhooks.models import DBSession, Webhook


class WebhookOperation(object):
    def __init__(self, webhook, request):
        self.webhook = webhook
        self.request = request


class WebhookCreated(WebhookOperation):
    pass


class WebhookUpdated(WebhookOperation):
    pass


class WebhookDeleted(WebhookOperation):
    pass


class WebhookEvent(object):
    def __init__(self, owner, event_type, payload):
        self.owner = owner
        self.event_type = event_type
        self.payload = payload


@subscriber(WebhookEvent)
def fire_event(event):
    webhooks = DBSession.query(Webhook). \
        filter(Webhook.owner == event.owner,
               Webhook.event_type == event.event_type)

    for webhook in webhooks:
        requests.post(webhook.url, data=json.dumps({
            'event_type': event.event_type,
            'payload': event.payload,
        }))
