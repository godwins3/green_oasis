import pymongo
from tokenz import tokens
from mongodb_connection import mongo_configuration
from user.persistence import get_user_info
import json
from bson import json_util


def get(msg_received, header):
    try:
        message_id = str(msg_received["message_id"])
        receiver_locator = str(msg_received["receiver_locator"])

    except KeyError:
        return {"Message": "A key for getting single message is missing", "statusCode": 401}

    user_id = tokens.get_id(header)

    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    else:
        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])

        # Sender's database
        sender_data = get_user_info.get(user_id=user_id)
        db_name = f"messages_{sender_data['db_name']}"
        sender_collection = client[db_name][receiver_locator]

        if sender_collection.count_documents({"message_id": message_id}) == 1:
            res = sender_collection.find({"message_id": message_id})
            for r in res:
                x: dict = json.loads(json_util.dumps(r))
                x.update({"statusCode": 200})

                client.close()
                return x

        else:
            client.close()
            return {"Message": "Message does not exist", "statusCode": 401}
