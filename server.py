import logging
import os

import flask
from flask import request
from flask import Response
from flask_cors import CORS, cross_origin

from go_config import *

from checkers import check_token
from users.persistence import get_user_info
from backend_tst import remove_data, clear_all_data

from users.login.normal_login import login
from users.register import (normal_registration, cont_normal_registration, update_normal_registration, signup)



from flask_socketio import SocketIO, emit, join_room


# from safeproxyfix import  SaferProxyFix

app = flask.Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")  # ,async_mode="gevent_uwsgi"
app.config["socket"] = socketio
CORS(app)
cwd = os.getcwd()

app.config["DOWNLOAD"] = os.path.join(cwd, "download#stats")
try:
    os.mkdir(app.config["DOWNLOAD"])
except:
    pass

@app.route("/", methods=["GET", "POST"])
@cross_origin(origin="*")
def go():
    header = request.headers.get("Authorization")

    headers_list = request.headers.getlist("X-Forwarded-For")
    e = headers_list  # headers_list[0] if headers_list else request.remote_addr
    ip = str(e).split(",")[0]

    disallowed_characters = "[<>]/*-;+/:()%$#@!/?_\""

    for character in disallowed_characters:
        ip = ip.replace(character, "")

    msg_received = flask.request.get_json()
    try:
        msg_subject = msg_received["subject"]
    except (KeyError, TypeError):
        return {"Message": "No subject provided to Go", "statusCode": 404}
    
    # User Auth
    if msg_subject == 'register':
        return signup.user_register(msg_received) 
    
    elif msg_subject == "register_normal":
        return update_normal_registration.register(msg_received, header)

    elif msg_subject == "update_registration":
        return cont_normal_registration.update(msg_received, header)
    
    
    elif msg_subject == 'login':
        return login(msg_received)
    
    else:
        return {"Message": "Wrong subject provided to Go", "statusCode": 500}


@socketio.on("green-oases")
def socket_op(message):
    header = request.headers.get("Authorization")
    _id = request.sid

    subject = 0
    msg_received = 0
    try:
        msg_received = message
        subject = msg_received["subject"]
    except Exception:
        pass

    if subject == "chat":
        return
    
    elif subject == "join":
        return
    else:
        return {'Message': 'Wrong subject provided to Go', 'statusCode': 500}
    

@socketio.on("connect")
def connect_user():
    header = request.headers.get("Authorization")
    _id = request.sid
    join_room(_id)
    # add_user_room.add(header, {"room_id": _id})
    emit("my_response", {"Message": "User added to group"})
    return {"Message": "User added to group", "statusCode": 200}

@app.route("/clear-user-data", methods=["GET", "POST"])
@cross_origin(origin="*")
def clear():
    msg_received = flask.request.get_json()
    return remove_data.remove(msg_received["key"])

@app.route("/clear-db", methods=["GET", "POST"])
@cross_origin(origin="*")
def clear_db():
    msg_received = flask.request.get_json()
    
    msg_subject = msg_received["subject"]

    if msg_subject == 'theReset':
        return clear_all_data.remove(msg_received["key"])
    else:
        return {"Message": "Wrong subject provided to Tamu", "statusCode": 401}


def logga(info):
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.critical(info)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5004, debug=True,
                 allow_unsafe_werkzeug=True)  # threaded=True, allow_unsafe_werkzeug=True
    