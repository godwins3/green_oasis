from mongodb_connection import mongo_configuration
import pymongo


def register(email, user_id):
    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])
    db_name = "tamu"
    collection = client[db_name]["msg_test"]

    if collection.count_documents({"email": email}) == 1:
        client.close()
        return {"Message": "Email already registered.", "statusCode": 401}

    else:
        x = {
            "email": email,
            "user_id": user_id
        }
        collection.insert_one(x)
        client.close()
        return {"Message": "Email registered.", "statusCode": 200}

