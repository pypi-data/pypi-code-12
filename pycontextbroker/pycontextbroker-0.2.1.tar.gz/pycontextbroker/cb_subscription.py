import json
import requests


class ContextBrokerSubscription(object):
    def __init__(self, cb_address):
        self.cb_subscription_endpoint = cb_address + '/v1/subscribeContext'
        self.cb_subscriptions_endpoint_v2 = cb_address + '/v2/subscriptions'
        self.cb_unsubscription_endpoint = cb_address + '/v1/unsubscribeContext'

    def all(self):
        return requests.get(self.cb_subscriptions_endpoint_v2).json()

    def on_change(self, entity_type, entity_id, attribute_name, subscriber_endpoint):
        subscription_data = {
            "entities": [
                {
                    "type": entity_type,
                    "isPattern": "false",
                    "id": entity_id
                }
            ],
            "attributes": [
                attribute_name
            ],
            "reference": subscriber_endpoint,
            "duration": "P1M",
            "notifyConditions": [
                {
                    "type": "ONCHANGE",
                    "condValues": [
                        attribute_name
                    ]
                }
            ],
            "throttling": "PT5S"
        }

        return requests.post(self.cb_subscription_endpoint,
                             data=json.dumps(subscription_data),
                             headers={'Content-Type': 'application/json'}).json()

    def unsubscribe(self, subscription_id):
        data = {
            "subscriptionId": subscription_id
        }
        return requests.post(self.cb_unsubscription_endpoint,
                             data=json.dumps(data),
                             headers={'Content-Type': 'application/json'}).json()
