import pymongo
import json
from bson import json_util
from tokenz import tokens
from mongodb_connection import mongo_configuration
from user.persistence import get_user_info
from bson.objectid import ObjectId
from messages.msg_util import remove_object_id


def get_messages(msg_received, header):
    try:
        locator = msg_received["locator"]
        last_id = 0
        try:
            last_id = msg_received["last_id"]
        except KeyError:
            pass

    except Exception:
        return {"Message": "A key for getting messages is missing", "statusCode": 401}

    user_id = tokens.get_id(header)

    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    else:
        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])

        user_data = get_user_info.get(user_id=user_id)
        db_name = f"messages_{user_data['db_name']}"
        user_collection = client[db_name][locator]
        messages = []

        # Contact collection
        contact_data = get_user_info.get(user_locator=locator)
        if contact_data["user_id"] == 0:
            return {"Message": "User does not exist", "statusCode": 401}

        sort_user = [user_data["user_locator"], locator]
        sort_user_data = [user_data, contact_data]

        if user_collection.count_documents({}) != 0:
            res = ""
            if last_id != 0:
                res = pagination(last_id, user_collection)

            else:
                res = user_collection.aggregate([{"$sort": {"_id": -1}}, {"$limit": 150}, {'$match': {"deleted": 0}}])

            for r in res:
                x: dict = json.loads(json_util.dumps(r))

                if x["sender"] == sort_user[0]:
                    # Set the json file
                    display_name = sort_user_data[0]["display_name"]
                    profile_image = sort_user_data[0]['personalInformation']['profile_image']
                    x.update({"display_name": display_name, 'profile_image': profile_image})
                    sent = sorter(x)
                    messages.append(sent)
                else:
                    display_name = sort_user_data[1]["display_name"]
                    profile_image = sort_user_data[1]['personalInformation']['profile_image']
                    x.update({"display_name": display_name, 'profile_image': profile_image})
                    sent = sorter(x)
                    messages.append(sent)

        # Mark messages are read
        # Receiver's database
        receiver_db_name = f"messages_{contact_data['db_name']}"
        receiver_collection = client[receiver_db_name][user_data["user_locator"]]

        # Mark messages
        receiver_collection.update_many({"receiver": user_data["user_locator"]}, {"$set": {"read": 1}})
        user_collection.update_many({"sender": contact_data["user_locator"]}, {"$set": {"read": 1}})

        last_id = get_last_id(messages)
        client.close()
        return {"Message": "User messages retrieved", "messages": remove_object_id.remove(messages),
                "last_id": last_id, "statusCode": 200}


def sorter(data):
    sent_message = {
        "objectID": data["_id"],
        "message_id": data["message_id"],
        "text": data["message"],
        "createdAt": data["timestamp"],
        "sender": data["sender"],
        "receiver": data["receiver"],
        "user": {
            "locator": data["sender"],
            "name": data["display_name"],
            "avatar": data["profile_image"],
        },
        "image": 0,
        "video": 0,
        "sent": data["sent"],
        "received": data["read"],
        "pending": 0
    }

    return sent_message


def get_last_id(data):
    last_record = 0
    if len(data) != 0:
        last_record = len(data) - 1
    try:
        return data[last_record]['objectID']['$oid']

    except Exception:
        return last_record



def pagination(last_id, collection):
    res = collection.find({"_id": {"$lt": ObjectId(last_id)}, "deleted": 0}).sort("_id", -1).limit(200)
    
    return res
