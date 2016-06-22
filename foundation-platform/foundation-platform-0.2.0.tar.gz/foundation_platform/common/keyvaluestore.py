#!/usr/bin/python
import redis


class KeyValueStore(object):
    """The Key-value-store stores data, called a value, inside a key.

    The value can be retrieved, updated or deleted only by using specific key it was stored in.
    There is no direct way to search for a key by value.
    In a sense, it is like a very large hash/dictionary, but it is persistent, i.e.
    when your application ends, the data doesn't go away
    """
    def __init__(self, keyID=None, fields=None):
        """Initialize

            - Redis
            - variables
        """
        if fields is None:
            fields = {}

        self.keyID = keyID
        self.fields = fields
        self.crud = redis.Redis(host='localhost', port=6379, db="0")

    def create(self, keyID, fields=None):
        """Create a key/value pair entry is redis

        keyID: If specified, use this as the redis ID, otherwise generate a random ID.
        fields: A map of field name to constructor used to read values from redis.
        """
        if fields is None:
            fields = {}
        if self.keyID != "" and self.fields != "":
            self.crud.hmset(keyID, fields)
        else:
            raise AttributeError

    def update(self, keyID, fields=None):
        """Update key/value pair entry is redis

        keyID: If specified, use this as the redis ID, otherwise generate a random ID.
        fields: A map of field name to constructor used to read values from redis.
        """
        if fields is None:
            fields = {}

        if self.keyID != "" and self.crud.hgetall(keyID) is not {}:
            self.crud.hmset(keyID, fields)
        else:
            raise AttributeError

    def read(self, keyID):
        """Read one the fields of a give key ID

        keyID: If specified, use this as the redis ID, otherwise generate a random ID.
        """
        if keyID != "":
            redirect = self.crud.hgetall(keyID)
        else:
            raise AttributeError

        return redirect

    def readall(self, keyIDPattern=""):
        """Read all the fields of a give key ID

        keyID: If specified, use this as the redis ID, otherwise generate a random ID.
        """
        if keyIDPattern != "":
            elements = []
            for keys in self.crud.keys(pattern=keyIDPattern):
                elements.append(keys)
        else:
            raise AttributeError

        return elements

    def delete(self, keyID):
        """Delete the entry of a given keyID

        keyID of the resource to be deleted.
        """
        if keyID != "":
            self.crud.delete(keyID)
        else:
            raise AttributeError
