import os
import json
import logging
from collections import defaultdict

log = logging.getLogger(__name__)


class JsonDataStore(object):
    def __init__(self, location):
        self.location = location
        self.data = defaultdict(dict)
        self.data.update(self.load())

    def load(self):
        if not os.path.exists(self.location):
            return {}

        with open(self.location, 'rb') as fle:
            return json.load(fle)

    def save(self):
        with open(self.location, 'wb') as fle:
            return json.dump(self.data, fle)

    def set(self, prefix, key, value):
        self.data[prefix][key] = value

    def get(self, prefix, key):
        return self.data[prefix].get(key, None)

    def get_all(self):
        """
        Get all the data. We currently send all data to all clients.

        NOTE: Removes internal private data first.

        :return: dict
        """
        data = dict(self.data)
        del data['__private']
        return data
