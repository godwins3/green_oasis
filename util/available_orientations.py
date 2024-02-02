from mongo_conn import mongo_configuration
import pymongo
from datetime import datetime
import json
from bson import json_util


def getter():
    mongo_key = mongo_configuration.read_config()
    client = pymongo.MongoClient(mongo_key["link"])
    db = client["tamu"]
    collection = db["orientations"]
    orientations = []

    res = collection.find({}, {"_id": 0})

    for r in res:
        x: dict = json.loads(json_util.dumps(r))
        orientations.append(x)

    genders = [
        {
            "id": 1,
            "label": "Man",
            "value": "male",
        },
        {
            "id": 2,
            "label": "Woman",
            "value": "female",
        },
        {
            "id": 3,
            "label": "Choose Another",
            "value": "others",
            "options": orientations,
        },
    ]

    client.close()
    return {"genders": genders, "statusCode": 200}


def setter(msg_received):
    try:
        label = str(msg_received['label'])
        value = str(msg_received['value'])

    except KeyError:
        return {"Message": "A key is missing for setting up the gender.", "statusCode": 401}

    mongo_key = mongo_configuration.read_config()
    client = pymongo.MongoClient(mongo_key["link"])
    db = client["tamu"]
    collection = db["orientations"]

    if collection.count_documents({"label": label, "value": value}) == 0:
        item_id = collection.count_documents({})
        collection.insert_one({"id": item_id, "label": label, "value": value, "createdOn": str(datetime.now())})

        client.close()
        return {"Message": "The orientation has been added successfully.", "statusCode": 200}
    else:
        client.close()
        return {"Message": "The orientation already exists.", "statusCode": 401}
