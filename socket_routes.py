'''
socket_routes
file containing all the routes related to socket.io
'''

from flask_socketio import join_room, emit, leave_room
from flask import request
from middlewares.auth import jwt_ws_required

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models.models import Room
from services import room_service, user_service

room = Room()
map_user_id_and_sid = {}

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
@jwt_ws_required()
def connect(_):
    user_id = request.user_id
    map_user_id_and_sid[request.sid] = user_id
    user_service.update_status_by_user_id(user_id, 1)

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    user_id = map_user_id_and_sid[request.sid]
    if user_id is None:
        return
    user_service.update_status_by_user_id(user_id, 0)

# message event handler
# sent when the user sends a message
@socketio.on('message')
def handle_message(data):
    room_id = data["room_id"]
    message_id = room_service.create_message(int(data["room_id"]), data["user_id"], "text", data["content"])
    user = user_service.get_by_id(data["user_id"])
    emit('message', {
        "author": data["user_id"],
        "avatar": user.avatar,
        "content": data["content"],
        "kind": "text",
        "id": message_id,
        "room_id": room_id
    }, broadcast=True, to=room_id)

# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(data):
    room_id = data["room_id"]
    join_room(int(room_id))
    emit("join", {"room_id": room_id}, to=room_id)

# leave room event handler
# sent when the user leaves a room
@socketio.on("leave")
def leave(data):
    room_id = data["room_id"]
    leave_room(room_id)
    emit("leave", {}, to=room_id)
