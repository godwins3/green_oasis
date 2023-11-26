import pymongo
from tokenz import tokens
from mongodb_connection import mongo_configuration
from user.persistence import get_user_info
from datetime import datetime


def delete(msg_received, header):
    try:
        receiver_locator = str(msg_received["receiver_locator"])
    except KeyError:
        return {"Message": "A key for deleting message is missing", "statusCode": 401}

    user_id = tokens.get_id(header)

    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    else:
        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])

        receiver_data = get_user_info.get(user_locator=receiver_locator, client=client)
        if receiver_data['user_id'] == 0:
            client.close()
            return {'Message': 'User not found', 'statusCode': 404}

        else:
            try:

                # Sender's database
                sender_data = get_user_info.get(user_id=user_id, client=client)
                db_name = f"messages_{sender_data['db_name']}"
                sender_collection = client[db_name][receiver_locator]

                sender_collection.update_many({},
                                              {"$set": {"deleted": 1, "deletedOn": str(datetime.now())}})

                client.close()
                return {"Message": "Messages deleted", "statusCode": 200}

            except Exception:
                return {"Message": "Messages not deleted", "statusCode": 500}
