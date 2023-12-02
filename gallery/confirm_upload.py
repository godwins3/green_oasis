from tokenz import tokens
from mongodb_connection import mongo_configuration
import pymongo
from user.persistence import get_user_info


def confirm(msg_received, header):
    try:
        try:
            media_id = int(msg_received['mediaId'])
            confirmation = int(msg_received['confirmation'])

            if confirmation != 204:
                return {'Message': 'Upload cancelled', 'statusCode': 401}

        except KeyError:
            return {'Message': 'A key for confirming upload is missing', 'statusCode': 401}

        user_id = tokens.get_id(header)
        if not str(user_id).isalnum():
            return {'Message': 'login in again.', "statusCode": 600}

        user_data = get_user_info.get(user_id=user_id)
        db_name = user_data['db_name']

        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])
        db = client[db_name]
        collection = db["gallery"]

        if collection.count_documents({'media_id': media_id}) == 1:
            collection.update_one({'media_id': media_id}, {'$set': {'status': 'active'}})

        client.close()
        return {'Message': 'Upload confirmed', 'statusCode': 200}

    except Exception:
        return {'Message': 'An error occurred', 'statusCode': 500}



