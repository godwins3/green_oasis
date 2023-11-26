from users.individual.persistence import get_user_info
from tokenz import tokens
from mongo_conn import mongo_configuration
import pymongo
from media_work import story_media
from datetime import datetime, timedelta
from util import date_formarter
import random
import string

import boto3
from botocore.config import Config
from media_work import aws_config
from botocore.exceptions import ClientError, HTTPClientError

def upload(msg_received, header):
    try:
        file_type = msg_received['fileType']
        comment = msg_received['comment']
        created_on_ts = msg_received['createdOn']
        created_on = str(datetime(1970, 1, 1) + timedelta(seconds=int(created_on_ts / 1000)))
        expires_on_ts = 86400000 + created_on_ts

    except KeyError:
        return {'Message': 'A key for adding story is missing', 'statusCode': 401}

    user_id = tokens.get_id(header)

    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    key = mongo_configuration.read_config()
    client = pymongo.MongoClient(key["link"])

    user_data = get_user_info.get(user_id=user_id, client= client)
    db_name = user_data['db_name']
    user_locator = user_data['user_locator']

    db = client[db_name]
    collection = db["story_media"]

    total_media = collection.count_documents({})
    media_loc = int(total_media + 1)

    data = {
        'media_loc': media_loc,
        'comment': comment,
        "user_locator": user_locator,
        'file_type': file_type
    }

    res: dict = story_media.upload(data)
    if res['statusCode'] == 200:
        x = {
            'media_id': media_loc,
            'comment': comment,
            'key': res['data']['fields']['key'],
            'views': [],
            'created_at': created_on,
            'expires_on_ts': expires_on_ts,
            'created_on_ts': created_on_ts,
            'formatted_date': date_formarter.format_date(created_on),
            'status': 'pending',
        }

        collection.insert_one(x)
        res.update({'media_id': int(media_loc)})

    client.close()
    return res


def generate_string():
    return ''.join(random.choice(string.ascii_letters) for _ in range(9)).upper()


def upload_status(msg_received):
    try:
        file_type = msg_received['file_type']
        media_loc = msg_received['media_loc']
        user_locator = msg_received['user_locator']

    except KeyError:
        return {'Message': 'A key for adding the profile image is missing', 'statusCode': 401}

    allowed_types = ['png', 'jpeg', 'mp3', 'jpg', 'mp4']
    if file_type not in allowed_types:
        return {'Message': 'file type not allowed', 'statusCode': 401}

    try:
        key_id = aws_config.read_config()
        s3_bucket = "tamugallery"
        gallery_link = key_id['gallery_link']
        # media_loc = f'{picture_code.user_locator()}{random.randint(1,1000)}'

        file_name = f'{user_locator}/{media_loc}.{file_type}'
        my_config = Config(
            region_name='us-east-1',

            retries={
                'max_attempts': 10,
                'mode': 'standard'
            }
        )

        s3 = boto3.client('s3', aws_access_key_id=key_id['aws_access_key_id'],
                          aws_secret_access_key=key_id['aws_secret_access_key'], config=my_config)

        presigned_post = s3.generate_presigned_post(
            Bucket=s3_bucket,
            Key=file_name,
            Fields={"acl": "public-read", "Content-Type": file_type},
            Conditions=[
                {"acl": "public-read"},
                {"Content-Type": file_type},
                ["content-length-range", 200, 10485760]
            ],
            ExpiresIn=7200
        )

        return {
            'data': presigned_post,
            'image_url': f"{gallery_link}/{file_name}",
            "statusCode": 200
        }

    except (ClientError, HTTPClientError):

        return {"Error": "Something unexpected happened when creating gallery media link ", "statusCode": 500}
