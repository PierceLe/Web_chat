from flask import Blueprint, request
from services import block_service
from middlewares.auth import jwt_required, admin_required

block = Blueprint('block', __name__, template_folder='templates')

@block.route("/api/blocks/me", methods=["GET"])
@jwt_required()
def get_blocks_me():
    blocks = block_service.get_by_user_id(request.user_id)
    return {"status_code": 200, "data": blocks}, 200

@block.route("/api/blocks", methods=["GET"])
@jwt_required()
def get_blocks():
    action = request.args.get("action")
    q = request.args.get("q")

    users = []
    if action == "article-blocked":
        users = block_service.get_all("article-blocked", q)
    elif action == "active":
        users = block_service.get_all("active", q)
    else:
        users = block_service.get_all("blocked", q)
        
    return {"status_code": 200, "data": users}, 200

@block.route("/api/blocks", methods=["POST"])
@jwt_required()
def create_block():
    type_block = request.json.get("typeBlock")
    user_block = request.json.get("userBlock")
    block_service.create(type_block, user_block)
    return {"status_code": 201, "data": None}, 201

@block.route("/api/blocks", methods = ["DELETE"])
@jwt_required(False)
def delete_block_by_id():
    type_block = request.args.get("type_block")
    user_block = request.args.get("user_block")
    block_service.delete_by_type_and_user_id(type_block, user_block)
    return {"status_code": 200, "data": None}, 200