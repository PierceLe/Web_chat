from flask import Blueprint, request
from services import user_service
from middlewares.auth import jwt_required

user = Blueprint('user', __name__, template_folder='templates')

@user.route("/api/users/me", methods=["GET"])
@jwt_required()
def get_infor():
    user = user_service.get_by_id(request.user_id)
    return {"status_code": 200, "data": {
        "id": user.user_id, 
        "fullname": user.fullname, 
        "avatar": user.avatar, 
        "username": user.username,
        "role": user.role,
    }}, 200

@user.route("/api/users/<username>", methods = ["GET"])
@jwt_required()
def get_user_by_username(username):
    user_id = request.user_id
    friend = user_service.get_user(username)
    if friend is None:
        return {"status_code": 400, "error": "user does not exist!"}, 400
    
    user = user_service.get_relation_by_username(user_id, friend.user_id)
    if user is None:
        return {"status_code": 200, "data": [{ "username": friend.username, "fullname": friend.fullname, "avatar": friend.avatar, "user_id": friend.user_id, "status": -1, "role": friend.role}]}  

    return {"status_code": 200, "data": [{ "username": user[0], "fullname": user[1], "avatar": user[2], "user_id": friend.user_id, "status": int(user[3]), "role": user[4] }]}  

@user.route('/api/users/friend')
@jwt_required()
def get_friend():
    action = request.args.get("action")
    user_id = request.user_id
    friend_list = []
    if action == "all":
        friend_list = user_service.get_relationships(user_id, 1)
    elif action == "sending":
        friend_list = user_service.get_relationships(user_id, 0)
    else:
        friend_list = user_service.get_receiveds(user_id)

    return {"status_code": 200, "data": friend_list}, 200

@user.route("/api/users/friend", methods = ["POST"])
@jwt_required()
def add_friend():
    action = request.json.get("action")
    user_id = request.user_id
    friend_username = request.json.get("friendUsername")
    friend_id = user_service.get_user(friend_username).user_id
    if action == "request_friend":
        user_service.insert_relationship(user_id, friend_id, 0)  
        return {"status_code": 200}, 200
    
    if action == "request_accept":
        user_service.update_relation_by_id(user_id, friend_id, 1)
        return {"status_code": 200}, 200

    return {"status_code": 400, "error": "action not supported"}, 400

@user.route('/api/users/unfriend', methods = ["POST"])
@jwt_required()
def unfriend():
    user_id = request.user_id
    friend_username = request.json.get("friendUsername")
    friend_id = user_service.get_user(friend_username).user_id
    user_service.delete_realtion_by_id(user_id, friend_id)
    return {"status_code": 200}, 200