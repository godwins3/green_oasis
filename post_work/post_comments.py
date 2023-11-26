from tokenz import tokens
from mongo_conn import mongo_configuration
import pymongo
from users.individual.persistence import get_user_info


def record(msg_received, header):
    try:
        locator: str = msg_received["locator"]
        comment: str = msg_received["comment"]

    except KeyError:
        return {'Message': 'A key for recording story views is missing', 'statusCode': 401}

    user_id = tokens.get_id(header)
    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    user_data = get_user_info.get(user_id=user_id)
    viewer_data = get_user_info.get(user_locator=locator)
    if viewer_data['db_name'] != 0:
        
        db_name = user_data['db_name']
        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])
        db = client[db_name]
        collection = db["post_media"]
        query = {"locator": locator, "status": "active"}

        if collection.count_documents(query) == 0:
            collection.update_one(query, {'$push': {'comment': comment}})
            client.close()
            return {'Message': 'Comment has been recorded.', 'statusCode': 200}

        else:
            client.close()
            return {'Message': 'Comment had been recorded.', 'statusCode': 401}

    else:
        return {'Message': 'User does not exists.', 'statusCode': 401}


