import requests
from messages.msg_util import get_user_room
from flask import current_app as app


def check(requested_by, locator):
    try:
        socketio = app.config['socket']
        room = get_user_room.get(locator)
        socketio.emit('ping', {'requested_by': requested_by, "locator": locator, "statusCode": 200}, room=room)


        return {"Message": "Ping sent", "statusCode": 200}

    except Exception:
        return {"Message": "User is offline", "online": 0, "statusCode": 200}

