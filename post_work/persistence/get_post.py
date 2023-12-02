from tokenz import tokens
from mongo_conn import mongo_configuration
import pymongo
from user.persistence import get_user_info
import json
from bson import json_util
from media_handling import aws_config


def get(header):
    user_id = tokens.get_id(header)
    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])

    user_data = get_user_info.get(user_id=user_id, client= client)
    db_name = user_data['db_name']

    db = client[db_name]
    collection = db["post_media"]
    key_id = aws_config.read_config()
    gallery_link = f"{key_id['gallery_link']}"
    stories = []

    res = collection.find({"status": "active"}, {"_id": 0})
    for r in res:
        x: dict = json.loads(json_util.dumps(r))
        x.update({'url': f"{gallery_link}/{x['key']}"})
        x.pop('key')
        stories.append(x)

    client.close()
    return {'Message': 'Stories fetched', 'statusCode': 200, 'stories': stories}
