from pymongo import MongoClient
from iweb.sys import AppConfig

appConfig = AppConfig()

class Model(object):

    def __init__(self):
        self.client = MongoClient(host=appConfig.app.config['db.host'], port=appConfig.app.config['db.port'])
        self.db = self.client[appConfig.app.config['db.name']]