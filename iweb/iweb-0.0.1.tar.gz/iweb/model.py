from pymongo import MongoClient

class Model(object):
    db_host = 'localhost'
    db_port = 27017
    db_name = 'test'

    def __init__(self):
        client = MongoClient(host=self.db_host, port=self.db_port)
        self.db = client[self.db_name]

    def get_db(self):
        return self.db