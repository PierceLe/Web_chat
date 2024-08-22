from sqlalchemy.orm import Session
from models.models import *
from services.db import engine

def create(user_id, content):
    with Session(engine) as session:
        article = Article(
            content=content,
            author=user_id
        )
        session.add(article)
        session.commit()
        return article.article_id
    
def new_feed(user_id, role):
    with Session(engine) as session:
        relationships = session.query(Relationships.friend_id).filter(Relationships.user_id == user_id).all()
        friends = [relationship[0] for relationship in relationships]
        friends.append(user_id)
        result = session.query(Article, User)\
            .join(User, Article.author == User.user_id)\
            .filter(Article.author.in_(friends))\
            .order_by(Article.time_created.desc())\
            .all()
        
        articles_json = []

        for [article, user] in result:
            is_modify = False

            if role != "student" or article.author == user_id:
                is_modify = True

            count_comment = session.query(Comment.comment_id)\
                .filter(Comment.article_id == article.article_id)\
                .with_entities(func.count())\
                .scalar()
            
            articles_json.append({
                "id": article.article_id,
                "author": {
                    "fullname": user.fullname,
                    "role": user.role,
                    "avatar": user.avatar,
                },
                "count_comment": count_comment,
                "is_modify": is_modify,
                "content": article.content,
                "time_created": article.time_created,
                "time_updated": article.time_updated
            })
        
        return articles_json

def get_all(user_id):
    with Session(engine) as session:
        articles = session.query(Article).filter(Article.author == user_id).all()
        articles_json = []

        for article in articles:
            articles_json.append({
                "id": article.article_id,
                "author": article.author,
                "content": article.content,
                "time_created": article.time_created,
                "time_updated": article.time_updated
            })

        return articles_json
    
def get_by_id(article_id):
    with Session(engine) as session:
        article = session.query(Article).filter(Article.article_id == article_id).first()
        if article is None:
            return None
        
        return {
            "id": article.article_id,
            "author": article.author,
            "content": article.content,
            "time_created": article.time_created,
            "time_updated": article.time_updated
        }

def update_by_id(article_id, content):
    with Session(engine) as session:
        article = session.query(Article).filter(Article.article_id == article_id).first()
        if article is None:
            return None
        
        article.content = content
        session.add(article)
        session.commit()
        return article.article_id
    
def delete_by_id(article_id):
    with Session(engine) as session:
        article = session.query(Article).filter(Article.article_id == article_id).first()
        if article is None:
            return None
        
        session.delete(article)
        session.commit()
        return article_id