from flask import Blueprint, request
from services import comment_service
from middlewares.auth import jwt_required, admin_required
from utils.utils import remove_consecutive_empty_lines

comment = Blueprint('comment', __name__, template_folder='templates')

@comment.route("/api/comments", methods = ["GET"])
@jwt_required(False)
def get_comments_by_article_id():
    article_id = request.args.get('articleId')
    user_id = request.user_id
    role = request.role
    comments = comment_service.get_all(article_id, user_id, role)
    return {"status_code": 200, "data": comments} 

@comment.route("/api/comments/<comment_id>", methods = ["GET"])
@jwt_required(False)
def get_comments_by_id(comment_id):
    comment = comment_service.get_by_id(comment_id)
    if comment is None:
        return {"status_code": 400, "error": "comment not found"}, 400
    return {"status_code": 200, "data": comment}, 200

@comment.route("/api/comments/<article_id>", methods = ["POST"])
@jwt_required(False)
def create_comment(article_id):
    content = remove_consecutive_empty_lines(request.json.get("content"))
    comment_service.create(article_id, request.user_id, content)
    return {"status_code": 201, "data": None}, 201

@comment.route("/api/comments/<comment_id>", methods = ["PUT"])
@jwt_required(False)
def update_comment_by_id(comment_id):
    comment = comment_service.get_by_id(comment_id)
    if comment is None:
        return {"status_code": 404, "error": "comment not found"}, 404
    
    if request.role != "student" or request.user_id == comment["author"]["id"]:
        content = remove_consecutive_empty_lines(request.json.get("content"))
        comment_service.update_by_id(comment_id, content)
        return {"status_code": 200, "data": None}, 200
    else:
        return {"status_code": 403, "error": "You are not authorized"}, 403
    
@comment.route("/api/comments/<comment_id>", methods = ["DELETE"])
@jwt_required(False)
def delete_comment_by_id(comment_id):
    comment = comment_service.get_by_id(comment_id)
    if comment is None:
        return {"status_code": 404, "error": "comment not found"}, 404
    
    if request.role != "student" or request.user_id == comment["author"]["id"]:
        comment_service.delete_by_id(comment["id"])
        return {"status_code": 200, "data": None}, 200
    else:
        return {"status_code": 403, "error": "You are not authorized"}, 403