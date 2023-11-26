import pymongo
from mongo_connection import mongo_configuration


def create():
    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])

    return client
