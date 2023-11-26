from twilio.rest import Client
from sms import sms_config
from twilio.base.exceptions import TwilioRestException


def send(phone_number, code):
    key = sms_config.config()
    account_sid = key['account_sid']
    auth_token = key['auth_token']
    try:
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=f"Welcome to Tamu,\n your verification code is {code}",
            from_='+14799991055',
            to=phone_number
        )

        print(message.sid)
        return {'Message': 'SMS has been sent, use the code in the SMS as verification', "statusCode": 200}

    except TwilioRestException as err:
        print(err)
        return {'Message': 'SMS not sent', "statusCode": 500}
