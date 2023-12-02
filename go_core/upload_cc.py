from gallery import (add_media, confirm_upload)

from mongo_conn import mongo_configuration
import pymongo
import random
import string

def add_plant(msg_received):
    try:
        plant_name = msg_received['name']
        plant_price = msg_received['price']
        plant_image = msg_received['image']
        currency = str(msg_received['currency']).upper()
    except KeyError:
        return {"Message": "A key is missing for adding plant.", "statusCode": 401}

    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])
    db = client['tamu']
    collection = db['plants']

    if collection.count_documents({'plant_name': plant_name}) == 0:
        x = {'name': plant_name,
             "locator": plant_locator(collection),
             'price': plant_price,
             'image': plant_image,
             'currency': currency,
             'status': 'active'
             }
        collection.insert_one(x)
        client.close()
        return {'Message': 'plant added', "statusCode": 200}

    else:
        client.close()
        return {'Message': 'plant already exists', "statusCode": 401}


def plant_locator(collection):
    s = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
    s = f'{s}{collection.count_documents({})}'
    if collection.count_documents({'locator': s}) == 0:
        return s
    else:
        return plant_locator(collection)
