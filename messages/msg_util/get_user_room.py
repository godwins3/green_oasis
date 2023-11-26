import pymongo
from mongodb_connection import mongo_configuration
import json
from bson import json_util


def get(locator):
    try:
        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])
        db_name = f"tamu"
        collection = client[db_name]['message_rooms']

        res = collection.find({'locator': locator})

        for r in res:
            x: dict = json.loads(json_util.dumps(r))
            room = x['room']

            client.close()
            return room

    except Exception:
        return 0
