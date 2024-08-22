import os
from flask import Blueprint, request
from services import room_service, user_service
from middlewares.auth import jwt_required

room = Blueprint('room', __name__, template_folder='templates')

@room.route("/api/rooms", methods = ["GET"])
@jwt_required()
def get_rooms():
    rooms = room_service.get_all(request.user_id)
    return {"status_code": 200, "data": rooms}, 200

@room.route("/api/rooms/history/<room_id>", methods = ["GET"])
@jwt_required()
def get_historys(room_id):
    messages = room_service.get_history(room_id)
    return {"status_code": 200, "data": messages}, 200

@room.route("/api/rooms/<room_id>", methods = ["GET"])
@jwt_required()
def get_room(room_id):
    rooms = room_service.get_by_id(room_id)
    return {"status_code": 200, "data": rooms}, 200

@room.route("/api/rooms", methods = ["POST"])
@jwt_required()
def create_room():
    body = request.json
    room_name = body["roomName"]
    room_id = None
    if(len(body["users"]) == 1):
        room_id = room_service.room_single_exist(request.user_id, body["users"][0])
        if room_id is None:
            body["users"].append(request.user_id)
            room_id = room_service.create(None, "", "")
            room_service.join_users(room_id, body["users"])
        else:
            room_service.update_is_deleted(room_id[0])
    else:
        body["users"].append(request.user_id)
        room_id = room_service.create(request.user_id, room_name, "/static/images/groups.png", "group")
        room_service.join_users(room_id, body["users"])

    return {"status_code": 200, "data": {"room_id": None}} 

@room.route("/api/rooms/leave-room/<room_id>", methods = ["POST"])
@jwt_required(False)
def leave_room(room_id):
    room = room_service.get_by_id(room_id)
    if room is None:
        return {"status_code": 404, "error": "room not found"}, 404

    user_id = request.json["userId"]
    room_service.leave_room(room_id, user_id)
    return {"status_code": 200, "data": None}, 200

@room.route("/api/rooms/join-room/<room_id>", methods = ["POST"])
@jwt_required(False)
def join_room(room_id):
    room = room_service.get_by_id(room_id)
    if room is None:
        return {"status_code": 404, "error": "room not found"}, 404

    users = request.json["users"]
    room_service.join_users(room_id, users)
    return {"status_code": 200, "data": None}, 200

@room.route("/api/rooms/<room_id>", methods = ["DELETE"])
@jwt_required(False)
def delete_comment_by_id(room_id):
    room = room_service.get_by_id(room_id)
    if room is None:
        return {"status_code": 404, "error": "room not found"}, 404
    
    room_service.delete_chat_by_id(room_id, request.user_id)
    return {"status_code": 200, "data": None}, 200 