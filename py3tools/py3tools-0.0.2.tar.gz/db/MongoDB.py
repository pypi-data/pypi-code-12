from pymongo import MongoClient

class MongoDB(object):

    def __init__(self, host_name, port, db_name):
        mongo_client = MongoClient(host=host_name, port=port)
        self.db = mongo_client[db_name]