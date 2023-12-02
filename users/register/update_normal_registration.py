from checkers import checkEmail, checkPhone
from sql_conn import mysql_conn
from mongo_conn import mongo_configuration
import pymongo
from tokenz import tokens
import bcrypt
from checkers.disallowed_characters import disallowed, not_allowed, phone_char
from checkers.validEmail import valid_email
from checkers import check_if_verified, age_calculator
from checkers.generate_display_name import generate
from checkers.length_of_words import name_length, about_length
from datetime import datetime, timedelta
from tokenz import registration_token
from go_pool import add_user
from referral import add_referred, check_referral_code
import json
from bson import json_util
from user.register import register_country
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def register(msg_received, header):
    reg_token = registration_token.get_data_verification(header)
    if reg_token == 0:
        return {"Message": "Invalid token provided for verification", "statusCode": 401}

    try:

        display_name = generate(name_length(str(msg_received["displayName"]))).strip()
        about = about_length(str(msg_received["about"]))
        form = reg_token['form']  # str(msg_received['form']).lower()
        key = reg_token['key']  # str(msg_received['key']).strip()
        email = str(0)
        phone_number = str(0)
        location = msg_received['location']  # [lon,lat,town:'']
        country = disallowed(str(msg_received['country'])).upper()  # Will be generated from location data

        gender = not_allowed(str(msg_received['gender']).strip()).lower()
        birthday = int(msg_received['birthday'])  # timestamp format in milliseconds
        age = age_calculator.calculate(birthday)
        over_18 = int(msg_received['over18'])  # 0 1
        interested_in = not_allowed(str(msg_received['interestedIn'])).strip().lower()  #
        interest = msg_received['interest']  # list

        profile_image = 'https://profilephoto.tamu.dating'
        # app.logger.info('Checkpoint 1')
        try:
            profile_image = f'https://profilephoto.tamu.dating/{str(msg_received["profile_image"]).strip()}'

        except KeyError:
            pass

        if form == 'email':
            email = str(key).lower().strip()
            if valid_email(email) == 0:
                return {"Message": "Invalid Email", "statusCode": 401}

        elif form == 'phoneNumber':
            phone_number = phone_char(key)
            if len(phone_number) < 9:
                return {"Message": "Invalid phone number", "statusCode": 401}
        else:
            return {"Message": "Invalid form type", "statusCode": 401}

        referral_code = 0
        try:
            referral_code = str(msg_received["referral_code"]).replace(" ", "")
            referral_code = check_referral_code.check({"referral_code": referral_code})["referral_code"]
        except Exception:
            pass
        # app.logger.info('Checkpoint 2')
    except KeyError as e:
        return {"Message": "A key is missing for registrations", "statusCode": 401, "error": str(e)}

    checkm = json.loads(checkEmail.check_email({'email': email}))
    checkp = json.loads(checkPhone.check_phoneNo({"phoneNumber": phone_number}))

    if age < 18:
        return {"Message": "You should be 18 years old or above to join Tamu.", "statusCode": 401}


    if check_if_verified.check(key, form) == 0:
        return {"Message": f"The {form} is not verified.", "statusCode": 401}
        
    else:

        conn = mysql_conn.create()
        cursor = conn.cursor()

        mongo_key = mongo_configuration.read_config()
        client = pymongo.MongoClient(mongo_key["link"])

        try:
            # Update Created account for the user

            if form == 'phoneNumber':
                form = 'phone_number'

            cursor.execute(f"""
            UPDATE `users` SET `display_name` = %s, `what_i_do` = %s,
                `location` = %s, `date` = CURRENT_TIMESTAMP
                WHERE  {form} = %s ;
            """, (display_name, '0', country, key))

            conn.commit()
            cursor.execute(f"SELECT * FROM `users` WHERE `{form}`= %s ;", (key,))
            row = cursor.fetchall()
            tkn = ''

            # Create the database
            for record in row:
                user_id = int(record[0])
                locator = record[6]

                cursor.execute("SELECT * FROM `users_database` WHERE `user_id` = %s ;", (user_id,))
                row = cursor.fetchall()
                db_name = ''
                old_country = ''
                old_gender = ''

                for r in row:
                    db_name = r[1]

                db = client[db_name]
                collection = db["personal_information"]

                res = collection.find()
                for r in res:
                    x: dict = json.loads(json_util.dumps(r))
                    old_country = x['country']
                    old_gender = x['gender']

                x = {
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
                    'referred_by': referral_code,
                    'registration': 1
                }
                collection.update_one({'user_id': user_id}, {"$set": x})

                # Add user to referred table
                if referral_code != 0:
                    add_referred.add({'locator': locator, 'referral_code': referral_code})

                client.close()

                # Add user to pool
                pool_data = {
                    'user_id': user_id,
                    'locator': locator,
                    'gender': gender,
                    'interested_in': interested_in,
                    'country': country,
                    'mood': '',
                    'old_country': old_country,
                    'old_gender': old_gender
                }
                # add_user.add(pool_data)
                add_user.remove_update(pool_data)
                register_country.register(country)

                tkn = str(tokens.generate_token(user_id, locator))
            # app.logger.info('Checkpoint 5')
            conn.close()
            cursor.close()
            return json.dumps({"Message": "Account created", "token": tkn, "statusCode": 200})

        except TypeError:
            client.close()
            conn.close()
            cursor.close()
            return json.dumps({"TypeError": "Account not created", "statusCode": 500})
