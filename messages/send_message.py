import pymongo
from tokenz import tokens
from mongodb_connection import mongo_configuration
from user.persistence import get_user_info
from string import ascii_letters, digits
from random import choice, randint
from util import date_formarter
from datetime import datetime, timedelta
from flask import current_app as app
from messages.msg_util import get_user_room, check_blocked
from checkers.check_message import check


def send(header, msg_received):
    try:
        sender = msg_received["sender"]
        receiver = msg_received["receiver"]
        message = msg_received["message"]
        message = check(message)
        message_type = msg_received["messageType"]
        timestamp = msg_received["timestamp"]
        real_time = str(datetime(1970, 1, 1) + timedelta(seconds=int(timestamp / 1000)))
        formatted_date = date_formarter.format_date(real_time)

    except KeyError as e:
        return {"Message": "A key for sending message is missing", "error": str(e), "statusCode": 401}

    user_id = tokens.get_id(header)

    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    else:
        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])

        receiver_data = get_user_info.get(user_locator=receiver, client=client)
        if receiver_data['user_id'] == 0:
            client.close()
            return {'Message': 'User not found', 'statusCode': 404}

        else:
            # try:

            # Sender's database
            sender_data = get_user_info.get(user_id=user_id, client=client)
            db_name = f"messages_{sender_data['db_name']}"
            sender_collection = client[db_name][receiver]

            if sender != sender_data["user_locator"]:
                client.close()
                return {"Message": "Wrong sender details", "statusCode": 401}

            # Add contacts to sender
            add_contact = client[db_name]["contacts"]
            if add_contact.count_documents({"locator": receiver}) == 0:
                add_contact.insert_one(
                    {"contact_id": add_contact.count_documents({}), "locator": receiver,
                     "createdOn": str(datetime.now())})

            # Receiver's database
            receiver_db_name = f"messages_{receiver_data['db_name']}"
            receiver_collection = client[receiver_db_name][sender_data["user_locator"]]

            # Add contacts to receiver
            add_contact_receiver = client[receiver_db_name]["contacts"]
            if add_contact_receiver.count_documents({"locator": sender}) == 0:
                add_contact_receiver.insert_one(
                    {"contact_id": add_contact_receiver.count_documents({}), "locator": sender,
                     "createdOn": str(datetime.now())})

            message_id = generate_message_id(sender_collection, receiver_collection)

            x = {
                "message_id": message_id,
                "sender": sender,
                "receiver": receiver,
                "message": message,
                "messageType": message_type,
                "timestamp": timestamp,
                "read": 0,
                "deleted": 0,
                "sent": 1,
                "formatted_date": formatted_date
            }

            sender_collection.insert_one(x)
            # Check if sender is blocked
            ch_blocked = 0
            try:
                ch_blocked = check_blocked.block({"receiver_locator": sender_data["user_locator"]},
                                                 uid=receiver_data['user_id'])
            except Exception:
                pass

            if ch_blocked["status"] == 0:
                receiver_collection.insert_one(x)

            x.update({"display_name": sender_data["display_name"]})
            x.update({'profile_image': sender_data['personalInformation']['profile_image']})

            if ch_blocked["status"] == 0:
                emit_message(receiver, x)

            client.close()
            return {"Message": "Message sent successfully", "message_id": message_id, "statusCode": 200}

        # except Exception as e:
        #
        #     return {"Message": "An error occurred while sending message","error":str(e), "statusCode": 500}


def emit_message(locator, message):
    sent_message = {
        "message_id": message["message_id"],
        "text": message["message"],
        "createdAt": message["timestamp"],
        "sender": message["sender"],
        "receiver": message["receiver"],
        "user": {
            "locator": message["sender"],
            "name": message["display_name"],
            "avatar": message["profile_image"],
        },
        "image": 0,
        # You can also add a video prop:
        "video": 0,
        # Mark the message as sent, using one tick
        "sent": 1,
        # Mark the message as received, using two tick
        "received": 1,
        # Mark the message as pending with a clock loader
        "pending": 0,
        # Any additional custom parameters are passed through
        "total": 0,
        "statusCode": 200
    }

    socketio = app.config['socket']
    room = get_user_room.get(locator)
    socketio.emit('receiveMessage', sent_message, room=room)


def generate_message_id(sender_collection, receiver_collection):
    minimum = 10
    maximum = 10
    string_format = ascii_letters.upper() + digits
    generated_string = "".join(choice(string_format) for x in range(randint(minimum, maximum)))
    query = {"message_id": generated_string}

    if sender_collection.count_documents(query) == 0 and receiver_collection.count_documents(query) == 0:
        return generated_string
    else:
        return generate_message_id(sender_collection, receiver_collection)
