from flask import Blueprint, request
from services import article_service
from middlewares.auth import jwt_required, admin_required
from utils.utils import remove_br_tags

article = Blueprint('article', __name__, template_folder='templates')

@article.route("/api/articles", methods = ["GET"])
@jwt_required(False)
def get_articles():
    articles = article_service.get_all(request.user_id)
    return {"status_code": 200, "data": articles} 

@article.route("/api/articles", methods = ["POST"])
@jwt_required(False)
def create_articles():
    content = remove_br_tags(request.json.get("content"))
    article_service.create(request.user_id, content)
    return {"status_code": 201, "data": None} 

@article.route("/api/articles/<article_id>", methods = ["PUT"])
@jwt_required(False)
def update_article_by_id(article_id):
    article = article_service.get_by_id(article_id)
    if article is None:
        return {"status_code": 404, "error": "article not found"}
    
    if request.role != "student" or request.user_id == article["author"]:
        content = remove_br_tags(request.json.get("content"))
        article_service.update_by_id(article_id, content)
        return {"status_code": 200, "data": None}
    else:
        return {"status_code": 403, "error": "You are not authorized"}
    
@article.route("/api/articles/<article_id>", methods = ["DELETE"])
@jwt_required(False)
def delete_article_by_id(article_id):
    article = article_service.get_by_id(article_id)
    if article is None:
        return {"status_code": 404, "error": "article not found"}
    
    if request.role != "student" or request.user_id == article["author"]:
        article_service.delete_by_id(article_id)
        return {"status_code": 200, "data": None}
    else:
        return {"status_code": 403, "error": "You are not authorized"}