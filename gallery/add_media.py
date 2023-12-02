from user.persistence import get_user_info
from tokenz import tokens
from mongodb_connection import mongo_configuration
import pymongo
from media_handling import gallery_media
from datetime import datetime, timedelta
from util import date_formarter


def upload(msg_received, header):
    try:
        file_type = msg_received['fileType']
        created_on = str(datetime(1970, 1, 1) + timedelta(seconds=int(msg_received['createdOn']) / 1000))

    except KeyError:
        return {'Message': 'A key for adding media file is missing', 'statusCode': 401}

    user_id = tokens.get_id(header)

    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])

    user_data = get_user_info.get(user_id=user_id, client= client)
    db_name = user_data['db_name']
    user_locator = user_data['user_locator']

    db = client[db_name]
    collection = db["gallery"]

    total_media = collection.count_documents({})
    media_loc = total_media + 1
    if len(str(media_loc)) < 6:
        media_loc = f'{(6 - len(str(media_loc))) * "0"}{media_loc}'
    
    data = {
        'media_loc': media_loc,
        "user_locator": user_locator,
        'file_type': file_type
    }

    res: dict = gallery_media.upload(data)
    if res['statusCode'] == 200:
        x = {
            'media_id': int(media_loc),
            'key': res['data']['fields']['key'],
            'created_at': created_on,
            'formatted_date': date_formarter.format_date(created_on),
            'status': 'pending',
        }

        collection.insert_one(x)
        res.update({'media_id': int(media_loc)})

    client.close()
    return res

