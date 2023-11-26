import boto3
from botocore.config import Config
from media_handling import aws_config
from botocore.exceptions import ClientError, HTTPClientError
from tokenz import picture_code, tokens, registration_token
import random


def upload(msg_received):
    try:
        file_type = msg_received["fileType"]

    except KeyError:
        return {"Message": "A key for adding the profile image is missing", "statusCode": 401}

    allowed_types = ["png", "jpeg", "gif", "jpg"]
    if file_type not in allowed_types:
        return {"Message": "file type not allowed", "statusCode": 401}

    else:

        try:
            key_id = aws_config.read_config()
            s3_bucket = "tamuprofileimages"
            product_loc = f"{picture_code.user_locator()}{random.randint(1, 1000)}"

            file_name = f"{product_loc}.{file_type}"
            my_config = Config(
                region_name="us-east-1",

                retries={
                    "max_attempts": 10,
                    "mode": "standard"
                }
            )

            s3 = boto3.client("s3", aws_access_key_id=key_id["aws_access_key_id"],
                              aws_secret_access_key=key_id["aws_secret_access_key"], config=my_config)

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
                "data": presigned_post,
                "image_url": f"https://profilephoto.tamu.dating/{file_name}"
            }

        except (ClientError, HTTPClientError) as err:

            return {"Error": "Something unexpected happened when creating profile image ", "statusCode": 500}


def check_token(header):
    try:
        normal_token = tokens.get_id(header)
        if not str(normal_token).isdigit():
            reg_token = registration_token.get_data(header)
            if reg_token == 0:
                return 0
            else:
                return 1
        else:
            return 1

    except Exception:
        return 0



