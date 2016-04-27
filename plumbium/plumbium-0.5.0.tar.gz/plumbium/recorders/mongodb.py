"""
plumbium.recorders.mongodb
**************************
"""

try:
    from pymongo import MongoClient
except:
    pass


class MongoDB(object):
    """Records results to a MongoDB database

    :param uri: MongoDB server URI e.g. ``mongodb://localhost:27017``
    :type uri: str
    :param database: database name
    :type database: str
    :param collection: collection name
    :type collection: str

    .. note:: Use of this class requires the installation of the `pymongo
        module <https://pypi.python.org/pypi/pymongo>`_.
    .. seealso:: `MongoDB tutorial <https://api.mongodb.org/python/current/tutorial.html>`_
    """

    def __init__(self, uri, database, collection):
        self.uri = uri
        self.database_name = database
        self.collection_name = collection

    def write(self, results):
        client = MongoClient(self.uri)
        db = client[self.database_name]
        collection = db[self.collection_name]
        collection.insert_one(results)
