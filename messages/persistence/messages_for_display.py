import pymongo
import json
from bson import json_util
from tokenz import tokens
from mongodb_connection import mongo_configuration
from user.persistence import get_user_info


def get_messages(header):
    user_id = tokens.get_id(header)

    if not str(user_id).isalnum():
        return {'Message': 'login in again.', "statusCode": 600}

    else:
        key = mongo_configuration.read_config()
        client = pymongo.MongoClient(key["link"])

        user_data = get_user_info.get(user_id=user_id, client=client)
        db_name = f"messages_{user_data['db_name']}"
        sender_collection = client[db_name]["contacts"]
        unread_messages = []

        if sender_collection.count_documents({}) != 0:
            res = sender_collection.find({})
            for r in res:
                x: dict = json.loads(json_util.dumps(r))

                contact_collection = client[db_name][x["locator"]]
                contact_data = get_user_info.get(user_locator=x["locator"], client=client)

                total_unread = contact_collection.count_documents({"read": 0, "receiver": user_data["user_locator"]})
                if contact_collection.count_documents({"deleted": 0}) == 0:
                    continue

                for_display = contact_collection.aggregate([{"$sort": {"_id": -1}}, {"$limit": 1},
                                                            {'$match': {
                                                                # "receiver": user_data["user_locator"],
                                                                "deleted": 0
                                                            }}
                                                            ])
                for f in for_display:
                    aggregated: dict = json.loads(json_util.dumps(f))
                    aggregated.pop("_id")
                    # print(aggregated)
                    profile_photo = "https://profilephoto.tamu.dating"
                    try:
                        profile_photo = contact_data['personalInformation']["profile_image"]
                    except Exception:
                        pass

                    data = {
                        "message_id": aggregated["message_id"],
                        "text": aggregated["message"],
                        "createdAt": aggregated["timestamp"],
                        "sender": aggregated["sender"],
                        "receiver": aggregated["receiver"],
                        "user": {
                            "locator": x["locator"],
                            "name": contact_data["display_name"],
                            "avatar": profile_photo,
                        },
                        "image": 0,
                        "video": 0,
                        "sent": aggregated["sent"],
                        "received": aggregated["read"],
                        "pending": 0,
                        "total": total_unread,
                    }
                    unread_messages.append(data)

        client.close()
        unread_messages.sort(key=lambda val: val["createdAt"], reverse=True)
        return {"Message": "Messages for display retrieved", "messages": unread_messages, "statusCode": 200}