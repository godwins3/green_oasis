import pymongo
from mongodb_connection import mongo_configuration
from user.persistence import get_user_info
from datetime import datetime
from tokenz.tokens import get_id


def add(header, msg_received):
    try:
        room_id = msg_received["room_id"]

    except KeyError:
        return {"Message": "A key for adding user to room is missing", "statusCode": 401}

    user_id = get_id(header)
    if not str(user_id).isdigit():
        return {'Message': 'login in again', "statusCode": 600}

    user_data = get_user_info.get(user_id=user_id)
    locator = user_data["user_locator"]

    if user_data["user_id"] == 0:
        return 0

    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])
    db = client["tamu"]
    collection = db['message_rooms']

    if collection.count_documents({"locator": locator, "room": room_id}) == 1:
        return 0

    x = {
        "user_id": user_id,
        "locator": locator,
        "room": room_id,
        "createdOn": str(datetime.now())
    }

    if collection.count_documents({'locator': locator, "user_id": user_id}) == 0:
        collection.insert_one(x)
        client.close()
        return 1

    elif collection.count_documents({'locator': locator, "user_id": user_id}) != 0:
        collection.update_one({'locator': locator, "user_id": user_id}, {"$set": x})
        client.close()
        return 1

