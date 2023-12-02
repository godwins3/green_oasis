from mongodb_connection import mongo_configuration
import pymongo
from user.persistence import get_user_info
import json
from bson import json_util
from media_handling import aws_config


def get(msg_received):
    try:
        media_key = msg_received['key']
        user_locator = str(media_key).split('/')[0]

    except KeyError:
        return {'Message': 'A key for confirming upload is missing', 'statusCode': 401}

    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])

    user_data = get_user_info.get(user_locator=user_locator, client=client)
    db_name = user_data['db_name']

    db = client[db_name]
    collection = db["gallery"]
    query = {'key': media_key, 'status': 'active'}

    key_id = aws_config.read_config()
    gallery_link = key_id['gallery_link']

    if collection.count_documents(query) == 1:

        res = collection.find(query, {'user_id': 0, '_id': 0})
        for r in res:
            x: dict = json.loads(json_util.dumps(r))
            x.update({"image_url": f'{gallery_link}/{x["key"]}', 'statusCode': 200})

            client.close()
            return x

    else:
        client.close()
        return {'Message': 'Media file does not exists.', 'statusCode': 401}
