from datetime import datetime
from datetime import timedelta
from mongo_conn import mongo_configuration
from tokenz import generate_locator, generate_dbname, tokens
from sql_conn import mysql_conn
from checkers.generate_display_name import generate
from checkers.length_of_words import name_length, about_length
from datetime import datetime, timedelta

import random
from datetime import datetime, timedelta
from sql_conn import mysql_conn
from checkers import validEmail
import string
import pymongo
from tamu_pool import add_user
import bcrypt

from sql_conn import mysql_conn
from mongo_conn import mongo_configuration
import pymongo
from tokenz import tokens
import bcrypt
from checkers.disallowed_characters import disallowed, not_allowed
from checkers import age_calculator
from checkers.generate_display_name import generate
from checkers.length_of_words import name_length, about_length
from datetime import datetime, timedelta
from tamu_pool import add_user
from user.register import register_country

def g_signup(msg_received):
    try:
        email = msg_received['email']
        password = msg_received['google_id']

        if validEmail.valid_email(email) == 0:
            return {"Message": "Invalid Email", "statusCode": 401}

        # form = msg_received['form']

    except KeyError as k:
        return {"Message": "A key is missing for Google registration", "statusCode": 401, "Error": str(k)}

    try:
    
        conn = mysql_conn.create()
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM `users` WHERE `email` = %s ;""", (email,))
        check_exist = cursor.fetchall()
        if len(check_exist) != 0:
            cursor.close()
            conn.close()
            return {'Message': 'Email already exists, kindly log in.', 'statusCode': 401}


        google_id = str(msg_received['google_id'])
        email = str(msg_received['email'])
        name = random_string
        
        form = 'email'
        key = email
        
        login ="google"
    
        if login == "google":
            mongo_key = mongo_configuration.read_config()
            client = pymongo.MongoClient(mongo_key["link"])
            db = client['tamu']
            collection = db["google"]


            
            y = {
                'google_id': google_id,
                'email': email,
                'name': name,
                'created': datetime.now()
            }
        conn = mysql_conn.create()
        cursor = conn.cursor()

        db_key = mongo_configuration.read_config()
        client = pymongo.MongoClient(db_key["link"])
        display_name = generate(name_length(str(msg_received["displayName"]))).strip()
        about = about_length(str(msg_received["about"]))
        form = form  # str(msg_received['form']).lower()
        key = key  # str(msg_received['key']).strip()
        email = email
        phone_number = str(0)
        password = password  # Replace with the actual password
        password_encoded = password.encode("utf-8")  # Encode the password as bytes
        salt = bcrypt.gensalt()  # Generate a salt
        password = bcrypt.hashpw(password_encoded, salt)  # Hash the password

        location = msg_received['location']  # [lon,lat,town:'']
        country = disallowed(str(msg_received['country'])).upper()  # Will be generated from location data

        gender = not_allowed(str(msg_received['gender']).strip()).lower()
        birthday = int(msg_received['birthday'])  # timestamp format in milliseconds
        age = age_calculator.calculate(birthday)
        over_18 = int(msg_received['over18'])  # 0 1
        interested_in = not_allowed(str(msg_received['interestedIn'])).strip().lower()  #
        interest = msg_received['interest']  # list

        profile_image = 'https://profilephoto.tamu.dating'
        
        try:
            profile_image = f'https://profilephoto.tamu.dating/{str(msg_received["profile_image"]).strip()}'

        except KeyError:
            pass


        try:
            # Create an account for the user
            locator = str(generate_locator.generate())
            db_name = generate_dbname.generate()
            cursor.execute("""
            INSERT INTO `users` (`user_id`, `display_name`, `what_i_do`, `email`, `phone_number`, `password`, 
            `locator`,`location`, `date`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);""",
                           (display_name, '0', email, phone_number, password, locator, 'KE'))


            conn.commit()
            if form == 'phoneNumber':
                form = "phone_number"
            # print(form, key)
            cursor.execute(f"SELECT * FROM `users` WHERE {form} = %s ;", (key,))
            row = cursor.fetchall()
            

            # Create the database
            for record in row:
                user_id = int(record[0])
                referral_code = ''
                code = random.randint(1000, 9999)
                q = datetime.now().strftime("%Y-%m-%d %H:%M")

                cursor.execute("""
                            INSERT INTO `users_database` (`database_id`, `database_name`, `user_id`, `locator`, `date`)
                             VALUES (NULL, %s , %s , %s , CURRENT_TIMESTAMP);
                            """, (db_name, user_id, locator))
                conn.commit()
                cursor.execute("""
                   INSERT INTO `reg_verification` (`id`, `email`, `phone_number`, `code`, `date`,
                    `counts`, `createdOn`, `state`, `method`) VALUES 
                    (NULL, %s , %s , %s , %s , %s , CURRENT_TIMESTAMP, %s , %s );
                   """, (email, 0, code, str(q), 1, 'verified', 'email'))
                conn.commit()
                
                db = client[db_name]
                collection = db["personal_information"]
                x = {
                    'user_id': int(user_id),
                    'locator': locator,
                    'referral_code': referral_code,
                    'gender': gender,
                    'location': location,  # [{'longitude':1234,'latitude':1234,'address':}]
                    'about': about,
                    'birthday': str(datetime(1970, 1, 1) + timedelta(seconds=birthday / 1000)).split(" ")[0],
                    'birthday_timestamp': birthday,
                    'age': age,
                    'over_18': over_18,
                    'interested_in': interested_in,
                    'interest': interest,
                    'profile_image': profile_image,
                    'country': country,
                    'referred_by': 0,
                    'registration': 0
                }
                collection.insert_one(x)

                # Add user to pool
                pool_data = {
                    'user_id': user_id,
                    'locator': locator,
                    'gender': gender,
                    'interested_in': interested_in,
                    'country': country,
                    'mood': ''
                }
                
                add_user.add(pool_data)
            register_country.register(country)
            
            user_data = get_user_id_locator_by_email(email)
            user_id =str(user_data['user_id'])
            locator = str(user_data['locator'])
            conn.close()
            cursor.close()
            client.close()
            tkn = str(tokens.generate_token(user_id, locator))
            return {"Message": "Account created", "token": tkn, "statusCode": 200}
        
        except TypeError as t:
            client.close()
            conn.close()
            cursor.close()
            tkn = str(tokens.generate_token(user_id, locator))
            # return {"TypeError": "Account not created", "statusCode": 500, "Error": str(t)}
            return {"Message": "Account created", "token": tkn, "statusCode": 200}
        
    except Exception as e:
        return {"Message": "Error creating account", "Error": str(e), "statusCode": 500}
    
def random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))

def get_user_id_locator_by_email(email):
    try:
        conn = mysql_conn.create()
        cursor = conn.cursor()

        # Create a cursor
        with conn.cursor() as cursor:
            # SQL query to retrieve user_id and locator based on email
            sql = "SELECT user_id, locator FROM users WHERE email = %s"
            
            # Execute the query
            cursor.execute(sql, (email,))
            
            # Fetch the result
            result = cursor.fetchone()
            
            return result
        
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        # Close the connection
        if conn:
            conn.close()
