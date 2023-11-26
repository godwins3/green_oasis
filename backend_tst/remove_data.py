from sql_conn import mysql_conn
from mongodb_connection import mongo_configuration
import pymongo
from user.persistence import get_user_info


def remove(string: str):
    _string = string.strip().replace(" ", "")

    if "@" in _string:
        form = 'email'
    else:
        form = 'phone_number'

    conn = mysql_conn.create()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM users where {form} = %s;", (_string,))
    row = cursor.fetchall()

    for r in row:
        user_id = r[0]

        cursor.execute(f"SELECT * FROM users_database WHERE user_id = %s;", (user_id,))
        db_row = cursor.fetchall()

        for db in db_row:
            db_name = db[1]

            key = mongo_configuration.read_config()
            client = pymongo.MongoClient(key["link"])

            user_data = get_user_info.get(user_id=user_id)

            try:
                cursor.execute(f"DELETE FROM users WHERE user_id = %s;", (user_id,))
                cursor.execute(f"DELETE FROM users_database WHERE user_id = %s;", (user_id,))
                cursor.execute(f"DELETE FROM reg_verification WHERE {form} = %s;", (_string,))
                client.drop_database(db_name)
                conn.commit()

                try:
                    country = user_data['personalInformation']['country']
                    user_gender = user_data['personalInformation']['gender']

                    # Tamu pool
                    db = client[country]
                    collection = db[user_gender]
                    collection.delete_one({"user_id": user_id})
                except Exception:
                    pass

                client.close()
                cursor.close()
                conn.close()

            except Exception:
                client.close()
                cursor.close()
                conn.close()
                return {"Message": "Something went wrong.", "statusCode": 500}

    return {"Message": f"User {string} has been deleted.", "statusCode": 200}
