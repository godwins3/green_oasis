import pymongo
from tokenz import tokens
from mongodb_connection import mongo_configuration
from user.persistence import get_user_info
from user.persistence import get_user_db


def block(msg_received, header=None, uid=None):
    try:
        receiver_locator = str(msg_received["receiver_locator"])

    except KeyError:
        return {"Message": "A key for blocking user is missing", "statusCode": 401}

    user_id = 0
    if header is not None:
        user_id = tokens.get_id(header)

    if uid is not None:
        user_id = uid

    if not str(user_id).isalnum():
        return {"Message": "login in again.", "statusCode": 600}

    try:
        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])

        receiver_data = get_user_info.get(user_locator=receiver_locator, client=client)
        if receiver_data["user_id"] == 0:
            client.close()
            return {"Message": "User not found", "statusCode": 404}

        db_name = get_user_db.get(user_id)
        db = client[db_name]
        collection = db["blocked_users"]

        if collection.count_documents({"locator": receiver_locator}) == 0:
            client.close()
            return {"Message": "You have not blocked the user", "status": 0, "state": "not blocked", "statusCode": 200}

        else:
            client.close()
            return {"Message": "You have blocked the user", "status": 1, "state": "blocked", "statusCode": 200}

    except Exception:
        return {"Message": "Error getting blocked state", "status": 0, "state": "unknown", "statusCode": 500}
