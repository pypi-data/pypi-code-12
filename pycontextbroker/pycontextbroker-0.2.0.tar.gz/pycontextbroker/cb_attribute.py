import json
import requests

from .cb_entity import ContextBrokerEntity


class ContextBrokerAttribute(object):
    def __init__(self, cb_address):
        self.cb_entity_endpoint = cb_address + '/v1/contextEntities'
        self.entity = ContextBrokerEntity(cb_address)

    def get_value(self, entity_type, entity_id, attribute_name):
        if self.entity.get(entity_type, entity_id).get('contextElement') is None or \
           self.entity.get(entity_type, entity_id).get('contextElement').get('attributes') is None:
            return None

        response_attributes = self.entity.get(entity_type, entity_id).get('contextElement').get('attributes')
        attributes = dict([(a.get('name'), a.get('value')) for a in response_attributes])

        return attributes.get(attribute_name)

    def create(self, entity_type, entity_id, attribute_name, attribute_value):
        # Check if entity already exists
        if self.get_value(entity_type, entity_id, attribute_name) is not None:
            return None

        endpoint = '{}/type/{}/id/{}'.format(self.cb_entity_endpoint, entity_type, entity_id)
        data = {
            "attributes": [
                {
                    "name": attribute_name,
                    "type": "integer",
                    "value": attribute_value
                }
            ]
        }
        return requests.post(
            endpoint,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        ).json()

    def update_value(self, entity_type, entity_id, attribute_name, attribute_value):
        # create attribute if it was never created
        if self.get_value(entity_type, entity_id, attribute_name) is None:
            return self.create(entity_type, entity_id, attribute_name, attribute_value)

        data = {"value": attribute_value}
        endpoint = '{}/type/{}/id/{}/attributes/{}'.format(
            self.cb_entity_endpoint,
            entity_type,
            entity_id,
            attribute_name
        )
        return requests.put(endpoint,
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json'}).json()

    def delete(self, entity_type, entity_id, attribute_name):
        endpoint = '{}/type/{}/id/{}/attributes/{}'.format(
            self.cb_entity_endpoint,
            entity_type,
            entity_id,
            attribute_name)
        return requests.delete(endpoint, headers={'Content-Type': 'application/json'}).json()
