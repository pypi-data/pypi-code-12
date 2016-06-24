import decimal
import json

try:
    from boto3.dynamodb.conditions import Key, Attr
except ImportError as e:
    raise ImportError('Failed to import "boto3" ({})'.format(e))

from .abstract import Abstract

class DynamoDB(Abstract):
    """ Adapter for DynamoDB """

    __primary_key     = 'identifier'; # the main identifier
    __secondary_key   = 'search_key'; # the search key (the content is the same as the PK)
    __value_attribute = 'value';

    def __init__(self, storage, namespace = 'default'):
        self._namespace = namespace
        self._storage   = storage

    def get(self, key):
        response = self._table().get_item(Key = self._get_key(key))

        item = response['Item'] if 'Item' in response else None

        return item[self.__value_attribute] if item else None

    def set(self, key, value, ttl = None):
        item = {
            self.__value_attribute: self._prepare_for_setter(value),
        }

        item.update(self._get_key(key))

        self._table().put_item(Item = item)

    def remove(self, key):
        self._table().delete_item(Key = self._get_key(key))

    def find(self, begins_with=None, eq=None):
        criteria = {}

        if eq:
            criteria['KeyConditionExpression'] = Key(self.__primary_key).eq(eq)
        elif begins_with:
            criteria['FilterExpression'] = Key(self.__secondary_key).begins_with(begins_with)

        if not criteria:
            raise ValueError('Need to define the criteria.')

        response = self._table().scan(**criteria)

        if 'Items' not in response:
            return {}

        return {
            item[self.__primary_key]: item[self.__value_attribute]
            for item in response['Items']
        }

    def prepare(self, io_read = 5, io_write = 4):
        throughput = {
            'ReadCapacityUnits':  io_read,
            'WriteCapacityUnits': io_write,
        }

        self._storage.create_table(
            TableName = self._table_name(),
            KeySchema = [
                {
                    'AttributeName': self.__primary_key,
                    'KeyType':       'HASH',
                },
                {
                    'AttributeName': self.__secondary_key,
                    'KeyType':       'RANGE',
                },
            ],
            AttributeDefinitions = [
                {
                    'AttributeName': self.__primary_key,
                    'AttributeType': 'S',
                },
                {
                    'AttributeName': self.__secondary_key,
                    'AttributeType': 'S',
                },
            ],
            ProvisionedThroughput = throughput
        )

    def _get_key(self, key):
        return {
            self.__primary_key:   key,
            self.__secondary_key: key,
        }

    def _table_name(self):
        return self._namespace

    def _table(self):
        return self._storage.Table(self._table_name())

    def _prepare_for_setter(self, data):
        return self._decode(json.dumps(data))

    def _decode(self, data):
        return json.loads(data, parse_float = decimal.Decimal)
