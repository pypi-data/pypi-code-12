# mongodao.py
"""Module contains a data access object to simplify saving data to a MongoDB
database.
"""


import logging

import pymongo

from paraturegmailfeed.exceptions import MongoDbConnectionError


logger = logging.getLogger(__name__)


class MongoDao(object):
    """Data access object for MongoDB"""
    def __init__(self, mongo_uri, db_name):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db_name = db_name
        self.database = self.client[self.db_name]

    def save(self, collection, data):
        """Write single document to MongoDB database"""
        if collection == 'action':
            selector = {
                'ticketNumber': data['ticketNumber'],
                'timestamp': data['timestamp']
            }
        else:
            selector = data # Whole sale match

        try:
            upserted_id = self.database[collection].update_one(selector,
                                                           {'$set': data},
                                                           upsert=True).upserted_id
        except pymongo.errors.ConnectionFailure:
            logger.critical('MongoDB: Connection failure; check that a mongod is running')
            raise MongoDbConnectionError
        else:
            logger.info("MongoDB: Insert/update successful for: " + str(data))
            return upserted_id

    def save_many(self, collection, data):
        """Write many documents to MongoDB database"""
        upserted_ids = []
        for element in data:
            upserted_id = self.save(collection, element)
            upserted_ids.append(upserted_id)

        return upserted_ids
