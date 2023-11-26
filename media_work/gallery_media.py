import boto3
from botocore.config import Config
from media_handling import aws_config
from botocore.exceptions import ClientError, HTTPClientError


def upload(msg_received):
    try:
        file_type = msg_received['file_type']
        media_loc = msg_received['media_loc']
        user_locator = msg_received['user_locator']

    except KeyError:
        return {'Message': 'A key for adding the profile image is missing', 'statusCode': 401}

    allowed_types = ['png', 'jpeg', 'gif', 'jpg']
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
