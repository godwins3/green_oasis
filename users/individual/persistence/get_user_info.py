from sql_conn import mysql_conn
from mongo_conn import mongo_configuration
import pymongo
import json
from bson import json_util


def get(phone_number=None, users_locator=None, users_id=None, client=None):
    conn = mysql_conn.create()
    cursor = conn.cursor()

    key = mongo_configuration.read_config()
    original_client = 0
    if client is None:
        client = pymongo.MongoClient(key["link"])
        original_client = 1

    auth_type = ''
    value = ''
    if phone_number:
        auth_type = 'phone_number'
        value = email
    elif users_locator:
        auth_type = 'locator'
        value = users_locator
    elif user_id:
        auth_type = 'user_id'
        value = users_id

    user_id = 0
    email = 0
    display_name = 0
    phone_number = 0
    db_name = 0
    personal_information = {}

    try:
        cursor.execute(f"SELECT * FROM users WHERE {auth_type} = %s ;", (value,))
        data = cursor.fetchall()

        if len(data) == 1:
            for d in data:
                user_id = d[0]
                phone_number = str(d[1])
                users_locator = str(d[3])

                cursor.execute("SELECT * FROM users_database WHERE user_id = %s ;", (user_id,))
                users_db = cursor.fetchall()
                for db in users_db:
                    db_name = db[1]

                    db = client[db_name]
                    collection = db["personal_information"]

                    res = collection.find({}, {'users_id': 0, '_id': 0})
                    for r in res:
                        x: dict = json.loads(json_util.dumps(r))
                        personal_information.update(x)
    except Exception as e:
        print(e)
        return {"Message": "users does not exist", "statusCode": 401}

    cursor.close()
    conn.close()
    if original_client == 1:
        client.close()

    return {"user_id": user_id, "display_name": display_name, 'db_name': db_name,
            'personalInformation': personal_information,
            "users_locator": users_locator, "phone_number": phone_number, "email": email}

# print(get(email='raimondo2@email.com'))
