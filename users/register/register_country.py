from mongo_conn import mongo_configuration
import pymongo
from datetime import datetime
from util.location.core import get_location


def register(country_name: str):

    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])

    db = client["tamu"]
    country_collection = db["countries"]

    if country_collection.count_documents({"country": country_name}) == 0:
        country_data = get_location()
        country_data = country_data['country_name']
        x = {
            "country": country_name.upper(),
            "full_country_name": country_data.name,
            "official_name": country_data.official_name,
            "createdOn": str(datetime.now()).split('.')[0]
        }
        country_collection.insert_one(x)

    client.close()
