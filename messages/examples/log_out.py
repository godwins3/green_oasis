from mongodb_connection import mongo_configuration
import pymongo
import json
from bson import json_util


def delete(email):
    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])
    db_name = "tamu"
    collection = client[db_name]["msg_test"]

    if collection.count_documents({"email": email}) == 1:
        collection.delete_one({"email": email})
        client.close()
        return {"Message": "Log out successful.", "statusCode": 200}

    else:
        client.close()
        return {"Message": "Email not registered.", "statusCode": 401}
