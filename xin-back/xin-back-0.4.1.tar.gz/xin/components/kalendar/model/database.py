from pymongo import MongoClient
from os import environ

db = MongoClient(
    host=environ.get('MONGODB_HOST', 'mongodb://localhost:27017/calendar')).get_default_database()
