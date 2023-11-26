from mongodb_connection import mongo_connection, mongo_configuration
from tokenz import tokens
from subscription import check_subscription
from user.persistence import get_user_info

def login(msg_received):
    try:
        google_id = str(msg_received['google_id'])
        email = str(msg_received['email'])
        login ="google"
        user_id = " "
        locator = ""
        client = mongo_connection.create()
        key = mongo_configuration.read_config()
        db = client['tamu']
        collection = db["google"]

        if login =='google':
            # Query for the user
            user = collection.find_one({"google_id": google_id, "email": email})

            tkn = str(tokens.generate_token(user_id, locator))
            user_data = get_user_info.get(user_id=user_id)
            check_sub = check_subscription.check(header=tkn)
            registration = user_data['personalInformation']['registration']
            # Close the MongoDB connection
            client.close()
        else:
            return {"Message": "Please check login type", "statusCode": 200}

        # Check if user exists and details match
        if user:
            return {"Message": "Sign in successful", "token": tkn, "registration": registration,
                    "subscription": int(check_sub),
                    "statusCode": 200}
        else:
            return {"Message": "User details do not match", "statusCode": 401}

    except Exception as e:
        return {"Message": "Error occurred", "error": str(e), "statusCode": 500}

