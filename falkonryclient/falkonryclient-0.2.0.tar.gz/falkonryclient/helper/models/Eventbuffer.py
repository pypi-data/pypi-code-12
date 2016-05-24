"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""

import jsonpickle
from falkonryclient.helper.models.Subscription import Subscription

class Eventbuffer:
    """Eventbuffer schema class"""

    def __init__(self, **kwargs):
        self.raw = kwargs.get('eventbuffer') if 'eventbuffer' in kwargs else {}

    def get_id(self):
        return self.raw['id'] if 'id' in self.raw else None

    def set_name(self, name):
        self.raw['name'] = name
        return self

    def get_name(self):
        return self.raw['name'] if 'name' in self.raw else None

    def set_source_id(self, source_id):
        self.raw['sourceId'] = source_id
        return self

    def get_source_id(self):
        return self.raw['sourceId'] if 'sourceId' in self.raw else None

    def get_account(self):
        return self.raw['tenant'] if 'tenant' in self.raw else None

    def get_create_time(self):
        return self.raw['createTime'] if 'createTime' in self.raw else None

    def get_created_by(self):
        return self.raw['createdBy'] if 'createdBy' in self.raw else None

    def get_update_time(self):
        return self.raw['updateTime'] if 'updateTime' in self.raw else None

    def get_updated_by(self):
        return self.raw['updatedBy'] if 'updatedBy' in self.raw else None

    def get_schema(self):
        return self.raw['schemaList'] if 'schemaList' in self.raw else []

    def set_subscriptions(self, subscriptions):
        subscription_list = self.raw['subscriptionList'] if 'subscriptionList' in self.raw else []
        for subscription in subscriptions:
            if isinstance(subscription, Subscription):
                subscription_list.append(subscription)

        self.raw['subscriptionList'] = subscription_list
        return self

    def get_subscriptions(self):
        return self.raw['subscriptionList'] if 'subscriptionList' in self.raw else []

    def to_json(self):
        subscriptions = []
        for subscription in self.get_subscriptions():
            subscriptions.append(jsonpickle.unpickler.decode(subscription.to_json()))

        eventbuffer = self.raw
        eventbuffer['subscriptionList'] = subscriptions
        return jsonpickle.pickler.encode(eventbuffer)
