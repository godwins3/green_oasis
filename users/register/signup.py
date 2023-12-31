from sql_conn import mysql_conn
import bcrypt
from users.persistence import get_user_info
from checkers.generate_display_name import generate
from checkers.length_of_words import name_length
import json
from checkers import checkEmail, checkPhone
from sql_conn import mysql_conn
from mongo_conn import mongo_configuration
import pymongo
from tokenz import generate_locator, generate_dbname, tokens
from checkers.disallowed_characters import disallowed, not_allowed, phone_char


def user_register(msg_received):
    try:
        fname = msg_received['fullname']
        key = msg_received['key']
        terms = msg_received['TnC']
        form = msg_received['form']

        try:
            password = bcrypt.hashpw(msg_received["password"].encode("utf-8"), bcrypt.gensalt())
        except Exception as e:
            # Handle the exception appropriately
            # print(f"Error hashing password: {e}")
            return {"Message": f"Error hashing password: {e}"}

        password = bcrypt.hashpw(msg_received["password"].encode("utf-8"), bcrypt.gensalt())
        if form == 'phoneNumber':
            phone_number = phone_char(key)
            checkp = json.loads(checkPhone.check_phoneNo({"phoneNumber": phone_number}))
            if len(phone_number) < 9:
                return {"Message": "Invalid phone number", "statusCode": 401}

            if checkp["phone"] == '1':
                return {"Message": "phone number already in use.", "statusCode": 401}
        
        elif form == 'email':
            checke = checkEmail(msg_received)
            if checke['email'] == 1:
                return
            else:
                return         
        else:
            return {"Message": "Invalid form type", "statusCode": 401}
        

    except KeyError as k:
        return {"Message": "A key is missing for registrations", "Error": str(k), "statusCode": 401}
    # except Exception as e:
    #     return {"Error": str(e), "statusCode": 401}

    conn = mysql_conn.create()
    cursor = conn.cursor()

    db_key = mongo_configuration.read_config()
    client = pymongo.MongoClient(db_key["link"])

    try:
        # Create an account for the users
        locator = str(generate_locator.generate())
        db_name = generate_dbname.generate()
        cursor.execute("""
        INSERT INTO `users` (`user_id`,  `key`, `password`, `locator`,`location`, `date`) VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP);""",
                        (key, password, locator, 'KE'))

        conn.commit()
        if form == 'phoneNumber':
            form = "phone_number"
        # print(form, key)
        cursor.execute(f"SELECT * FROM `users` WHERE {form} = %s ;", (key,))
        row = cursor.fetchall()
        tkn = ''
        creditScore = 1

        # Create the database
        for record in row:
            users_id = int(record[0])

            cursor.execute("""
                        INSERT INTO `users_database` (`database_id`, `database_name`, `user_id`, `locator`, `date`)
                            VALUES (NULL, %s , %s , %s , CURRENT_TIMESTAMP);
                        """, (db_name, users_id, locator))

            db = client[db_name]
            collection = db["personal_information"]
            x = {
                'users_id': int(users_id),
                'fname': fname,
                'locator': locator,
                'Tnc': terms
            }
            collection.insert_one(x)

            tkn = str(tokens.generate_token(users_id, locator))

        conn.close()
        cursor.close()
        client.close()
        return {"Message": "Account created", "token": tkn, "statusCode": 200}

    except TypeError:
        client.close()
        conn.close()
        cursor.close()
        return {"TypeError": "Account not created", "statusCode": 500}
    except Exception as e:
        return {"Message": "Account not created", "Error": str(e), "statusCode": 500}