import json
import requests


class ContextBrokerEntity(object):
    def __init__(self, cb_address):
        self.cb_entity_endpoint = cb_address + '/v1/contextEntities'

    def create(self, entity_type, entity_id, attributes=None):
        data = {
            "id": entity_id,
            "type": entity_type
        }

        if attributes:
            # [{"name": "number", "type": "integer", "value": "0"}]
            data.update({"attributes": attributes})

        return requests.post(
            self.cb_entity_endpoint,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        ).json()

    # Read
    def get(self, entity_type, entity_id):
        endpoint = '{}/type/{}/id/{}'.format(self.cb_entity_endpoint, entity_type, entity_id)
        return requests.get(endpoint).json()

    # Delete
    def delete(self, entity_type, entity_id):
        endpoint = '{}/type/{}/id/{}'.format(self.cb_entity_endpoint, entity_type, entity_id)
        return requests.delete(endpoint).json()
