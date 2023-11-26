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

def clear_db():
    try:
        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])

        # List all databases
        db_list = client.list_database_names()

        mysql_status = delete_all_records()

        if mysql_status['statusCode'] == 200:
            # Delete non-system databases
            for db_name in db_list:
                if db_name != "admin" and db_name != "local" and db_name != "config":
                    client.drop_database(db_name)

            # Close the MongoDB client
            client.close()

            return {"Message": "All databases have been deleted.", "statusCode": 200}
        else:
            return {"Message": "Something went wrong with mysql.", "statusCode": 500}
    except Exception as e:
        return {"Message": f"An error occurred: {str(e)}", "statusCode": 500}
def delete_all_records():
    try:
        # Create a database connection
        conn = mysql_conn.create()

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Define the names of the tables to delete records from
        tables_to_delete = ['users', 'users_database', 'reg_verification']

        for table in tables_to_delete:
            # Execute a DELETE query to remove all records from the table
            delete_query = f"DELETE FROM {table};"
            cursor.execute(delete_query)

        # Commit the changes to the database
        conn.commit()

        # Close the cursor and the database connection
        cursor.close()
        conn.close()

        return {"Message": "All records in the specified tables have been deleted.", "statusCode": 200}

    except Exception as e:
        return {"Message": f"An error occurred: {str(e)}", "statusCode": 500}

# Example usage:
# result = delete_all_records()
# print(result)
