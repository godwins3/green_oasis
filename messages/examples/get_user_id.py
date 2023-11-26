from mongodb_connection import mongo_configuration
import pymongo
import json
from bson import json_util


def get(email):
    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])
    db_name = "tamu"
    collection = client[db_name]["msg_test"]

    if collection.count_documents({"email": email}) == 1:
        res = collection.find({"email": email})
        for r in res:
            x: dict = json.loads(json_util.dumps(r))
            user_id = x['user_id']
            client.close()
            return {"Message": "Email already registered.", "statusCode": 200, "user_id": user_id}

    else:
        client.close()
        return {"Message": "Email not registered.", "statusCode": 401, "user_id": None}
