from tokenz import tokens
from mongo_conn import mongo_configuration
import pymongo
from users.persistence import get_user_info


def delete(msg_received, header):
    try:
        media_id = msg_received['mediaId']

    except KeyError:
        return {'Message': 'A key for deleting media is missing', 'statusCode': 401}

    user_id = tokens.get_id(header)
    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])

    user_data = get_user_info.get(user_id=user_id, client=client)
    db_name = user_data['db_name']

    db = client[db_name]
    collection = db["gallery"]

    if collection.count_documents({'media_id': media_id, "status": "active"}) == 1:
        collection.update_one({'media_id': media_id}, {'$set': {'status': 'deleted'}})
        client.close()
        return {'Message': 'Media file has been deleted.', 'statusCode': 200}

    else:
        client.close()
        return {'Message': 'Media file does not exists.', 'statusCode': 401}
